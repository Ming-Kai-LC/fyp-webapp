from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count
from datetime import timedelta
from .models import (
    AuditLog, DataAccessLog, LoginAttempt, DataChange,
    ComplianceReport, SecurityAlert
)
from .forms import ComplianceReportForm, AuditLogFilterForm
from .services import ComplianceReportGenerator, AuditExporter
from .decorators import admin_required


@login_required
@admin_required
def audit_log_list(request):
    """
    Display filterable audit log
    """
    logs = AuditLog.objects.select_related('user').all()

    # Apply filters
    form = AuditLogFilterForm(request.GET)
    if form.is_valid():
        if form.cleaned_data.get('user'):
            logs = logs.filter(user=form.cleaned_data['user'])
        if form.cleaned_data.get('action_type'):
            logs = logs.filter(action_type=form.cleaned_data['action_type'])
        if form.cleaned_data.get('severity'):
            logs = logs.filter(severity=form.cleaned_data['severity'])
        if form.cleaned_data.get('date_from'):
            logs = logs.filter(created_at__gte=form.cleaned_data['date_from'])
        if form.cleaned_data.get('date_to'):
            logs = logs.filter(created_at__lte=form.cleaned_data['date_to'])
        if form.cleaned_data.get('search'):
            search = form.cleaned_data['search']
            logs = logs.filter(
                Q(action_description__icontains=search) |
                Q(username__icontains=search)
            )

    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'form': form,
    }
    return render(request, 'audit/audit_log_list.html', context)


@login_required
@admin_required
def data_access_log_list(request):
    """
    Display patient data access logs (HIPAA compliance)
    """
    logs = DataAccessLog.objects.select_related('accessor', 'patient__user').all()

    # Filter by patient if specified
    patient_id = request.GET.get('patient_id')
    if patient_id:
        logs = logs.filter(patient_id=patient_id)

    # Filter flagged items
    flagged_only = request.GET.get('flagged_only')
    if flagged_only:
        logs = logs.filter(flagged_for_review=True)

    # Date filters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        logs = logs.filter(accessed_at__gte=date_from)
    if date_to:
        logs = logs.filter(accessed_at__lte=date_to)

    context = {
        'logs': logs[:100],  # Limit for performance
        'patient_id': patient_id,
        'flagged_only': flagged_only,
    }
    return render(request, 'audit/data_access_log_list.html', context)


@login_required
@admin_required
def login_attempts_list(request):
    """
    Display login attempts with security analysis
    """
    attempts = LoginAttempt.objects.all()

    # Show only failed attempts if requested
    failed_only = request.GET.get('failed_only')
    if failed_only:
        attempts = attempts.filter(success=False)

    # Show suspicious activity
    suspicious_only = request.GET.get('suspicious_only')
    if suspicious_only:
        attempts = attempts.filter(is_suspicious=True)

    # Recent attempts (last 24 hours)
    recent = request.GET.get('recent')
    if recent:
        yesterday = timezone.now() - timedelta(days=1)
        attempts = attempts.filter(created_at__gte=yesterday)

    # Statistics
    total_attempts = LoginAttempt.objects.count()
    failed_attempts = LoginAttempt.objects.filter(success=False).count()
    suspicious_attempts = LoginAttempt.objects.filter(is_suspicious=True).count()

    # Top failed usernames
    top_failed = LoginAttempt.objects.filter(success=False).values('username').annotate(
        count=Count('id')
    ).order_by('-count')[:10]

    # Top IPs with failed attempts
    top_ips = LoginAttempt.objects.filter(success=False).values('ip_address').annotate(
        count=Count('id')
    ).order_by('-count')[:10]

    context = {
        'attempts': attempts[:100],
        'total_attempts': total_attempts,
        'failed_attempts': failed_attempts,
        'suspicious_attempts': suspicious_attempts,
        'top_failed': top_failed,
        'top_ips': top_ips,
    }
    return render(request, 'audit/login_attempts_list.html', context)


@login_required
@admin_required
def security_alerts_dashboard(request):
    """
    Display security alerts dashboard
    """
    # Unacknowledged alerts
    unacknowledged_alerts = SecurityAlert.objects.filter(acknowledged=False).order_by('-triggered_at')

    # Critical alerts
    critical_alerts = SecurityAlert.objects.filter(severity='critical', acknowledged=False)

    # Recent alerts (last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    recent_alerts = SecurityAlert.objects.filter(triggered_at__gte=week_ago)

    # Alert statistics
    alert_stats = SecurityAlert.objects.values('alert_type').annotate(
        count=Count('id')
    ).order_by('-count')

    context = {
        'unacknowledged_alerts': unacknowledged_alerts,
        'critical_alerts': critical_alerts,
        'recent_alerts': recent_alerts,
        'alert_stats': alert_stats,
    }
    return render(request, 'audit/security_alerts_dashboard.html', context)


@login_required
@admin_required
def acknowledge_alert(request, alert_id):
    """
    Acknowledge a security alert
    """
    alert = get_object_or_404(SecurityAlert, id=alert_id)

    if request.method == 'POST':
        alert.acknowledged = True
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.resolution_notes = request.POST.get('resolution_notes', '')
        alert.save()

        # Log this action
        AuditLog.log(
            user=request.user,
            action_type='other',
            description=f"Acknowledged security alert: {alert.get_alert_type_display()}",
            severity='info'
        )

        messages.success(request, "Alert acknowledged successfully.")
        return redirect('audit:security_alerts_dashboard')

    context = {
        'alert': alert,
    }
    return render(request, 'audit/acknowledge_alert.html', context)


@login_required
@admin_required
def generate_compliance_report(request):
    """
    Generate compliance reports (HIPAA/GDPR)
    """
    if request.method == 'POST':
        form = ComplianceReportForm(request.POST)
        if form.is_valid():
            try:
                generator = ComplianceReportGenerator(
                    report_type=form.cleaned_data['report_type'],
                    start_date=form.cleaned_data['start_date'],
                    end_date=form.cleaned_data['end_date']
                )

                report = generator.generate(generated_by=request.user)

                messages.success(request, "Compliance report generated successfully!")
                return redirect('audit:view_compliance_report', report_id=report.id)

            except Exception as e:
                messages.error(request, f"Error generating report: {str(e)}")

    else:
        form = ComplianceReportForm()

    context = {
        'form': form,
    }
    return render(request, 'audit/generate_compliance_report.html', context)


@login_required
@admin_required
def view_compliance_report(request, report_id):
    """
    View generated compliance report
    """
    report = get_object_or_404(ComplianceReport, id=report_id)

    context = {
        'report': report,
    }
    return render(request, 'audit/view_compliance_report.html', context)


@login_required
@admin_required
def export_audit_logs(request):
    """
    Export audit logs to CSV for external analysis
    """
    # Get filter parameters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    action_type = request.GET.get('action_type')

    # Generate export
    exporter = AuditExporter(
        date_from=date_from,
        date_to=date_to,
        action_type=action_type
    )

    csv_file = exporter.export_to_csv()

    # Serve file
    response = HttpResponse(csv_file.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="audit_logs_{timezone.now().strftime("%Y%m%d")}.csv"'
    return response


@login_required
def my_access_history(request):
    """
    Allow users to view their own access history (transparency)
    """
    if not hasattr(request.user, 'profile'):
        messages.error(request, "Profile not found.")
        return redirect('detection:home')

    # Get user's own audit logs
    my_logs = AuditLog.objects.filter(user=request.user).order_by('-created_at')[:100]

    # Get data access logs (if patient)
    my_data_accesses = None
    if request.user.profile.is_patient() and hasattr(request.user, 'patient_info'):
        my_data_accesses = DataAccessLog.objects.filter(
            patient=request.user.patient_info
        ).select_related('accessor').order_by('-accessed_at')[:50]

    context = {
        'my_logs': my_logs,
        'my_data_accesses': my_data_accesses,
    }
    return render(request, 'audit/my_access_history.html', context)


@login_required
@admin_required
def data_change_history(request, content_type_id, object_id):
    """
    View complete change history for a specific object
    """
    from django.contrib.contenttypes.models import ContentType

    content_type = get_object_or_404(ContentType, id=content_type_id)
    changes = DataChange.objects.filter(
        content_type=content_type,
        object_id=object_id
    ).select_related('changed_by').order_by('-changed_at')

    context = {
        'content_type': content_type,
        'object_id': object_id,
        'changes': changes,
    }
    return render(request, 'audit/data_change_history.html', context)
