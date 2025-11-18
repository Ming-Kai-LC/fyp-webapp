# Enhanced Dashboards Module - Detailed Specification

## Module Information
- **Module Name:** dashboards (enhancement to existing app)
- **Priority:** MEDIUM (Phase 2)
- **Estimated Effort:** 1-2 days
- **Dependencies:** detection app, analytics module, all other modules

## Purpose
Improve existing dashboard functionality with comprehensive, role-specific interfaces that integrate all system features in a unified view.

## Features

### Core Features
1. Enhanced Doctor Dashboard with today's schedule
2. Enhanced Patient Dashboard with health timeline
3. Enhanced Admin Dashboard with system health monitoring
4. Quick actions and shortcuts
5. Real-time notifications panel
6. Widget-based customizable layout
7. Recent activities feed

### Advanced Features
8. Drag-and-drop dashboard customization
9. Dashboard presets/templates
10. Export dashboard data
11. Mobile-optimized responsive design
12. Dark mode support

---

## Dashboard Specifications

### Doctor Dashboard Enhancements

**File:** `dashboards/views.py` - `doctor_dashboard()`

**Widgets:**
1. **Today's Schedule** - Upcoming appointments
2. **Pending Validations** - Predictions awaiting doctor review
3. **Recent Predictions** - Last 10 predictions with quick actions
4. **Patient Search** - Quick search bar
5. **Statistics Cards** - Today's patients, pending reviews, validation rate
6. **Notifications** - Unread notifications
7. **Quick Actions** - Upload X-ray, Schedule appointment, View reports

**Layout:**
```
┌─────────────────────────────────────────────────────┐
│  Statistics Cards (4 cards in row)                  │
├──────────────────────┬──────────────────────────────┤
│  Today's Schedule    │  Pending Validations         │
│                      │                              │
├──────────────────────┼──────────────────────────────┤
│  Recent Predictions  │  Quick Actions               │
│                      │  + Notifications             │
└──────────────────────┴──────────────────────────────┘
```

---

### Patient Dashboard Enhancements

**File:** `dashboards/views.py` - `patient_dashboard()`

**Widgets:**
1. **Health Summary Card** - COVID risk score, vaccination status
2. **Test Results Timeline** - All X-ray results chronologically
3. **Upcoming Appointments** - Next appointments
4. **Medical Documents** - Recent uploads
5. **Health Trends** - Chart showing test results over time
6. **Notifications** - Important alerts
7. **Quick Actions** - Book appointment, Upload document, View history

**Layout:**
```
┌─────────────────────────────────────────────────────┐
│  Health Summary Card (COVID Risk, Vaccination)      │
├──────────────────────┬──────────────────────────────┤
│  Test Results        │  Upcoming Appointments       │
│  Timeline            │  + Medical Documents         │
├──────────────────────┼──────────────────────────────┤
│  Health Trends Chart │  Quick Actions               │
│                      │  + Notifications             │
└──────────────────────┴──────────────────────────────┘
```

---

### Admin Dashboard Enhancements

**File:** `dashboards/views.py` - `admin_dashboard()`

**Widgets:**
1. **System Health Monitoring** - Server status, database, ML models
2. **User Statistics** - Total users, active sessions, new registrations
3. **Hospital Statistics** - Total predictions, COVID cases, trends
4. **Recent Activities** - Audit log feed
5. **Security Alerts** - Unacknowledged security alerts
6. **Compliance Status** - Data retention, backup status
7. **Model Performance** - ML model accuracy and uptime
8. **Quick Actions** - Generate report, View audit logs, Manage users

**Layout:**
```
┌─────────────────────────────────────────────────────┐
│  System Health (Server, DB, ML Models)              │
├─────────────┬─────────────┬─────────────────────────┤
│  User Stats │ Hospital    │  Model Performance      │
│             │ Stats       │                         │
├─────────────┴─────────────┼─────────────────────────┤
│  Recent Activities         │  Security Alerts        │
│                            │  + Compliance Status    │
└────────────────────────────┴─────────────────────────┘
```

---

## Database Models

### File: `dashboards/models.py`

```python
from django.db import models
from django.conf import settings


class DashboardPreference(models.Model):
    """
    Store user dashboard customization preferences
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dashboard_preferences'
    )

    # Layout preferences
    widget_layout = models.JSONField(
        default=dict,
        help_text="Widget positions and sizes"
    )
    theme = models.CharField(
        max_length=20,
        choices=[('light', 'Light'), ('dark', 'Dark')],
        default='light'
    )

    # Widget visibility
    visible_widgets = models.JSONField(
        default=list,
        help_text="List of visible widget IDs"
    )

    # Refresh settings
    auto_refresh = models.BooleanField(default=True)
    refresh_interval = models.IntegerField(
        default=60,
        help_text="Auto-refresh interval in seconds"
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Dashboard Preferences"


class DashboardWidget(models.Model):
    """
    Define available dashboard widgets
    """
    WIDGET_TYPES = (
        ('statistics', 'Statistics Card'),
        ('chart', 'Chart/Graph'),
        ('table', 'Data Table'),
        ('list', 'List View'),
        ('calendar', 'Calendar'),
        ('notifications', 'Notifications'),
        ('quick_actions', 'Quick Actions'),
        ('custom', 'Custom Widget'),
    )

    widget_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)

    # Access control
    available_for_roles = models.JSONField(
        default=list,
        help_text="List of roles that can see this widget"
    )

    # Default settings
    default_size = models.CharField(
        max_length=20,
        choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')],
        default='medium'
    )
    default_position = models.IntegerField(default=0)

    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['default_position']

    def __str__(self):
        return self.name
```

---

## Views

### File: `dashboards/views.py`

```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from detection.models import Prediction, Patient, XRayImage
from appointments.models import Appointment
from notifications.models import Notification
from audit.models import SecurityAlert


@login_required
def enhanced_doctor_dashboard(request):
    """
    Enhanced doctor dashboard with all widgets
    """
    # Today's appointments
    today = timezone.now().date()
    todays_appointments = Appointment.objects.filter(
        doctor=request.user,
        appointment_date=today,
        status__in=['scheduled', 'confirmed']
    ).order_by('appointment_time')[:5]

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

    pending_count = pending_validations.count()

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
        'unread_notifications': unread_notifications,
    }

    return render(request, 'dashboards/doctor_dashboard_enhanced.html', context)


@login_required
def enhanced_patient_dashboard(request):
    """
    Enhanced patient dashboard with health timeline
    """
    if not hasattr(request.user, 'patient'):
        # Redirect to create patient profile
        return redirect('detection:patient_profile')

    patient = request.user.patient

    # Test results timeline
    predictions = Prediction.objects.filter(
        xray__patient=patient
    ).order_by('-xray__upload_date')[:10]

    # Upcoming appointments
    upcoming_appointments = Appointment.objects.filter(
        patient=patient,
        appointment_date__gte=timezone.now().date(),
        status__in=['scheduled', 'confirmed']
    ).order_by('appointment_date', 'appointment_time')[:5]

    # COVID risk score (if medical_records module exists)
    risk_score = None
    # from medical_records.models import COVIDRiskScore
    # risk_score = COVIDRiskScore.objects.filter(patient=patient).first()

    # Health trends data (for chart)
    trend_data = {
        'dates': [p.xray.upload_date.strftime('%Y-%m-%d') for p in predictions],
        'diagnoses': [p.final_diagnosis for p in predictions],
        'confidences': [p.consensus_confidence for p in predictions],
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
    }

    return render(request, 'dashboards/patient_dashboard_enhanced.html', context)


@login_required
def enhanced_admin_dashboard(request):
    """
    Enhanced admin dashboard with system monitoring
    """
    if not request.user.profile.is_admin():
        return redirect('detection:home')

    # System health
    from django.db import connection
    db_healthy = connection.ensure_connection() is None

    # User statistics
    from django.contrib.auth.models import User
    total_users = User.objects.count()
    new_users_today = User.objects.filter(
        date_joined__date=timezone.now().date()
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
    from audit.models import AuditLog
    recent_activities = AuditLog.objects.select_related('user').order_by('-timestamp')[:10]

    # Model performance (simplified)
    avg_inference_time = Prediction.objects.aggregate(
        avg_time=models.Avg('inference_time')
    )['avg_time'] or 0

    context = {
        'db_healthy': db_healthy,
        'total_users': total_users,
        'new_users_today': new_users_today,
        'total_predictions': total_predictions,
        'covid_cases': covid_cases,
        'today_predictions': today_predictions,
        'unacknowledged_alerts': unacknowledged_alerts,
        'recent_activities': recent_activities,
        'avg_inference_time': avg_inference_time,
    }

    return render(request, 'dashboards/admin_dashboard_enhanced.html', context)
```

---

## URL Configuration

### File: `dashboards/urls.py`

```python
from django.urls import path
from . import views

app_name = 'dashboards'

urlpatterns = [
    # Enhanced dashboards
    path('doctor/', views.enhanced_doctor_dashboard, name='doctor'),
    path('patient/', views.enhanced_patient_dashboard, name='patient'),
    path('admin/', views.enhanced_admin_dashboard, name='admin'),

    # Widget management
    path('preferences/', views.dashboard_preferences, name='preferences'),
    path('widgets/toggle/', views.toggle_widget, name='toggle_widget'),
]
```

---

## Templates Structure

1. `dashboards/doctor_dashboard_enhanced.html`
2. `dashboards/patient_dashboard_enhanced.html`
3. `dashboards/admin_dashboard_enhanced.html`
4. `dashboards/widgets/` - Individual widget templates

---

## Integration Points

- Replace or enhance existing dashboard views in detection app
- Link to all modules (appointments, analytics, medical records, etc.)
- Use AJAX for real-time updates
- Integrate with notifications module for alerts

---

## Success Criteria

- ✅ Role-specific dashboards show relevant information
- ✅ Real-time updates without page refresh
- ✅ Mobile-responsive design
- ✅ Quick actions streamline common tasks
- ✅ Customizable widget layout
- ✅ Dark mode support
