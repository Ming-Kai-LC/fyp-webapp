# Audit & Compliance Module - Detailed Specification

## Module Information
- **Module Name:** audit
- **Priority:** CRITICAL (Phase 1)
- **Estimated Effort:** 2-3 days
- **Dependencies:** All modules (cross-cutting concern)

## Purpose
Track all system activities for medical compliance, data protection regulations (HIPAA/GDPR), and legal documentation. Ensure complete auditability of all user actions and data access.

## Features

### Core Features
1. Comprehensive audit trail for all user actions
2. Data access logging (who viewed what patient data, when)
3. Change tracking for all medical records
4. Login/logout tracking with IP addresses
5. Failed login attempt monitoring
6. Data export logs
7. Report generation logs
8. Admin action tracking

### Advanced Features
9. Compliance report generation
10. Data retention policy enforcement
11. Automated compliance alerts
12. Data anonymization for research
13. Right to be forgotten (GDPR)
14. Audit log export for regulatory bodies
15. Real-time security alerts
16. Suspicious activity detection

---

## Database Models

### File: `audit/models.py`

```python
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
import json


class AuditLog(models.Model):
    """
    Comprehensive audit trail for all system activities
    """
    ACTION_TYPES = (
        ('create', 'Create'),
        ('read', 'Read/View'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('login_failed', 'Failed Login'),
        ('export', 'Data Export'),
        ('report', 'Report Generation'),
        ('upload', 'File Upload'),
        ('download', 'File Download'),
        ('permission_change', 'Permission Change'),
        ('password_change', 'Password Change'),
        ('other', 'Other'),
    )

    SEVERITY_LEVELS = (
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    )

    # Who
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    username = models.CharField(max_length=150, blank=True)  # Store username even if user deleted

    # What
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    action_description = models.CharField(max_length=500)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='info')

    # When
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    # Where (network info)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_key = models.CharField(max_length=40, blank=True)

    # Context (what was affected)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Details
    old_value = models.JSONField(null=True, blank=True, help_text="Previous state before change")
    new_value = models.JSONField(null=True, blank=True, help_text="New state after change")
    additional_data = models.JSONField(null=True, blank=True, help_text="Extra context data")

    # Status
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action_type', '-timestamp']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f"{self.username or 'Anonymous'} - {self.action_type} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    @classmethod
    def log(cls, user, action_type, description, **kwargs):
        """
        Convenience method to create audit log entries
        """
        return cls.objects.create(
            user=user,
            username=user.username if user and user.is_authenticated else 'Anonymous',
            action_type=action_type,
            action_description=description,
            **kwargs
        )


class DataAccessLog(models.Model):
    """
    Specific tracking for patient data access (HIPAA compliance)
    """
    ACCESS_TYPES = (
        ('view', 'View'),
        ('download', 'Download'),
        ('export', 'Export'),
        ('print', 'Print'),
        ('share', 'Share'),
    )

    # Who accessed
    accessor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='data_accesses'
    )
    accessor_role = models.CharField(max_length=20)  # doctor, admin, patient

    # What was accessed
    patient = models.ForeignKey(
        'detection.Patient',
        on_delete=models.CASCADE,
        related_name='access_logs'
    )
    data_type = models.CharField(max_length=50)  # 'prediction', 'xray', 'medical_history', etc.
    data_id = models.PositiveIntegerField()

    # How
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPES)
    access_reason = models.TextField(blank=True, help_text="Purpose of access")

    # When
    accessed_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # Where
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    # Context
    is_legitimate = models.BooleanField(
        default=True,
        help_text="Whether access was for legitimate medical purpose"
    )
    flagged_for_review = models.BooleanField(default=False)
    review_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-accessed_at']
        indexes = [
            models.Index(fields=['patient', '-accessed_at']),
            models.Index(fields=['accessor', '-accessed_at']),
            models.Index(fields=['flagged_for_review']),
        ]

    def __str__(self):
        return f"{self.accessor.username if self.accessor else 'Unknown'} accessed {self.patient.user.get_full_name()}'s {self.data_type}"


class LoginAttempt(models.Model):
    """
    Track all login attempts for security monitoring
    """
    username = models.CharField(max_length=150, db_index=True)
    success = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    failure_reason = models.CharField(max_length=200, blank=True)

    # Security flags
    is_suspicious = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['username', '-timestamp']),
            models.Index(fields=['ip_address', '-timestamp']),
            models.Index(fields=['is_suspicious']),
        ]

    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{self.username} - {status} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


class DataChange(models.Model):
    """
    Track changes to critical medical data with full history
    """
    # What was changed
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Who changed it
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='data_changes'
    )

    # When
    changed_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # Details
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)

    # Context
    change_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id', '-changed_at']),
        ]

    def __str__(self):
        return f"{self.field_name} changed by {self.changed_by.username if self.changed_by else 'System'}"


class ComplianceReport(models.Model):
    """
    Generated compliance reports for regulatory review
    """
    REPORT_TYPES = (
        ('hipaa_audit', 'HIPAA Audit Report'),
        ('gdpr_compliance', 'GDPR Compliance Report'),
        ('access_review', 'Data Access Review'),
        ('security_audit', 'Security Audit'),
        ('user_activity', 'User Activity Report'),
    )

    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    generated_at = models.DateTimeField(auto_now_add=True)

    # Date range for report
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    # Report data
    summary = models.JSONField(help_text="Summary statistics")
    details = models.JSONField(help_text="Detailed findings")

    # Files
    pdf_file = models.FileField(upload_to='compliance_reports/%Y/%m/', null=True, blank=True)

    class Meta:
        ordering = ['-generated_at']

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.generated_at.strftime('%Y-%m-%d')}"


class DataRetentionPolicy(models.Model):
    """
    Define and enforce data retention policies
    """
    data_type = models.CharField(max_length=100, unique=True)
    retention_days = models.IntegerField(help_text="Number of days to retain data")
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Enforcement
    auto_delete = models.BooleanField(
        default=False,
        help_text="Automatically delete data after retention period"
    )
    notify_before_days = models.IntegerField(
        default=30,
        help_text="Notify admins N days before deletion"
    )

    class Meta:
        verbose_name_plural = "Data Retention Policies"

    def __str__(self):
        return f"{self.data_type} - {self.retention_days} days"


class SecurityAlert(models.Model):
    """
    Real-time security alerts for suspicious activities
    """
    ALERT_TYPES = (
        ('failed_login', 'Multiple Failed Logins'),
        ('unusual_access', 'Unusual Data Access Pattern'),
        ('bulk_export', 'Bulk Data Export'),
        ('privilege_escalation', 'Privilege Escalation Attempt'),
        ('after_hours', 'After Hours Access'),
        ('other', 'Other'),
    )

    ALERT_SEVERITY = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )

    alert_type = models.CharField(max_length=50, choices=ALERT_TYPES)
    severity = models.CharField(max_length=10, choices=ALERT_SEVERITY)
    description = models.TextField()
    triggered_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # Related user
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='security_alerts'
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    # Resolution
    acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_alerts'
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)

    # Actions taken
    auto_blocked = models.BooleanField(default=False)
    admin_notified = models.BooleanField(default=False)

    class Meta:
        ordering = ['-triggered_at']
        indexes = [
            models.Index(fields=['acknowledged', '-triggered_at']),
            models.Index(fields=['severity', '-triggered_at']),
        ]

    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.severity} - {self.triggered_at.strftime('%Y-%m-%d %H:%M')}"
```

---

## Views

### File: `audit/views.py`

```python
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
            logs = logs.filter(timestamp__gte=form.cleaned_data['date_from'])
        if form.cleaned_data.get('date_to'):
            logs = logs.filter(timestamp__lte=form.cleaned_data['date_to'])
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
        attempts = attempts.filter(timestamp__gte=yesterday)

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
    my_logs = AuditLog.objects.filter(user=request.user).order_by('-timestamp')[:100]

    # Get data access logs (if patient)
    my_data_accesses = None
    if request.user.profile.is_patient() and hasattr(request.user, 'patient'):
        my_data_accesses = DataAccessLog.objects.filter(
            patient=request.user.patient
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
```

---

## Forms

### File: `audit/forms.py`

```python
from django import forms
from django.contrib.auth.models import User
from .models import ComplianceReport, AuditLog
from datetime import datetime, timedelta
from django.utils import timezone


class AuditLogFilterForm(forms.Form):
    """
    Filter form for audit log list
    """
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        label="User",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    action_type = forms.ChoiceField(
        choices=[('', 'All Actions')] + list(AuditLog.ACTION_TYPES),
        required=False,
        label="Action Type",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    severity = forms.ChoiceField(
        choices=[('', 'All Severities')] + list(AuditLog.SEVERITY_LEVELS),
        required=False,
        label="Severity",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    date_from = forms.DateTimeField(
        required=False,
        label="From Date",
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )

    date_to = forms.DateTimeField(
        required=False,
        label="To Date",
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )

    search = forms.CharField(
        required=False,
        label="Search",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search in description or username...'
        })
    )


class ComplianceReportForm(forms.Form):
    """
    Form for generating compliance reports
    """
    report_type = forms.ChoiceField(
        choices=ComplianceReport.REPORT_TYPES,
        required=True,
        label="Report Type",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    start_date = forms.DateTimeField(
        required=True,
        label="Start Date",
        initial=lambda: timezone.now() - timedelta(days=30),
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )

    end_date = forms.DateTimeField(
        required=True,
        label="End Date",
        initial=timezone.now,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date >= end_date:
                raise forms.ValidationError("End date must be after start date.")

        return cleaned_data
```

---

## Services

### File: `audit/services.py`

```python
from django.utils import timezone
from django.db.models import Count, Q
from .models import (
    AuditLog, DataAccessLog, LoginAttempt, ComplianceReport, SecurityAlert
)
from detection.models import Prediction, Patient
from io import BytesIO
import csv


class ComplianceReportGenerator:
    """
    Generate compliance reports for regulatory review
    """
    def __init__(self, report_type, start_date, end_date):
        self.report_type = report_type
        self.start_date = start_date
        self.end_date = end_date

    def generate(self, generated_by):
        """
        Generate compliance report based on type
        """
        if self.report_type == 'hipaa_audit':
            summary, details = self._generate_hipaa_audit()
        elif self.report_type == 'gdpr_compliance':
            summary, details = self._generate_gdpr_compliance()
        elif self.report_type == 'access_review':
            summary, details = self._generate_access_review()
        elif self.report_type == 'security_audit':
            summary, details = self._generate_security_audit()
        elif self.report_type == 'user_activity':
            summary, details = self._generate_user_activity()
        else:
            summary, details = {}, {}

        # Create report
        report = ComplianceReport.objects.create(
            report_type=self.report_type,
            generated_by=generated_by,
            start_date=self.start_date,
            end_date=self.end_date,
            summary=summary,
            details=details
        )

        return report

    def _generate_hipaa_audit(self):
        """
        Generate HIPAA compliance audit report
        """
        # Patient data access logs
        access_logs = DataAccessLog.objects.filter(
            accessed_at__range=[self.start_date, self.end_date]
        )

        # Summary statistics
        summary = {
            'total_access_events': access_logs.count(),
            'unique_patients_accessed': access_logs.values('patient').distinct().count(),
            'unique_accessors': access_logs.values('accessor').distinct().count(),
            'flagged_accesses': access_logs.filter(flagged_for_review=True).count(),
            'access_by_type': dict(access_logs.values('access_type').annotate(count=Count('id')).values_list('access_type', 'count')),
        }

        # Detailed findings
        details = {
            'flagged_accesses': list(
                access_logs.filter(flagged_for_review=True).values(
                    'accessor__username',
                    'patient__user__username',
                    'data_type',
                    'accessed_at',
                    'access_reason'
                )
            ),
            'high_volume_accessors': list(
                access_logs.values('accessor__username').annotate(
                    count=Count('id')
                ).filter(count__gte=50).order_by('-count')
            ),
        }

        return summary, details

    def _generate_gdpr_compliance(self):
        """
        Generate GDPR compliance report
        """
        audit_logs = AuditLog.objects.filter(
            timestamp__range=[self.start_date, self.end_date]
        )

        summary = {
            'data_access_requests': audit_logs.filter(action_type='read').count(),
            'data_exports': audit_logs.filter(action_type='export').count(),
            'data_deletions': audit_logs.filter(action_type='delete').count(),
            'consent_changes': 0,  # Implement when consent module is added
        }

        details = {
            'export_requests': list(
                audit_logs.filter(action_type='export').values(
                    'username', 'action_description', 'timestamp'
                )
            ),
            'deletion_requests': list(
                audit_logs.filter(action_type='delete').values(
                    'username', 'action_description', 'timestamp'
                )
            ),
        }

        return summary, details

    def _generate_access_review(self):
        """
        Generate data access review report
        """
        access_logs = DataAccessLog.objects.filter(
            accessed_at__range=[self.start_date, self.end_date]
        )

        summary = {
            'total_accesses': access_logs.count(),
            'by_role': dict(access_logs.values('accessor_role').annotate(count=Count('id')).values_list('accessor_role', 'count')),
            'by_data_type': dict(access_logs.values('data_type').annotate(count=Count('id')).values_list('data_type', 'count')),
        }

        details = {
            'top_accessors': list(
                access_logs.values('accessor__username', 'accessor_role').annotate(
                    count=Count('id')
                ).order_by('-count')[:20]
            ),
            'most_accessed_patients': list(
                access_logs.values('patient__user__username').annotate(
                    count=Count('id')
                ).order_by('-count')[:20]
            ),
        }

        return summary, details

    def _generate_security_audit(self):
        """
        Generate security audit report
        """
        login_attempts = LoginAttempt.objects.filter(
            timestamp__range=[self.start_date, self.end_date]
        )

        security_alerts = SecurityAlert.objects.filter(
            triggered_at__range=[self.start_date, self.end_date]
        )

        summary = {
            'total_login_attempts': login_attempts.count(),
            'failed_logins': login_attempts.filter(success=False).count(),
            'suspicious_logins': login_attempts.filter(is_suspicious=True).count(),
            'security_alerts': security_alerts.count(),
            'critical_alerts': security_alerts.filter(severity='critical').count(),
        }

        details = {
            'failed_login_trends': list(
                login_attempts.filter(success=False).values('username').annotate(
                    count=Count('id')
                ).order_by('-count')[:10]
            ),
            'alert_breakdown': list(
                security_alerts.values('alert_type', 'severity').annotate(
                    count=Count('id')
                ).order_by('-count')
            ),
        }

        return summary, details

    def _generate_user_activity(self):
        """
        Generate user activity report
        """
        audit_logs = AuditLog.objects.filter(
            timestamp__range=[self.start_date, self.end_date]
        )

        summary = {
            'total_actions': audit_logs.count(),
            'unique_users': audit_logs.values('user').distinct().count(),
            'by_action_type': dict(audit_logs.values('action_type').annotate(count=Count('id')).values_list('action_type', 'count')),
        }

        details = {
            'most_active_users': list(
                audit_logs.values('username').annotate(
                    count=Count('id')
                ).order_by('-count')[:20]
            ),
            'action_timeline': list(
                audit_logs.values('timestamp__date', 'action_type').annotate(
                    count=Count('id')
                ).order_by('timestamp__date')
            ),
        }

        return summary, details


class AuditExporter:
    """
    Export audit logs to CSV
    """
    def __init__(self, date_from=None, date_to=None, action_type=None):
        self.date_from = date_from
        self.date_to = date_to
        self.action_type = action_type

    def export_to_csv(self):
        """
        Export filtered audit logs to CSV
        """
        logs = AuditLog.objects.all()

        if self.date_from:
            logs = logs.filter(timestamp__gte=self.date_from)
        if self.date_to:
            logs = logs.filter(timestamp__lte=self.date_to)
        if self.action_type:
            logs = logs.filter(action_type=self.action_type)

        # Create CSV
        csv_buffer = BytesIO()
        writer = csv.writer(csv_buffer)

        # Headers
        writer.writerow([
            'Timestamp', 'Username', 'Action Type', 'Description',
            'Severity', 'IP Address', 'Success', 'Error Message'
        ])

        # Data
        for log in logs:
            writer.writerow([
                log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                log.username,
                log.action_type,
                log.action_description,
                log.severity,
                log.ip_address or 'N/A',
                'Yes' if log.success else 'No',
                log.error_message or 'N/A'
            ])

        csv_buffer.seek(0)
        return csv_buffer


class SecurityMonitor:
    """
    Monitor for suspicious activities and trigger alerts
    """
    @staticmethod
    def check_failed_login_attempts(username, ip_address):
        """
        Check for multiple failed login attempts
        """
        from datetime import timedelta

        # Check last hour
        one_hour_ago = timezone.now() - timedelta(hours=1)
        failed_attempts = LoginAttempt.objects.filter(
            username=username,
            success=False,
            timestamp__gte=one_hour_ago
        ).count()

        if failed_attempts >= 5:
            SecurityAlert.objects.create(
                alert_type='failed_login',
                severity='high',
                description=f"Multiple failed login attempts for user {username} from IP {ip_address}",
                ip_address=ip_address,
                auto_blocked=True,
                admin_notified=True
            )
            return True

        return False

    @staticmethod
    def check_unusual_access_pattern(accessor, patient):
        """
        Detect unusual data access patterns
        """
        # Check if accessor has accessed this patient before
        previous_accesses = DataAccessLog.objects.filter(
            accessor=accessor,
            patient=patient
        ).count()

        # Check if accessing many different patients in short time
        from datetime import timedelta
        last_hour = timezone.now() - timedelta(hours=1)
        recent_unique_patients = DataAccessLog.objects.filter(
            accessor=accessor,
            accessed_at__gte=last_hour
        ).values('patient').distinct().count()

        if recent_unique_patients >= 20:  # Accessing 20+ patients in 1 hour
            SecurityAlert.objects.create(
                alert_type='unusual_access',
                severity='medium',
                description=f"User {accessor.username} accessed {recent_unique_patients} different patient records in the last hour",
                user=accessor,
                admin_notified=True
            )
```

---

## Middleware

### File: `audit/middleware.py`

```python
from django.utils.deprecation import MiddlewareMixin
from .models import AuditLog


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware to automatically log certain requests
    """
    def process_request(self, request):
        # Store request start time for performance tracking
        import time
        request._audit_start_time = time.time()

    def process_response(self, request, response):
        # Log certain actions automatically
        if request.user.is_authenticated:
            # Log file downloads
            if 'download' in request.path and response.status_code == 200:
                AuditLog.log(
                    user=request.user,
                    action_type='download',
                    description=f"Downloaded file: {request.path}",
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    severity='info'
                )

        return response

    @staticmethod
    def get_client_ip(request):
        """
        Get client IP address from request
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
```

---

## Signals

### File: `audit/signals.py`

```python
from django.db.models.signals import post_save, post_delete, pre_save
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import AuditLog, LoginAttempt, DataChange
from detection.models import Prediction, Patient, XRayImage


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    Log successful user login
    """
    AuditLog.log(
        user=user,
        action_type='login',
        description=f"User logged in successfully",
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        severity='info'
    )

    LoginAttempt.objects.create(
        username=user.username,
        success=True,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """
    Log user logout
    """
    if user:
        AuditLog.log(
            user=user,
            action_type='logout',
            description=f"User logged out",
            ip_address=get_client_ip(request),
            severity='info'
        )


@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    """
    Log failed login attempt
    """
    username = credentials.get('username', 'Unknown')
    ip_address = get_client_ip(request)

    AuditLog.log(
        user=None,
        action_type='login_failed',
        description=f"Failed login attempt for username: {username}",
        ip_address=ip_address,
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        severity='warning'
    )

    LoginAttempt.objects.create(
        username=username,
        success=False,
        ip_address=ip_address,
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        failure_reason='Invalid credentials'
    )

    # Check for suspicious activity
    from .services import SecurityMonitor
    SecurityMonitor.check_failed_login_attempts(username, ip_address)


@receiver(pre_save)
def track_model_changes(sender, instance, **kwargs):
    """
    Track changes to critical models
    """
    # Only track specific models
    tracked_models = [Prediction, Patient]

    if sender not in tracked_models:
        return

    # Only for updates (not creates)
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            content_type = ContentType.objects.get_for_model(sender)

            # Compare fields
            for field in instance._meta.fields:
                field_name = field.name
                old_value = getattr(old_instance, field_name, None)
                new_value = getattr(instance, field_name, None)

                if old_value != new_value:
                    DataChange.objects.create(
                        content_type=content_type,
                        object_id=instance.pk,
                        changed_by=getattr(instance, '_changed_by', None),
                        field_name=field_name,
                        old_value=str(old_value),
                        new_value=str(new_value)
                    )

        except sender.DoesNotExist:
            pass


def get_client_ip(request):
    """
    Get client IP address from request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
```

---

## URL Configuration

### File: `audit/urls.py`

```python
from django.urls import path
from . import views

app_name = 'audit'

urlpatterns = [
    # Audit logs
    path('logs/', views.audit_log_list, name='audit_log_list'),
    path('data-access/', views.data_access_log_list, name='data_access_log_list'),
    path('login-attempts/', views.login_attempts_list, name='login_attempts_list'),

    # Security alerts
    path('security/alerts/', views.security_alerts_dashboard, name='security_alerts_dashboard'),
    path('security/alert/<int:alert_id>/acknowledge/', views.acknowledge_alert, name='acknowledge_alert'),

    # Compliance reports
    path('compliance/generate/', views.generate_compliance_report, name='generate_compliance_report'),
    path('compliance/view/<int:report_id>/', views.view_compliance_report, name='view_compliance_report'),

    # Export
    path('export/csv/', views.export_audit_logs, name='export_audit_logs'),

    # User access
    path('my-history/', views.my_access_history, name='my_access_history'),
    path('changes/<int:content_type_id>/<int:object_id>/', views.data_change_history, name='data_change_history'),
]
```

---

## Admin Configuration

### File: `audit/admin.py`

```python
from django.contrib import admin
from .models import (
    AuditLog, DataAccessLog, LoginAttempt, DataChange,
    ComplianceReport, DataRetentionPolicy, SecurityAlert
)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'username', 'action_type', 'action_description', 'severity', 'success']
    list_filter = ['action_type', 'severity', 'success', 'timestamp']
    search_fields = ['username', 'action_description', 'ip_address']
    readonly_fields = ['timestamp', 'user', 'username']
    date_hierarchy = 'timestamp'


@admin.register(DataAccessLog)
class DataAccessLogAdmin(admin.ModelAdmin):
    list_display = ['accessed_at', 'accessor', 'patient', 'data_type', 'access_type', 'flagged_for_review']
    list_filter = ['access_type', 'flagged_for_review', 'accessed_at']
    search_fields = ['accessor__username', 'patient__user__username']
    readonly_fields = ['accessed_at']
    date_hierarchy = 'accessed_at'


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'username', 'success', 'ip_address', 'is_suspicious']
    list_filter = ['success', 'is_suspicious', 'timestamp']
    search_fields = ['username', 'ip_address']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'


@admin.register(SecurityAlert)
class SecurityAlertAdmin(admin.ModelAdmin):
    list_display = ['triggered_at', 'alert_type', 'severity', 'acknowledged', 'user']
    list_filter = ['alert_type', 'severity', 'acknowledged', 'triggered_at']
    readonly_fields = ['triggered_at']
    date_hierarchy = 'triggered_at'


@admin.register(ComplianceReport)
class ComplianceReportAdmin(admin.ModelAdmin):
    list_display = ['generated_at', 'report_type', 'generated_by', 'start_date', 'end_date']
    list_filter = ['report_type', 'generated_at']
    readonly_fields = ['generated_at']


@admin.register(DataRetentionPolicy)
class DataRetentionPolicyAdmin(admin.ModelAdmin):
    list_display = ['data_type', 'retention_days', 'is_active', 'auto_delete']
    list_filter = ['is_active', 'auto_delete']


@admin.register(DataChange)
class DataChangeAdmin(admin.ModelAdmin):
    list_display = ['changed_at', 'content_type', 'object_id', 'field_name', 'changed_by']
    list_filter = ['content_type', 'changed_at']
    readonly_fields = ['changed_at']
    date_hierarchy = 'changed_at'
```

---

## Decorators

### File: `audit/decorators.py`

```python
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def admin_required(view_func):
    """
    Decorator to ensure user is an admin
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            messages.error(request, "You don't have permission to access this page.")
            return redirect('detection:home')

        if not request.user.profile.is_admin():
            messages.error(request, "Only administrators can access this page.")
            return redirect('detection:home')

        return view_func(request, *args, **kwargs)

    return wrapper


def log_data_access(data_type):
    """
    Decorator to automatically log patient data access
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Execute the view
            response = view_func(request, *args, **kwargs)

            # Log the access (implement based on your needs)
            # This is a simplified example
            if request.user.is_authenticated and hasattr(request.user, 'profile'):
                from .models import DataAccessLog
                # Extract patient from kwargs if available
                patient_id = kwargs.get('patient_id') or request.GET.get('patient_id')
                if patient_id:
                    try:
                        from detection.models import Patient
                        patient = Patient.objects.get(id=patient_id)
                        DataAccessLog.objects.create(
                            accessor=request.user,
                            accessor_role=request.user.profile.role,
                            patient=patient,
                            data_type=data_type,
                            data_id=patient_id,
                            access_type='view',
                            ip_address=get_client_ip(request)
                        )
                    except Patient.DoesNotExist:
                        pass

            return response

        return wrapper
    return decorator


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
```

---

## Integration Points

### 1. Update `config/settings.py`

```python
INSTALLED_APPS = [
    # ... existing apps ...
    'audit',
]

MIDDLEWARE = [
    # ... existing middleware ...
    'audit.middleware.AuditMiddleware',
]
```

### 2. Update `config/urls.py`

```python
urlpatterns = [
    # ... existing patterns ...
    path('audit/', include('audit.urls')),
]
```

### 3. Connect Signals in `audit/apps.py`

```python
from django.apps import AppConfig


class AuditConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'audit'

    def ready(self):
        import audit.signals
```

---

## Testing Requirements

### Unit Tests

1. Test audit log creation
2. Test data access logging
3. Test login attempt tracking
4. Test security alert triggers
5. Test compliance report generation
6. Test data change tracking

---

## Migration Steps

1. Create Django app
2. Run migrations
3. Connect signals
4. Add middleware
5. Create default retention policies via admin

---

## Success Criteria

- ✅ All user actions are logged
- ✅ Patient data access is tracked (HIPAA)
- ✅ Failed logins trigger security alerts
- ✅ Compliance reports can be generated
- ✅ Change history is available for critical data
- ✅ Users can view their own access history
