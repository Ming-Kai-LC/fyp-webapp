# Module Dependencies and Integration Points

This document maps dependencies and integration points between all modules in the COVID-19 Detection webapp to facilitate parallel development and prevent conflicts.

---

## Module Dependency Graph

```
┌─────────────────────────────────────────────────────────────┐
│                     detection (CORE)                         │
│              (Existing - All modules depend on this)         │
└────────────────┬───────────────────────────┬─────────────────┘
                 │                           │
    ┌────────────┴────────────┬──────────────┴──────────────┐
    │                         │                             │
    v                         v                             v
┌────────────┐        ┌──────────────┐            ┌─────────────────┐
│   audit    │◄───────│   reporting  │            │ medical_records │
│ (Phase 1)  │        │  (Phase 1)   │            │   (Phase 1)     │
└────────────┘        └──────┬───────┘            └─────────────────┘
    ▲                        │                             ▲
    │                        │                             │
    │                        v                             │
    │              ┌──────────────────┐                    │
    │              │  notifications   │◄───────────────────┤
    │              │    (Phase 1)     │                    │
    │              └────────┬─────────┘                    │
    │                       │                              │
    │                       │                              │
    │                       v                              │
    │              ┌──────────────────┐                    │
    │              │  appointments    │                    │
    │              │    (Phase 2)     │                    │
    │              └──────────────────┘                    │
    │                                                      │
    │              ┌──────────────────┐                    │
    └──────────────┤   analytics      │◄───────────────────┤
                   │    (Phase 2)     │                    │
                   └────────┬─────────┘                    │
                            │                              │
                            v                              │
                   ┌──────────────────┐                    │
                   │   dashboards     │◄───────────────────┘
                   │    (Phase 2)     │◄───────────────────┐
                   └────────┬─────────┘                    │
                            │                              │
                            │        ┌────────────────────┐│
                            └────────►      api           ││
                                     │    (Phase 3)       ││
                                     └────────────────────┘│
                                              ▲            │
                                              └────────────┘
                                     (Provides API to all modules)
```

---

## Module Dependency Matrix

| Module | Depends On | Used By | Can Develop In Parallel With |
|--------|-----------|---------|------------------------------|
| **detection** (existing) | - | All modules | - |
| **reporting** | detection | notifications, dashboards, api | audit, medical_records, notifications |
| **audit** | detection | All modules (cross-cutting) | reporting, medical_records, notifications |
| **medical_records** | detection, audit | dashboards, analytics, api | reporting, audit, notifications |
| **notifications** | detection, reporting (soft) | appointments, dashboards, api | audit, medical_records |
| **appointments** | detection, notifications | dashboards, analytics, api | analytics |
| **analytics** | detection, All modules (soft) | dashboards, api | appointments |
| **dashboards** | All modules | api | - (should be last in Phase 2) |
| **api** | All modules | - | - (should be last in Phase 3) |

**Legend:**
- **Hard dependency:** Cannot function without
- **Soft dependency:** Can function with basic integration, enhanced with full integration

---

## Detailed Integration Points

### 1. detection (CORE) - Existing Module

**Provides to all modules:**
- `User`, `UserProfile` models for authentication
- `Patient` model for patient data
- `XRayImage` model for X-ray uploads
- `Prediction` model for AI predictions

**Integration points:**
- All modules import from `detection.models`
- All modules use existing authentication system
- All modules can extend `Patient` with additional related models

---

### 2. reporting → detection

**Dependencies:**
```python
from detection.models import Prediction, Patient, XRayImage
```

**Integration points:**
- Report generation for `Prediction` instances
- Access patient information from `Patient` model
- Display X-ray images in reports

**Data flow:**
- User requests report for prediction → Reporting module generates PDF

**Coordination needed:**
- Add "Generate Report" button in `detection/results.html`
- Link from prediction detail view

---

### 3. audit (Cross-cutting concern)

**Dependencies:**
```python
from detection.models import Patient, Prediction, XRayImage
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
```

**Integration points:**
- Logs all user actions across all modules
- Middleware automatically logs requests
- Signals track model changes
- Data access logging for patient records

**Used by:**
- All modules should trigger audit logs for important actions
- Compliance reports pull from all module activities

**Coordination needed:**
```python
# In any view that accesses patient data
from audit.models import AuditLog, DataAccessLog

AuditLog.log(
    user=request.user,
    action_type='read',
    description=f"Viewed patient {patient_id}"
)
```

---

### 4. medical_records → detection, audit

**Dependencies:**
```python
from detection.models import Patient
from audit.models import AuditLog  # For access tracking
```

**Integration points:**
- Extends `Patient` with medical history
- One-to-many relationships: Patient → MedicalConditions, Allergies, etc.
- Foreign keys to Patient model

**Data flow:**
- Patient profile page shows medical records
- Risk score calculation uses patient demographics + medical history

**Coordination needed:**
- Add "Medical Records" tab in patient dashboard
- Link from patient detail view
- Show COVID risk score in prediction results

---

### 5. notifications → detection, reporting

**Dependencies:**
```python
from detection.models import Prediction, Patient
from reporting.models import Report  # Soft dependency
```

**Integration points:**
- Sends notifications when predictions are ready
- Sends notifications when reports are generated
- Sends appointment reminders (once appointments module exists)

**Trigger points:**
```python
# In detection/views.py after prediction created
from notifications.services import NotificationService
NotificationService.send_prediction_notification(prediction)

# In reporting/views.py after report generated
NotificationService.send_notification(
    user=patient_user,
    template_type='report_ready',
    context_data={...}
)
```

**Coordination needed:**
- Call notification service from other modules
- Create notification templates for each event type

---

### 6. appointments → detection, notifications

**Dependencies:**
```python
from detection.models import Patient
from notifications.services import NotificationService
```

**Integration points:**
- Appointments linked to Patient
- Doctor-patient scheduling
- Sends reminders via notifications module

**Data flow:**
- Patient books appointment → Appointment created → Reminder scheduled → Notification sent

**Coordination needed:**
- Add "Book Appointment" button in patient dashboard
- Add appointment calendar in doctor dashboard
- Set up Celery for scheduled reminders

---

### 7. analytics → ALL modules (soft dependencies)

**Dependencies:**
```python
from detection.models import Prediction, Patient, XRayImage
from appointments.models import Appointment  # Soft
from medical_records.models import MedicalCondition  # Soft
from audit.models import AuditLog  # Soft
```

**Integration points:**
- Aggregates data from all modules for analysis
- Generates statistics and trends
- Can function with just detection data initially
- Enhanced with data from other modules

**Data flow:**
- Daily cron job → Generate analytics snapshot → Store metrics
- User requests analytics → Query all modules → Generate charts

**Coordination needed:**
- Can start with detection data only
- Add additional metrics as other modules complete

---

### 8. dashboards → ALL modules

**Dependencies:**
```python
from detection.models import Prediction, Patient
from appointments.models import Appointment
from notifications.models import Notification
from medical_records.models import COVIDRiskScore
from analytics.models import AnalyticsSnapshot
from audit.models import AuditLog, SecurityAlert
from reporting.models import Report
```

**Integration points:**
- Aggregates widgets from all modules
- Doctor dashboard shows appointments, pending validations, analytics
- Patient dashboard shows medical records, upcoming appointments, test results
- Admin dashboard shows audit logs, security alerts, analytics

**Why last in Phase 2:**
- Needs all other modules to be complete for full functionality
- Can be developed incrementally as modules complete

**Coordination needed:**
- Each module can provide widget templates
- Dashboards module integrates them

---

### 9. api → ALL modules (Provides API to everything)

**Dependencies:**
```python
from detection.models import *
from appointments.models import *
from medical_records.models import *
from notifications.models import *
from reporting.models import *
from analytics.models import *
```

**Integration points:**
- Creates serializers for all models
- Provides REST endpoints for all CRUD operations
- JWT authentication for mobile apps
- Swagger documentation for all APIs

**Why last in Phase 3:**
- Should provide API to complete, tested functionality
- Easier to create API for finished features

**Coordination needed:**
- Each module should have clean, tested views before API wrapping

---

## Database Foreign Key Relationships

### Core Relationships

```python
# Existing (detection app)
UserProfile ──► User (OneToOne)
Patient ──► User (OneToOne)
XRayImage ──► Patient (ForeignKey)
XRayImage ──► User (uploaded_by, ForeignKey)
Prediction ──► XRayImage (OneToOne)
Prediction ──► User (reviewed_by, ForeignKey, nullable)

# New relationships

# reporting
Report ──► Prediction (ForeignKey)
Report ──► Patient (ForeignKey)
Report ──► User (generated_by, ForeignKey)
Report ──► ReportTemplate (ForeignKey)

# audit
AuditLog ──► User (ForeignKey, nullable)
DataAccessLog ──► User (accessor, ForeignKey)
DataAccessLog ──► Patient (ForeignKey)
LoginAttempt (no FK, just username tracking)
SecurityAlert ──► User (ForeignKey, nullable)

# medical_records
MedicalCondition ──► Patient (ForeignKey)
Allergy ──► Patient (ForeignKey)
Medication ──► Patient (ForeignKey)
Vaccination ──► Patient (ForeignKey)
Surgery ──► Patient (ForeignKey)
FamilyHistory ──► Patient (ForeignKey)
MedicalDocument ──► Patient (ForeignKey)
LifestyleInformation ──► Patient (OneToOne)
COVIDRiskScore ──► Patient (ForeignKey)

# notifications
Notification ──► User (recipient, ForeignKey)
Notification ──► Prediction (ForeignKey, nullable)
NotificationPreference ──► User (OneToOne)

# appointments
Appointment ──► Patient (ForeignKey)
Appointment ──► User (doctor, ForeignKey)
DoctorSchedule ──► User (doctor, ForeignKey)
Waitlist ──► Patient (ForeignKey)
Waitlist ──► User (doctor, ForeignKey)

# analytics
AnalyticsSnapshot (no FK, aggregated data)
ModelPerformanceMetric (no FK, aggregated data)
CustomReport ──► User (created_by, ForeignKey)
DataExport ──► User (exported_by, ForeignKey)

# dashboards
DashboardPreference ──► User (OneToOne)
```

---

## Settings Configuration Integration

### Order of adding to INSTALLED_APPS

```python
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps (install as needed per module)
    'crispy_forms',
    'crispy_bootstrap5',
    'rest_framework',                    # For api module
    'rest_framework_simplejwt',          # For api module
    'drf_yasg',                          # For api module
    'corsheaders',                       # For api module

    # Project apps (ORDER MATTERS!)
    'detection',              # CORE - must be first
    'audit',                  # Phase 1 - cross-cutting
    'reporting',              # Phase 1
    'medical_records',        # Phase 1
    'notifications',          # Phase 1
    'appointments',           # Phase 2
    'analytics',              # Phase 2
    'dashboards',             # Phase 2
    'api',                    # Phase 3
]
```

### Middleware Integration

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Static files
    'corsheaders.middleware.CorsMiddleware',       # API CORS (add for api module)
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'audit.middleware.AuditMiddleware',            # Add for audit module
]
```

---

## URL Configuration Integration

### config/urls.py

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('detection.urls')),           # Existing
    path('reporting/', include('reporting.urls')),  # Phase 1
    path('audit/', include('audit.urls')),          # Phase 1
    path('medical-records/', include('medical_records.urls')),  # Phase 1
    path('notifications/', include('notifications.urls')),      # Phase 1
    path('appointments/', include('appointments.urls')),        # Phase 2
    path('analytics/', include('analytics.urls')),              # Phase 2
    path('dashboards/', include('dashboards.urls')),            # Phase 2
    path('api/v1/', include('api.urls')),                       # Phase 3

    # API documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0)),
]
```

---

## Template Integration Points

### Base Template Extension

All modules should extend `templates/base.html`:

```html
{% extends 'base.html' %}
{% block content %}
  <!-- Module-specific content -->
{% endblock %}
```

### Navbar Integration

Add links to `templates/base.html` navbar:

```html
<!-- For doctors -->
{% if user.profile.is_doctor %}
  <a href="{% url 'appointments:doctor_appointments' %}">My Appointments</a>
  <a href="{% url 'analytics:dashboard' %}">Analytics</a>
  <a href="{% url 'reporting:report_list' %}">Reports</a>
{% endif %}

<!-- For patients -->
{% if user.profile.is_patient %}
  <a href="{% url 'appointments:my_appointments' %}">My Appointments</a>
  <a href="{% url 'medical_records:summary' patient.id %}">Medical Records</a>
  <a href="{% url 'notifications:notification_list' %}">Notifications</a>
{% endif %}

<!-- For admins -->
{% if user.profile.is_admin %}
  <a href="{% url 'audit:audit_log_list' %}">Audit Logs</a>
  <a href="{% url 'analytics:dashboard' %}">Analytics</a>
  <a href="{% url 'audit:security_alerts_dashboard' %}">Security</a>
{% endif %}
```

---

## Signals Integration

### Module Signals to Connect

```python
# audit/signals.py connects to:
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models.signals import post_save, pre_save

# appointments/signals.py (if needed)
from django.db.models.signals import post_save
from appointments.models import Appointment

@receiver(post_save, sender=Appointment)
def send_appointment_notification(sender, instance, created, **kwargs):
    if created:
        from notifications.services import NotificationService
        NotificationService.send_notification(...)
```

---

## API Integration Examples

### Calling Notifications from Other Modules

```python
# In reporting/views.py after report generation
from notifications.services import NotificationService

NotificationService.send_notification(
    user=patient_user,
    template_type='report_ready',
    context_data={
        'patient_name': patient_user.get_full_name(),
        'report_id': report.report_id,
        'action_url': f'/reporting/view/{report.report_id}/',
    },
    priority='normal'
)
```

### Logging Audit Events from Other Modules

```python
# In medical_records/views.py when viewing patient records
from audit.models import AuditLog, DataAccessLog

# General audit log
AuditLog.log(
    user=request.user,
    action_type='read',
    description=f"Viewed medical records for patient {patient.id}"
)

# Specific data access log (HIPAA)
DataAccessLog.objects.create(
    accessor=request.user,
    accessor_role=request.user.profile.role,
    patient=patient,
    data_type='medical_records',
    data_id=patient.id,
    access_type='view',
    ip_address=get_client_ip(request)
)
```

---

## Testing Integration Points

### Cross-Module Integration Tests

```python
# tests/integration/test_report_notification.py
def test_report_generation_sends_notification():
    """Test that generating a report triggers a notification"""
    # Create prediction
    prediction = create_test_prediction()

    # Generate report
    from reporting.services import ReportGenerator
    report = ReportGenerator(prediction, template).generate(user)

    # Check notification was created
    from notifications.models import Notification
    notification = Notification.objects.filter(
        related_prediction=prediction,
        recipient=prediction.xray.patient.user
    ).first()

    assert notification is not None
    assert notification.status == 'sent'
```

---

## Migration Coordination

### Migration Naming Convention

```
reporting/migrations/
  0001_initial.py
  0002_add_qr_code_field.py

audit/migrations/
  0001_initial.py
  0002_add_security_alerts.py
```

### Handling Foreign Key Conflicts

If two modules both add ForeignKey to the same model:

1. Create migrations in separate branches
2. When merging, Django will detect dependency
3. Adjust migration dependencies manually if needed:

```python
# In migration file
class Migration(migrations.Migration):
    dependencies = [
        ('detection', '0001_initial'),
        ('audit', '0001_initial'),  # Add if needed
    ]
```

---

## Deployment Coordination

### Order of Deployment

1. Run all migrations together:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. Create default data (in order):
   ```bash
   # Notification templates
   python manage.py loaddata notifications/fixtures/templates.json

   # Report templates
   python manage.py loaddata reporting/fixtures/templates.json

   # Dashboard widgets
   python manage.py loaddata dashboards/fixtures/widgets.json
   ```

3. Collect static files:
   ```bash
   python manage.py collectstatic --noinput
   ```

4. Start background workers (if using Celery):
   ```bash
   celery -A config worker --loglevel=info
   celery -A config beat --loglevel=info
   ```

---

## Summary

### Can Develop in Parallel (Phase 1):
- ✅ reporting
- ✅ audit
- ✅ medical_records
- ✅ notifications

### Must Wait For Dependencies (Phase 2):
- ⚠️ appointments (wait for notifications)
- ⚠️ analytics (can start anytime, enhanced as modules complete)
- ⚠️ dashboards (wait for all Phase 1 & 2)

### Must Be Last (Phase 3):
- ⚠️ api (wait for all modules to be complete)

---

## Questions or Issues?

If integration points are unclear:
1. Check the specific module specification in `specs/`
2. Review existing code in `detection/` app
3. Check Django documentation for best practices
4. Coordinate with other session developers
