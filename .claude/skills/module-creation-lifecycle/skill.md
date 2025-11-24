# Module Creation Lifecycle Orchestration

**Version:** 1.0.0
**Last Updated:** 2025-11-22
**Auto-apply:** YES - Automatically triggers when creating new Django modules

---

## Purpose

This skill orchestrates the complete end-to-end lifecycle for creating a new Django module/app, from initial planning through testing and integration. It ensures Claude Code follows a systematic, high-quality process without requiring user reminders at each step.

---

## When This Skill Auto-Triggers

Claude Code should **automatically apply this skill** when:
- User requests "create a new module/app"
- User asks to "add a new feature" that requires a new Django app
- User says "implement [feature name]" where feature name suggests new module
- Detects phrases: "new module", "create app", "add feature", "build system for"
- User mentions creating something that doesn't fit in existing modules

**Examples:**
- "Create a patient appointment scheduling module"
- "Add a notification system"
- "Build a medical records management feature"
- "I need a new app for analytics"

---

## Foundation Files - MUST USE

**CRITICAL:** The following foundation files MUST be used in all modules to ensure consistency, reusability, and DRY principles:

### 1. Abstract Base Models (`common/models.py`)
**ALWAYS inherit from these:**
- `TimeStampedModel` - Auto-adds `created_at` and `updated_at` (USE FOR ALL MODELS)
- `SoftDeleteModel` - Adds soft delete with `is_deleted`, `deleted_at`, `deleted_by`
- `AuditableModel` - Adds `created_by` and `updated_by` tracking
- `FullAuditModel` - Combines all above (timestamps + audit + soft delete)
- `ActiveManager` - Excludes soft-deleted records from querysets

**Example:**
```python
from common.models import TimeStampedModel, SoftDeleteModel

class Appointment(TimeStampedModel):  # ✅ Correct
    # Auto gets created_at, updated_at
    pass

class Appointment(models.Model):  # ❌ Wrong - missing base model
    pass
```

### 2. Bootstrap Widget Library (`common/widgets.py`)
**ALWAYS use these instead of hardcoded attrs:**
- `BootstrapTextInput` - Text input with form-control class
- `BootstrapEmailInput` - Email input with validation
- `BootstrapPasswordInput` - Password input
- `BootstrapTextarea` - Textarea with form-control
- `BootstrapSelect` - Select dropdown with form-select
- `BootstrapCheckboxInput` - Bootstrap checkbox
- `BootstrapRadioSelect` - Bootstrap radio buttons
- `BootstrapDateInput` - Date picker
- `BootstrapDateTimeInput` - DateTime picker
- `BootstrapFileInput` - File upload input

**Example:**
```python
from common.widgets import BootstrapTextInput, BootstrapSelect

widgets = {
    'name': BootstrapTextInput(),  # ✅ Correct
    'status': BootstrapSelect(choices=STATUS_CHOICES),  # ✅ Correct
}

widgets = {
    'name': forms.TextInput(attrs={'class': 'form-control'}),  # ❌ Wrong - hardcoded
}
```

### 3. Template Tags & Filters (`common/templatetags/common_tags.py`)
**ALWAYS use these for consistent UI:**
- `{% status_badge status %}` - Render status badges
- `{% diagnosis_badge diagnosis %}` - Render diagnosis badges
- `{% format_datetime datetime %}` - Format datetime
- `{% format_date date %}` - Format date
- `{% time_since datetime %}` - Human-readable time (e.g., "2 hours ago")
- `{% render_pagination page_obj %}` - Render pagination component

**Example:**
```django
{% load common_tags %}

<td>{% status_badge appointment.status %}</td>  {# ✅ Correct #}
<td>{% format_datetime appointment.scheduled_date %}</td>  {# ✅ Correct #}

{% render_pagination page_obj %}  {# ✅ Correct #}
```

### 4. Reusable Template Components (`templates/components/`)
**ALWAYS include these instead of duplicating HTML:**
- `card.html` - Bootstrap card component
- `alert.html` - Alert/notification component
- `loading_spinner.html` - Loading spinner
- `pagination.html` - Pagination (use via `{% render_pagination %}`)

**Example:**
```django
{% include 'components/card.html' with title="Appointments" %}  {# ✅ Correct #}
{% include 'components/alert.html' with message="Success!" type="success" %}  {# ✅ Correct #}
```

### 5. Common Utilities (`common/utils.py`)
**ALWAYS use these for validation and formatting:**
- `validate_phone(phone)` - Validate Malaysian phone numbers
- `validate_image_file(file, max_size_mb)` - Validate image uploads
- `validate_nric(nric)` - Validate Malaysian NRIC
- `sanitize_filename(filename)` - Sanitize file names
- `generate_unique_filename(filename, prefix)` - Generate unique file names
- `format_file_size(size_bytes)` - Format bytes to human-readable
- `calculate_age(date_of_birth)` - Calculate age from DOB
- `time_since(dt)` - Human-readable time difference

**Example:**
```python
from common.utils import validate_phone, validate_image_file

if not validate_phone(phone):  # ✅ Correct
    raise ValidationError("Invalid phone number")
```

### 6. UI/UX Design System (`UI_UX_DESIGN_SYSTEM.md`)
**ALWAYS reference this for:**
- Color palette (primary, secondary, semantic colors)
- Typography scale and font families
- Spacing system (Bootstrap utilities)
- Component patterns and usage
- Accessibility guidelines (WCAG 2.1 AA)
- Responsive breakpoints

**Before creating any UI component, consult this document first!**

---

## Complete Lifecycle Phases

### Phase 1: Planning & Design (BEFORE CODE)

**Objective:** Fully understand requirements and design the module structure before writing any code.

**Auto-actions Claude Code should take:**

1. **Create Planning Todo List**
   ```
   - Define module purpose and scope
   - List all models and their relationships
   - Define API endpoints needed
   - Identify user role permissions required
   - Plan URL structure and routing
   ```

2. **Ask Clarifying Questions** (use AskUserQuestion tool)
   - What is the primary purpose of this module? (1-2 sentences)
   - Which user roles can access this module? (admin/staff/patient)
   - What models/data structures are needed?
   - Are API endpoints required?
   - Are there external integrations? (email, SMS, third-party APIs)
   - What's the main user workflow?

3. **Design Models & Relationships**
   - List all models needed
   - Define relationships (ForeignKey, ManyToMany, OneToOne)
   - Identify fields for each model
   - Determine which abstract base models to inherit from:
     - `TimeStampedModel` (created_at, updated_at) - USE FOR ALL MODELS
     - `SoftDeleteModel` (soft delete functionality)
     - `AuditableModel` (created_by, updated_by tracking)

4. **Design API Endpoints** (if API needed)
   - List all endpoints (GET, POST, PUT, DELETE)
   - Define URL patterns
   - Identify serializer fields
   - Plan permission classes for each endpoint

5. **Plan Permission Requirements**
   - Admin-only features?
   - Staff-accessible features?
   - Patient self-service features?
   - Object-level permissions needed? (e.g., patients view own records only)
   - Reference: `user-role-permissions` skill

6. **Plan Service Layer** (if complex business logic)
   - Identify complex workflows that need services
   - Define service class names (e.g., `AppointmentService`, `NotificationService`)
   - List service methods
   - Reference: `three-tier-architecture` skill for when to use services

**Validation Gate:** Do NOT proceed to Phase 2 until:
- ✅ All clarifying questions answered
- ✅ Models and relationships documented
- ✅ API endpoints listed (if applicable)
- ✅ Permissions identified
- ✅ Service layer planned (if complex logic)
- ✅ User confirms plan looks good

**Output:** Create a planning document in todo list or present to user for approval.

---

### Phase 2: Code Generation (STRICT ORDER)

**Objective:** Generate code files in the correct dependency order to avoid errors and maintain consistency.

**CRITICAL RULE:** Follow this exact order. Do NOT skip steps. Do NOT change order.

#### Step 1: Create Django App

```bash
venv/Scripts/python.exe manage.py startapp <module_name>
```

**Naming conventions:**
- Use snake_case: `appointment_scheduling`, `medical_records`, `notifications`
- Plural names for multi-entity modules: `appointments`, `analytics`
- Singular for single-entity: `audit`, `reporting`

#### Step 2: Create Folder Structure

Create this exact structure:

```
<module_name>/
├── services/
│   └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_services.py
│   ├── test_forms.py
│   └── test_api.py           # if API module
├── templates/<module_name>/
│   ├── base.html              # if complex templates
│   └── ...
├── static/<module_name>/
│   ├── css/
│   ├── js/
│   └── img/
├── migrations/
│   └── __init__.py
├── __init__.py
├── apps.py
├── models.py
├── constants.py               # ALWAYS CREATE
├── admin.py
├── forms.py
├── views.py
├── urls.py
└── serializers.py             # if API module
```

**Reference:** `standard-folder-structure` skill

#### Step 3: Create models.py

**MUST follow these rules:**

1. **Import abstract base models:**
   ```python
   from django.db import models
   from django.contrib.auth.models import User
   from common.models import TimeStampedModel, SoftDeleteModel, ActiveManager
   ```

2. **Every model inherits from abstract base:**
   ```python
   class Appointment(TimeStampedModel):
       # Auto gets: created_at, updated_at from TimeStampedModel
       patient = models.ForeignKey(
           'detection.Patient',
           on_delete=models.CASCADE,
           related_name='appointments'
       )
       # ... other fields

       class Meta:
           ordering = ['-created_at']
           verbose_name = 'Appointment'
           verbose_name_plural = 'Appointments'
           indexes = [
               models.Index(fields=['patient', 'scheduled_date']),
           ]
   ```

3. **Required for each model:**
   - Type hints on all methods
   - Comprehensive docstrings
   - `__str__()` method
   - Appropriate `related_name` on ForeignKeys
   - Explicit `on_delete` behavior
   - Indexes on frequently filtered fields
   - `Meta` class with ordering

4. **Custom managers/querysets** (if needed):
   ```python
   class AppointmentQuerySet(models.QuerySet):
       def upcoming(self):
           return self.filter(scheduled_date__gte=timezone.now())

       def for_patient(self, patient):
           return self.filter(patient=patient)

   class AppointmentManager(models.Manager):
       def get_queryset(self):
           return AppointmentQuerySet(self.model, using=self._db)

       def upcoming(self):
           return self.get_queryset().upcoming()
   ```

**Reference:** `django-module-creation` skill, `performance-optimization` skill

#### Step 4: Create constants.py

**ALWAYS CREATE THIS FILE.** No exceptions.

```python
"""
Constants for <module_name> module.
Centralizes all magic strings, choices, and configuration values.
"""

class AppointmentStatus:
    """Status choices for appointments."""
    SCHEDULED = 'scheduled'
    CONFIRMED = 'confirmed'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'
    NO_SHOW = 'no_show'

    CHOICES = [
        (SCHEDULED, 'Scheduled'),
        (CONFIRMED, 'Confirmed'),
        (CANCELLED, 'Cancelled'),
        (COMPLETED, 'Completed'),
        (NO_SHOW, 'No Show'),
    ]

    @classmethod
    def get_display(cls, status: str) -> str:
        """Get display name for status."""
        return dict(cls.CHOICES).get(status, status)


class AppointmentType:
    """Type choices for appointments."""
    CONSULTATION = 'consultation'
    FOLLOW_UP = 'follow_up'
    EMERGENCY = 'emergency'

    CHOICES = [
        (CONSULTATION, 'Consultation'),
        (FOLLOW_UP, 'Follow-up'),
        (EMERGENCY, 'Emergency'),
    ]


# Configuration constants
DEFAULT_APPOINTMENT_DURATION = 30  # minutes
MAX_APPOINTMENTS_PER_DAY = 20
CANCELLATION_DEADLINE_HOURS = 24

# Email templates
EMAIL_CONFIRMATION_SUBJECT = "Appointment Confirmation - {date}"
EMAIL_REMINDER_SUBJECT = "Appointment Reminder - Tomorrow at {time}"

# Error messages
ERROR_APPOINTMENT_CONFLICT = "This time slot is already booked."
ERROR_OUTSIDE_HOURS = "Appointments must be scheduled during business hours (9 AM - 5 PM)."
ERROR_PAST_DATE = "Cannot schedule appointment in the past."
```

**Reference:** `full-stack-django-patterns` skill (Section 1: Constants Management)

#### Step 5: Create and Run Migrations

```bash
venv/Scripts/python.exe manage.py makemigrations <module_name>
venv/Scripts/python.exe manage.py migrate
```

**Verify:**
- Migration file created in `<module_name>/migrations/`
- Migration runs without errors
- Check database schema created correctly

#### Step 6: Create admin.py

```python
from django.contrib import admin
from .models import Appointment
from .constants import AppointmentStatus


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'scheduled_date', 'status', 'created_at')
    list_filter = ('status', 'scheduled_date', 'created_at')
    search_fields = ('patient__user__username', 'patient__user__email')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'scheduled_date'

    fieldsets = (
        ('Appointment Details', {
            'fields': ('patient', 'scheduled_date', 'appointment_type', 'status')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_delete_permission(self, request, obj=None):
        """Only admins can delete appointments."""
        return request.user.profile.is_admin()
```

**Reference:** `user-role-permissions` skill for access control in admin

#### Step 7: Create forms.py

**MUST use widget library** (from `common/widgets.py`):

```python
from django import forms
from .models import Appointment
from .constants import AppointmentStatus, AppointmentType
from common.widgets import BootstrapDateTimeInput, BootstrapSelect, BootstrapTextarea


class AppointmentForm(forms.ModelForm):
    """Form for creating/updating appointments."""

    class Meta:
        model = Appointment
        fields = ['patient', 'scheduled_date', 'appointment_type', 'notes']
        widgets = {
            'scheduled_date': BootstrapDateTimeInput(),
            'appointment_type': BootstrapSelect(choices=AppointmentType.CHOICES),
            'notes': BootstrapTextarea(attrs={
                'rows': 3,
                'placeholder': 'Additional notes...'
            }),
        }

    def clean_scheduled_date(self):
        """Validate scheduled date is in the future and during business hours."""
        from django.utils import timezone

        scheduled_date = self.cleaned_data['scheduled_date']

        # Check if date is in the past
        if scheduled_date < timezone.now():
            from .constants import ERROR_PAST_DATE
            raise forms.ValidationError(ERROR_PAST_DATE)

        # Check business hours (9 AM - 5 PM)
        if not (9 <= scheduled_date.hour < 17):
            from .constants import ERROR_OUTSIDE_HOURS
            raise forms.ValidationError(ERROR_OUTSIDE_HOURS)

        return scheduled_date

    def clean(self):
        """Cross-field validation."""
        cleaned_data = super().clean()
        # Add cross-field validation here if needed
        return cleaned_data
```

**Use common utilities for validation (from `common.utils`):**
- `validate_phone(phone)` - Validate Malaysian phone numbers
- `validate_image_file(file, max_size_mb)` - Validate image uploads
- `validate_nric(nric)` - Validate Malaysian NRIC format
- `sanitize_filename(filename)` - Sanitize file names
- `generate_unique_filename(filename, prefix)` - Generate unique file names

**Example with utilities:**

```python
from common.utils import validate_phone, validate_image_file

class PatientForm(forms.ModelForm):
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not validate_phone(phone):
            raise forms.ValidationError("Invalid Malaysian phone number format.")
        return phone

    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image')
        if image and not validate_image_file(image, max_size_mb=5):
            raise forms.ValidationError("Invalid image file or size exceeds 5MB.")
        return image
```

**Reference:** `full-stack-django-patterns` skill (Section 7: Form & Widget Library), `common/utils.py`

#### Step 8: Create services/ (if complex business logic)

**Only create services for:**
- Multi-step workflows
- Logic shared between web views and API
- External integrations (email, SMS, third-party APIs)
- Complex calculations or data aggregation

**Example:**

```python
# services/appointment_service.py
from typing import Optional, List
from django.db import transaction
from django.core.exceptions import ValidationError
from ..models import Appointment
from ..constants import AppointmentStatus, ERROR_APPOINTMENT_CONFLICT
import logging

logger = logging.getLogger(__name__)


class AppointmentService:
    """Service for appointment business logic."""

    @staticmethod
    def create_appointment(
        patient,
        scheduled_date,
        appointment_type,
        notes: str = "",
        created_by=None
    ) -> Appointment:
        """
        Create a new appointment with validation and notifications.

        Args:
            patient: Patient instance
            scheduled_date: datetime for appointment
            appointment_type: Type of appointment
            notes: Optional notes
            created_by: User creating the appointment

        Returns:
            Created Appointment instance

        Raises:
            ValidationError: If appointment conflicts or invalid
        """
        # Check for conflicts
        if AppointmentService._has_conflict(scheduled_date):
            raise ValidationError(ERROR_APPOINTMENT_CONFLICT)

        # Create appointment
        with transaction.atomic():
            appointment = Appointment.objects.create(
                patient=patient,
                scheduled_date=scheduled_date,
                appointment_type=appointment_type,
                status=AppointmentStatus.SCHEDULED,
                notes=notes
            )

            # Send confirmation email
            AppointmentService._send_confirmation_email(appointment)

            # Log creation
            logger.info(
                f"Appointment created",
                extra={
                    'user_id': created_by.id if created_by else None,
                    'appointment_id': appointment.id,
                    'patient_id': patient.id,
                    'scheduled_date': scheduled_date,
                }
            )

        return appointment

    @staticmethod
    def _has_conflict(scheduled_date) -> bool:
        """Check if time slot is available."""
        from datetime import timedelta

        start = scheduled_date - timedelta(minutes=30)
        end = scheduled_date + timedelta(minutes=30)

        return Appointment.objects.filter(
            scheduled_date__range=(start, end),
            status__in=[AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]
        ).exists()

    @staticmethod
    def _send_confirmation_email(appointment):
        """Send confirmation email to patient."""
        # TODO: Implement email sending
        pass
```

**Reference:** `three-tier-architecture` skill for service patterns

#### Step 9: Create views.py

**MUST be thin controllers.** Business logic goes in services or models.

```python
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from reporting.decorators import staff_required
from django.utils.decorators import method_decorator
from .models import Appointment
from .forms import AppointmentForm
from .services.appointment_service import AppointmentService
from .constants import AppointmentStatus


class AppointmentListView(LoginRequiredMixin, ListView):
    """List all appointments (filtered by user role)."""
    model = Appointment
    template_name = 'appointments/appointment_list.html'
    context_object_name = 'appointments'
    paginate_by = 20

    def get_queryset(self):
        """Filter appointments by user role."""
        user = self.request.user

        if user.profile.is_patient():
            # Patients see only their own appointments
            return Appointment.objects.filter(patient__user=user)

        # Staff and admin see all appointments
        return Appointment.objects.all()


@method_decorator(staff_required, name='dispatch')
class AppointmentCreateView(LoginRequiredMixin, CreateView):
    """Create new appointment (staff only)."""
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/appointment_form.html'
    success_url = reverse_lazy('appointments:list')

    def form_valid(self, form):
        """Create appointment using service layer."""
        try:
            appointment = AppointmentService.create_appointment(
                patient=form.cleaned_data['patient'],
                scheduled_date=form.cleaned_data['scheduled_date'],
                appointment_type=form.cleaned_data['appointment_type'],
                notes=form.cleaned_data.get('notes', ''),
                created_by=self.request.user
            )
            return redirect('appointments:detail', pk=appointment.pk)
        except ValidationError as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)
```

**Reference:** `django-module-creation` skill (Fat Models, Thin Views)

#### Step 10: Create urls.py

```python
from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.AppointmentListView.as_view(), name='list'),
    path('create/', views.AppointmentCreateView.as_view(), name='create'),
    path('<int:pk>/', views.AppointmentDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.AppointmentUpdateView.as_view(), name='edit'),
    path('<int:pk>/cancel/', views.AppointmentCancelView.as_view(), name='cancel'),
]
```

#### Step 11: Create templates/ (if web interface needed)

**MUST use:**
- Bootstrap 5 classes from `UI_UX_DESIGN_SYSTEM.md`
- Reusable template components from `templates/components/`:
  - `{% include 'components/card.html' with title="..." %}` for cards
  - `{% include 'components/alert.html' with message="..." type="success" %}` for alerts
  - `{% include 'components/loading_spinner.html' with text="..." %}` for spinners
  - `{% load common_tags %}{% render_pagination page_obj %}` for pagination
- Template tags from `common.templatetags.common_tags`:
  - `{% status_badge status %}` for status badges
  - `{% diagnosis_badge diagnosis %}` for diagnosis badges
  - `{% format_datetime datetime %}` for date formatting
  - `{% time_since datetime %}` for relative time display
- Consistent design system (colors, typography, spacing)
- Responsive design (mobile-first)
- Accessibility (WCAG 2.1 AA compliance)

**Example template using components:**

```django
{% extends "base.html" %}
{% load common_tags %}

{% block content %}
<div class="container mt-4">
    <h1>Appointments</h1>

    {% if messages %}
        {% for message in messages %}
            {% include 'components/alert.html' with message=message type=message.tags dismissible=True %}
        {% endfor %}
    {% endif %}

    {% include 'components/card.html' with title="Upcoming Appointments" title_icon="calendar" %}
        {% block card_body %}
            <table class="table">
                <thead>
                    <tr>
                        <th>Patient</th>
                        <th>Date</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {% for appointment in appointments %}
                    <tr>
                        <td>{{ appointment.patient }}</td>
                        <td>{% format_datetime appointment.scheduled_date %}</td>
                        <td>{% status_badge appointment.status %}</td>
                    </tr>
                    {% empty %}
                    <tr>
                        <td colspan="3" class="text-center text-muted">No appointments found.</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        {% endblock %}
    {% endinclude %}

    {% render_pagination page_obj %}
</div>
{% endblock %}
```

**Reference:** `ui-ux-consistency` skill, `mobile-responsive` skill, `UI_UX_DESIGN_SYSTEM.md`, `full-stack-django-patterns` skill (Section 8: Template Tag & Filter Library)

#### Step 12: Create serializers.py (if API needed)

```python
from rest_framework import serializers
from .models import Appointment
from .constants import AppointmentStatus, AppointmentType


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for Appointment model."""

    patient_name = serializers.CharField(
        source='patient.user.get_full_name',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    class Meta:
        model = Appointment
        fields = [
            'id',
            'patient',
            'patient_name',
            'scheduled_date',
            'appointment_type',
            'status',
            'status_display',
            'notes',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_scheduled_date(self, value):
        """Validate scheduled date."""
        from django.utils import timezone
        from .constants import ERROR_PAST_DATE

        if value < timezone.now():
            raise serializers.ValidationError(ERROR_PAST_DATE)

        return value
```

**Add to api/views.py:**

```python
from rest_framework import viewsets, permissions
from appointments.models import Appointment
from appointments.serializers import AppointmentSerializer
from api.permissions import IsStaffOrOwner


class AppointmentViewSet(viewsets.ModelViewSet):
    """API ViewSet for appointments."""
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrOwner]

    def get_queryset(self):
        """Filter by user role."""
        user = self.request.user

        if user.profile.is_patient():
            return Appointment.objects.filter(patient__user=user)

        return Appointment.objects.all()
```

---

### Phase 3: Quality Checklist (AUTO-VERIFY)

**Objective:** Ensure every file meets quality standards before proceeding.

Claude Code should **automatically verify** each item:

#### Models Quality Checklist
- [ ] All models inherit from abstract base model (TimeStampedModel)
- [ ] All ForeignKeys have explicit `on_delete` behavior
- [ ] All ForeignKeys have descriptive `related_name`
- [ ] Frequently filtered fields have `db_index=True`
- [ ] All models have `__str__()` method
- [ ] All models have `Meta` class with `ordering`
- [ ] Type hints on all custom methods
- [ ] Comprehensive docstrings on all classes and methods

#### Constants Quality Checklist
- [ ] `constants.py` file created (NO EXCEPTIONS!)
- [ ] All magic strings moved to constants
- [ ] All choices defined as classes with CHOICES attribute
- [ ] Configuration values centralized
- [ ] Error messages centralized
- [ ] No hardcoded strings in models/views/forms

#### Forms Quality Checklist
- [ ] Widget library used (from `common.widgets` - BootstrapTextInput, BootstrapSelect, etc.)
- [ ] No hardcoded `attrs={'class': 'form-control'}` - MUST use widgets from common.widgets
- [ ] Field-level validation in `clean_<field>()` methods
- [ ] Cross-field validation in `clean()` method
- [ ] Error messages from constants.py
- [ ] CSRF protection enabled (default)

#### Views Quality Checklist
- [ ] Views are thin (<50 lines per method)
- [ ] Business logic in services/ or models, not views
- [ ] Permission decorators/mixins applied (`@staff_required`, etc.)
- [ ] QuerySets filtered by user role
- [ ] Type hints on all methods
- [ ] Docstrings on all classes and methods

#### Services Quality Checklist (if created)
- [ ] Services are framework-agnostic (no request/response objects)
- [ ] Type hints on all methods
- [ ] Comprehensive docstrings
- [ ] Structured logging on important actions
- [ ] Transactions for multi-step operations (`@transaction.atomic()`)
- [ ] Custom exceptions raised (not generic Exception)

#### Security Checklist
- [ ] User input validated (forms, serializers)
- [ ] Object-level permissions enforced (patients see own data only)
- [ ] Role-based access control applied (admin/staff/patient)
- [ ] File uploads validated (if applicable)
- [ ] SQL injection prevented (using ORM, no raw queries)
- [ ] XSS prevented (template escaping enabled)
- [ ] CSRF tokens on all forms

**Reference:** `security-best-practices` skill, `user-role-permissions` skill

#### Code Quality Checklist
- [ ] PEP 8 compliant (run `black` and `flake8`)
- [ ] Type hints on all functions/methods
- [ ] Docstrings on all public classes/methods/functions
- [ ] No unused imports or variables
- [ ] Imports sorted (run `isort`)

**Reference:** `code-quality-standards` skill

**Validation Gate:** If ANY checklist item fails, FIX IT before proceeding to Phase 4.

---

### Phase 4: Integration & Validation (FINAL CHECKS)

**Objective:** Integrate the module into the project and verify everything works.

#### Step 1: Update config/settings.py

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... existing apps
    'appointments',  # NEW MODULE
]
```

#### Step 2: Update config/urls.py

Include module URLs:

```python
urlpatterns = [
    # ... existing patterns
    path('appointments/', include('appointments.urls')),  # NEW MODULE
]
```

If API module, update `api/urls.py`:

```python
from appointments.views import AppointmentViewSet

router.register(r'appointments', AppointmentViewSet, basename='appointment')
```

#### Step 3: Run Migrations (if not done earlier)

```bash
venv/Scripts/python.exe manage.py makemigrations
venv/Scripts/python.exe manage.py migrate
```

**Verify:**
- Migrations run without errors
- Database tables created
- Foreign keys properly linked

#### Step 4: Run Tests (CRITICAL!)

```bash
venv/Scripts/python.exe -m pytest appointments/tests/ -v --cov=appointments
```

**Verify:**
- All tests pass
- Coverage ≥ 80%
- No warnings or errors

**NOTE:** If tests don't exist yet, CREATE THEM in Phase 2, Step 13 (see Testing section below).

#### Step 5: Update Documentation

Create or update:
- `appointments/README.md` - Module overview, usage, examples
- Main project `README.md` - Add to modules list
- API documentation (if API module) - Swagger/OpenAPI annotations

#### Step 6: Manual Testing

1. **Admin Panel:**
   - Login to `/admin/`
   - Verify models appear
   - Test creating, editing, deleting via admin

2. **Web Interface:**
   - Test list view
   - Test create view (as staff)
   - Test permissions (try as patient)
   - Test form validation

3. **API (if applicable):**
   - Test all endpoints with different roles
   - Verify permission enforcement
   - Test error responses

#### Step 7: Integration Validation Checklist

- [ ] Module added to `INSTALLED_APPS`
- [ ] URLs included in main `urls.py`
- [ ] Migrations run successfully
- [ ] All tests pass with ≥ 80% coverage
- [ ] Models visible in admin panel
- [ ] Web views accessible and working
- [ ] API endpoints working (if applicable)
- [ ] Permissions enforced correctly (admin/staff/patient)
- [ ] Documentation updated
- [ ] Manual testing completed

**Validation Gate:** If ANY item fails, FIX IT before marking module complete.

---

## Testing Standards (AUTO-CREATE TESTS)

**CRITICAL:** Tests must be created during Phase 2, not as an afterthought.

### When to Create Tests

**After models:** Create `test_models.py`
**After forms:** Create `test_forms.py`
**After views:** Create `test_views.py`
**After services:** Create `test_services.py`
**After API:** Create `test_api.py`

### Test Types Required

1. **Model Tests** (`test_models.py`)
   - Test `__str__()` methods
   - Test custom methods
   - Test model managers/querysets
   - Test model validation
   - Test relationships (ForeignKey, ManyToMany)

2. **Form Tests** (`test_forms.py`)
   - Test valid data
   - Test invalid data
   - Test field validation
   - Test cross-field validation
   - Test error messages

3. **View Tests** (`test_views.py`)
   - Test GET requests
   - Test POST requests
   - Test redirects
   - Test template rendering
   - Test context data

4. **Permission Tests** (`test_views.py`)
   - Test admin access
   - Test staff access
   - Test patient access
   - Test unauthenticated access
   - Test object-level permissions

5. **Service Tests** (`test_services.py`)
   - Test service methods
   - Test error handling
   - Test transactions
   - Mock external dependencies

6. **API Tests** (`test_api.py`)
   - Test all endpoints (GET, POST, PUT, DELETE)
   - Test permissions for each role
   - Test pagination
   - Test filtering
   - Test error responses

### Test Pattern Example

```python
# tests/test_models.py
import pytest
from django.utils import timezone
from appointments.models import Appointment
from appointments.constants import AppointmentStatus
from detection.models import Patient


@pytest.mark.django_db
class TestAppointmentModel:
    """Tests for Appointment model."""

    def test_appointment_str(self, sample_patient):
        """Test __str__ method."""
        appointment = Appointment.objects.create(
            patient=sample_patient,
            scheduled_date=timezone.now(),
            status=AppointmentStatus.SCHEDULED
        )
        assert str(appointment) == f"Appointment for {sample_patient} on {appointment.scheduled_date}"

    def test_upcoming_queryset(self, sample_patient):
        """Test upcoming() queryset method."""
        future_date = timezone.now() + timezone.timedelta(days=1)
        past_date = timezone.now() - timezone.timedelta(days=1)

        future_appt = Appointment.objects.create(
            patient=sample_patient,
            scheduled_date=future_date,
            status=AppointmentStatus.SCHEDULED
        )
        past_appt = Appointment.objects.create(
            patient=sample_patient,
            scheduled_date=past_date,
            status=AppointmentStatus.COMPLETED
        )

        upcoming = Appointment.objects.upcoming()
        assert future_appt in upcoming
        assert past_appt not in upcoming
```

**Reference:** `testing-automation` skill (will be created next)

### Coverage Requirements

- **Minimum:** 80% overall coverage
- **Models:** 90%+ coverage
- **Services:** 85%+ coverage
- **Views:** 80%+ coverage
- **Forms:** 85%+ coverage

Run coverage report:
```bash
venv/Scripts/python.exe -m pytest --cov=appointments --cov-report=html
```

---

## Integration with Existing Skills

This skill **automatically references and applies** these existing skills:

1. **`user-role-permissions`** - For all permission checks in views, APIs, admin
2. **`three-tier-architecture`** - For service layer decisions
3. **`django-module-creation`** - For fat models, thin views pattern
4. **`security-best-practices`** - For input validation, access control
5. **`standard-folder-structure`** - For file organization
6. **`ui-ux-consistency`** - For template design
7. **`mobile-responsive`** - For responsive UI
8. **`code-quality-standards`** - For PEP 8, type hints, docstrings
9. **`component-reusability`** - For DRY principle, widget library
10. **`performance-optimization`** - For query optimization, indexing
11. **`full-stack-django-patterns`** - For constants, widgets, template tags
12. **`virtual-environment`** - For all Python/Django commands

**Claude Code should automatically apply ALL these skills without user reminding.**

---

## TodoWrite Integration

**IMPORTANT:** Use `TodoWrite` tool to track progress through all phases.

**Example Todo List:**

Phase 1 - Planning:
- [ ] Define module purpose and scope
- [ ] Design models and relationships
- [ ] Plan API endpoints
- [ ] Identify permission requirements

Phase 2 - Code Generation:
- [ ] Create Django app
- [ ] Create folder structure
- [ ] Create models.py
- [ ] Create constants.py
- [ ] Create migrations and run
- [ ] Create admin.py
- [ ] Create forms.py
- [ ] Create services/ (if needed)
- [ ] Create views.py
- [ ] Create urls.py
- [ ] Create templates/ (if needed)
- [ ] Create serializers.py (if API)
- [ ] Create comprehensive tests

Phase 3 - Quality Verification:
- [ ] Verify models checklist
- [ ] Verify constants checklist
- [ ] Verify forms checklist
- [ ] Verify views checklist
- [ ] Verify security checklist
- [ ] Verify code quality checklist

Phase 4 - Integration:
- [ ] Update INSTALLED_APPS
- [ ] Include URLs in config/urls.py
- [ ] Run migrations
- [ ] Run tests (verify ≥ 80% coverage)
- [ ] Test in admin panel
- [ ] Test web interface
- [ ] Test API (if applicable)
- [ ] Update documentation

**Mark todos as in_progress → completed as you work.**

---

## Common Pitfalls to Avoid

1. **❌ Skipping constants.py** - ALWAYS create this file, even for simple modules
2. **❌ Hardcoding Bootstrap classes in widgets** - Use `common.widgets` library instead (`BootstrapTextInput`, `BootstrapSelect`, etc.)
3. **❌ Not using template components** - MUST use `templates/components/` (card.html, alert.html, pagination.html, loading_spinner.html)
4. **❌ Not using template tags** - MUST use `common.templatetags.common_tags` (status_badge, diagnosis_badge, format_datetime, etc.)
5. **❌ Not using common utilities** - Use `common.utils` for validation (validate_phone, validate_image_file, validate_nric, etc.)
6. **❌ Fat views** - Move business logic to services or models
7. **❌ No abstract base models** - All models MUST inherit from `common.models.TimeStampedModel` at minimum
8. **❌ Missing permissions** - Every view/API must check permissions
9. **❌ Tests as afterthought** - Create tests during code generation
10. **❌ No type hints** - All functions/methods need type hints
11. **❌ Magic strings in code** - Use constants.py for all choices, error messages, config values
12. **❌ Skipping validation gates** - Fix quality issues before proceeding
13. **❌ Manual integration** - Automate with checklist
14. **❌ Reinventing the wheel** - Check `common/` app and `templates/components/` before creating new utilities/components

---

## Success Criteria

Module creation is complete when:

✅ All 4 phases completed (Planning, Code Generation, Quality, Integration)
✅ All validation gates passed
✅ All tests pass with ≥ 80% coverage
✅ All quality checklists verified
✅ Module integrated and working
✅ Documentation updated
✅ User can use the module successfully

---

## Example: Complete Module Creation Flow

**User request:** "Create a notification system module"

**Claude Code auto-response:**

1. **Planning Phase:**
   - Creates todo list with planning tasks
   - Asks clarifying questions:
     - "What types of notifications? (email, SMS, in-app, push)"
     - "Which user roles can send/receive notifications?"
     - "Are notifications real-time or scheduled?"
   - Designs models: `Notification`, `NotificationPreference`
   - Plans API endpoints: GET /api/notifications/, POST /api/notifications/
   - Identifies permissions: All roles can receive, staff can send

2. **Code Generation Phase:**
   - Creates `notifications/` app
   - Creates folder structure
   - Creates models with TimeStampedModel inheritance
   - Creates `constants.py` with NotificationType, NotificationStatus
   - Creates migrations, runs them
   - Creates admin.py with role-based permissions
   - Creates forms.py with widget library
   - Creates services/notification_service.py for sending logic
   - Creates thin views.py
   - Creates urls.py
   - Creates templates/ with Bootstrap 5
   - Creates serializers.py for API
   - Creates comprehensive tests for all components

3. **Quality Verification:**
   - Auto-verifies all checklists
   - Fixes any issues found
   - Runs `black`, `flake8`, `isort`

4. **Integration:**
   - Adds to INSTALLED_APPS
   - Includes URLs
   - Runs migrations
   - Runs tests (passes with 85% coverage)
   - Tests in admin panel
   - Tests web interface
   - Tests API
   - Updates README.md

**Result:** Fully functional, tested, documented notification system created autonomously following all best practices.

---

## Version History

- **1.0.0** (2025-11-22): Initial version with full lifecycle orchestration

---

**Last Updated:** 2025-11-22
