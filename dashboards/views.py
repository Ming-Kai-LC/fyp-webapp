# dashboards/views.py
"""
Enhanced Dashboards Module - Views
Role-specific dashboards with comprehensive widgets
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Avg
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import timedelta
from detection.models import Prediction, Patient, XRayImage
from appointments.models import Appointment
from notifications.models import Notification
from audit.models import SecurityAlert, AuditLog
from .models import DashboardPreference, DashboardWidget


@login_required
def enhanced_staff_dashboard(request):
    """
    Enhanced staff dashboard with all widgets
    """
    # Today's appointments
    today = timezone.now().date()
    todays_appointments = Appointment.objects.filter(
        doctor=request.user,
        appointment_date=today,
        status__in=['scheduled', 'confirmed']
    ).select_related('patient__user').order_by('appointment_time')[:5]

    # Pending validations
    pending_validations = Prediction.objects.filter(
        is_validated=False
    ).select_related('xray__patient__user').order_by('-xray__upload_date')[:10]

    # Recent predictions
    recent_predictions = Prediction.objects.select_related(
        'xray__patient__user'
    ).order_by('-xray__upload_date')[:10]

    # Statistics
    total_today = Prediction.objects.filter(
        xray__upload_date__date=today
    ).count()

    pending_count = Prediction.objects.filter(is_validated=False).count()

    # Validation rate
    total_predictions = Prediction.objects.count()
    validated_predictions = Prediction.objects.filter(is_validated=True).count()
    validation_rate = (validated_predictions / total_predictions * 100) if total_predictions > 0 else 0

    # Unread notifications
    unread_notifications = Notification.objects.filter(
        recipient=request.user,
        status='sent',
        read_at__isnull=True
    ).order_by('-created_at')[:5]

    context = {
        'todays_appointments': todays_appointments,
        'pending_validations': pending_validations,
        'recent_predictions': recent_predictions,
        'total_today': total_today,
        'pending_count': pending_count,
        'validation_rate': validation_rate,
        'unread_notifications': unread_notifications,
        'dashboard_type': 'staff',
    }

    return render(request, 'dashboards/staff_dashboard_enhanced.html', context)


@login_required
def enhanced_patient_dashboard(request):
    """
    Enhanced patient dashboard with health timeline
    """
    if not hasattr(request.user, 'patient_info'):
        # Redirect to create patient profile
        return redirect('detection:home')

    patient = request.user.patient_info

    # Test results timeline
    predictions = Prediction.objects.filter(
        xray__patient=patient
    ).select_related('xray').order_by('-xray__upload_date')[:10]

    # Upcoming appointments
    upcoming_appointments = Appointment.objects.filter(
        patient=patient,
        appointment_date__gte=timezone.now().date(),
        status__in=['scheduled', 'confirmed']
    ).select_related('doctor__profile').order_by('appointment_date', 'appointment_time')[:5]

    # COVID risk score (placeholder for future medical_records module)
    risk_score = None

    # Health trends data (for chart)
    trend_data = {
        'dates': [p.xray.upload_date.strftime('%Y-%m-%d') for p in predictions],
        'diagnoses': [p.final_diagnosis for p in predictions],
        'confidences': [float(p.consensus_confidence) for p in predictions],
    }

    # Unread notifications
    unread_notifications = Notification.objects.filter(
        recipient=request.user,
        status='sent',
        read_at__isnull=True
    ).order_by('-created_at')[:5]

    context = {
        'patient': patient,
        'predictions': predictions,
        'upcoming_appointments': upcoming_appointments,
        'risk_score': risk_score,
        'trend_data': trend_data,
        'unread_notifications': unread_notifications,
        'dashboard_type': 'patient',
    }

    return render(request, 'dashboards/patient_dashboard_enhanced.html', context)


@login_required
def enhanced_admin_dashboard(request):
    """
    Enhanced admin dashboard with system monitoring
    """
    if not hasattr(request.user, 'profile') or not request.user.profile.is_admin():
        return redirect('detection:home')

    # System health
    from django.db import connection
    try:
        connection.ensure_connection()
        db_healthy = True
    except Exception:
        db_healthy = False

    # User statistics
    from django.contrib.auth.models import User
    total_users = User.objects.count()
    new_users_today = User.objects.filter(
        date_joined__date=timezone.now().date()
    ).count()

    # Active sessions (users who logged in within last 24 hours)
    active_sessions = User.objects.filter(
        last_login__gte=timezone.now() - timedelta(hours=24)
    ).count()

    # Hospital statistics
    total_predictions = Prediction.objects.count()
    covid_cases = Prediction.objects.filter(final_diagnosis='COVID').count()
    today_predictions = Prediction.objects.filter(
        xray__upload_date__date=timezone.now().date()
    ).count()

    # Security alerts
    unacknowledged_alerts = SecurityAlert.objects.filter(
        acknowledged=False
    ).order_by('-triggered_at')[:5]

    # Recent activities
    recent_activities = AuditLog.objects.select_related('user').order_by('-created_at')[:10]

    # Model performance (simplified)
    avg_inference_time = Prediction.objects.aggregate(
        avg_time=Avg('inference_time')
    )['avg_time'] or 0

    # Model accuracy (validated predictions)
    validated_count = Prediction.objects.filter(is_validated=True).count()
    model_uptime = 100.0  # Placeholder - would need actual monitoring

    context = {
        'db_healthy': db_healthy,
        'total_users': total_users,
        'new_users_today': new_users_today,
        'active_sessions': active_sessions,
        'total_predictions': total_predictions,
        'covid_cases': covid_cases,
        'today_predictions': today_predictions,
        'unacknowledged_alerts': unacknowledged_alerts,
        'recent_activities': recent_activities,
        'avg_inference_time': avg_inference_time,
        'validated_count': validated_count,
        'model_uptime': model_uptime,
        'dashboard_type': 'admin',
    }

    return render(request, 'dashboards/admin_dashboard_enhanced.html', context)


@login_required
def dashboard_preferences(request):
    """
    Manage user dashboard preferences
    """
    preference, created = DashboardPreference.objects.get_or_create(
        user=request.user
    )

    if request.method == 'POST':
        # Update preferences
        preference.theme = request.POST.get('theme', 'light')
        preference.auto_refresh = request.POST.get('auto_refresh') == 'on'
        preference.refresh_interval = int(request.POST.get('refresh_interval', 60))
        preference.save()

        return redirect('dashboards:preferences')

    context = {
        'preference': preference,
    }

    return render(request, 'dashboards/preferences.html', context)


@login_required
@require_POST
def toggle_widget(request):
    """
    Toggle widget visibility via AJAX
    """
    widget_id = request.POST.get('widget_id')
    visible = request.POST.get('visible') == 'true'

    preference, created = DashboardPreference.objects.get_or_create(
        user=request.user
    )

    visible_widgets = preference.visible_widgets or []

    if visible and widget_id not in visible_widgets:
        visible_widgets.append(widget_id)
    elif not visible and widget_id in visible_widgets:
        visible_widgets.remove(widget_id)

    preference.visible_widgets = visible_widgets
    preference.save()

    return JsonResponse({'success': True, 'visible': visible})
