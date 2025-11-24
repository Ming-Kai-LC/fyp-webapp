---
name: Full-Stack Django Patterns & Performance
description: Comprehensive full-stack Django patterns including OOP best practices, Fat Models/Thin Views, CBVs, constants, utilities, error handling, testing, performance optimization, database tuning, and caching. Auto-applies to all Django development.
---

# Full-Stack Django Patterns

**Version:** 2.0.0 (Now includes django-module-creation patterns)
**Last Updated:** 2025-11-23
**Status:** ⭐ COMPREHENSIVE - Complete Django development framework
**Auto-apply:** YES - All Django module creation and development

## Overview

This skill enforces comprehensive reusability, DRY (Don't Repeat Yourself) principles, consistency, and efficiency across the entire Django full-stack application. It consolidates and extends ALL Django best practices including OOP patterns, architectural patterns, and cross-cutting concerns.

**Now includes (merged from django-module-creation):**
- Fat Models, Thin Views pattern
- Class-Based Views (CBVs) with mixins
- Type hints and comprehensive documentation
- Django app structure standards
- Model managers and querysets
- Service layer architecture

**Key Principles:**
- Define once, use everywhere (DRY)
- Fat Models, Thin Views (business logic in models)
- Centralize common patterns
- Maximize code reusability via OOP
- Ensure consistency across all modules
- Optimize for maintainability and performance
- Type hints for all code
- Comprehensive docstrings

---

## Auto-Apply Triggers

**Apply this skill when:**
- Creating any new Django module or feature
- Noticing repeated code patterns across modules
- Writing permission checks or authentication logic
- Creating forms, widgets, or templates
- Implementing business logic or services
- Adding API endpoints or serializers
- Writing tests or fixtures
- Setting up logging or monitoring
- Handling file uploads or media
- Adding background tasks or async operations
- Optimizing database queries
- Creating utility functions
- Refactoring existing code

---

## Section 1: Centralized Application Patterns

### 1.1 Constants Management

**Problem:** Magic strings and hardcoded values scattered throughout codebase lead to typos, inconsistency, and difficult refactoring.

**Solution:** Create a `constants.py` file in each Django app for centralized constants, enums, and choices.

#### Pattern:

```python
# app_name/constants.py

class UserRoles:
    """User role constants"""
    ADMIN = "admin"
    STAFF = "staff"
    PATIENT = "patient"

    CHOICES = [
        (ADMIN, "Administrator"),
        (STAFF, "Healthcare Staff"),
        (PATIENT, "Patient"),
    ]

    @classmethod
    def get_display_name(cls, role):
        """Get human-readable role name"""
        return dict(cls.CHOICES).get(role, role)


class DiagnosisTypes:
    """COVID-19 diagnosis constants"""
    COVID = "COVID"
    NORMAL = "Normal"
    VIRAL_PNEUMONIA = "Viral Pneumonia"
    LUNG_OPACITY = "Lung Opacity"

    CHOICES = [
        (COVID, "COVID-19 Positive"),
        (NORMAL, "Normal/Healthy"),
        (VIRAL_PNEUMONIA, "Viral Pneumonia"),
        (LUNG_OPACITY, "Lung Opacity"),
    ]


class PredictionStatus:
    """Prediction status constants"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

    CHOICES = [
        (PENDING, "Pending Analysis"),
        (PROCESSING, "Processing"),
        (COMPLETED, "Completed"),
        (FAILED, "Failed"),
    ]


class FileUploadLimits:
    """File upload constraints"""
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/jpg']
    ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png']
```

#### Usage in Models:

```python
# app_name/models.py
from django.db import models
from .constants import UserRoles, DiagnosisTypes, PredictionStatus

class UserProfile(models.Model):
    role = models.CharField(
        max_length=20,
        choices=UserRoles.CHOICES,
        default=UserRoles.PATIENT
    )

    def is_admin(self):
        return self.role == UserRoles.ADMIN

    def is_staff(self):
        return self.role == UserRoles.STAFF


class Prediction(models.Model):
    diagnosis = models.CharField(
        max_length=50,
        choices=DiagnosisTypes.CHOICES
    )
    status = models.CharField(
        max_length=20,
        choices=PredictionStatus.CHOICES,
        default=PredictionStatus.PENDING
    )
```

### 1.2 Application-Wide Configuration

Create `config.py` for feature flags and module-specific settings:

```python
# app_name/config.py

class AppConfig:
    """Application configuration"""

    # Feature flags
    ENABLE_EMAIL_NOTIFICATIONS = True
    ENABLE_SMS_NOTIFICATIONS = False
    ENABLE_EXPORT_TO_PDF = True
    ENABLE_BULK_UPLOAD = False

    # Business rules
    MAX_PREDICTIONS_PER_DAY = 50
    REPORT_RETENTION_DAYS = 365
    SESSION_TIMEOUT_MINUTES = 30

    # ML Model settings
    MODEL_CONFIDENCE_THRESHOLD = 0.75
    ENABLE_MODEL_CACHING = True
    MAX_BATCH_SIZE = 10
```

---

## Section 2: Reusable Utilities Library

### 2.1 Common Utility Functions

Create a `utils.py` file in each app for reusable helper functions.

```python
# app_name/utils.py

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.files.uploadedfile import UploadedFile
import hashlib
import os


class DateTimeUtils:
    """Date and time utility functions"""

    @staticmethod
    def get_age_from_birthdate(birthdate: datetime.date) -> int:
        """Calculate age from birthdate"""
        today = timezone.now().date()
        return today.year - birthdate.year - (
            (today.month, today.day) < (birthdate.month, birthdate.day)
        )

    @staticmethod
    def format_date_range(start_date: datetime, end_date: datetime) -> str:
        """Format date range for display"""
        return f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"

    @staticmethod
    def is_within_hours(dt: datetime, hours: int) -> bool:
        """Check if datetime is within X hours from now"""
        threshold = timezone.now() - timedelta(hours=hours)
        return dt >= threshold


class StringUtils:
    """String manipulation utilities"""

    @staticmethod
    def truncate(text: str, length: int = 50, suffix: str = "...") -> str:
        """Truncate string to specified length"""
        if len(text) <= length:
            return text
        return text[:length - len(suffix)] + suffix

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize whitespace in string"""
        return " ".join(text.split())

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        import re
        filename = re.sub(r'[^\w\s.-]', '', filename)
        return filename.strip()


class FileUtils:
    """File handling utilities"""

    @staticmethod
    def generate_unique_filename(original_filename: str, prefix: str = "") -> str:
        """Generate unique filename with timestamp and hash"""
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(original_filename)
        hash_suffix = hashlib.md5(f"{name}{timestamp}".encode()).hexdigest()[:8]
        return f"{prefix}{timestamp}_{hash_suffix}{ext}"

    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Get file extension in lowercase"""
        return os.path.splitext(filename)[1].lower()

    @staticmethod
    def validate_file_size(file: UploadedFile, max_size: int) -> bool:
        """Validate file size"""
        return file.size <= max_size

    @staticmethod
    def get_file_hash(file: UploadedFile, algorithm: str = 'sha256') -> str:
        """Calculate file hash"""
        hasher = hashlib.new(algorithm)
        for chunk in file.chunks():
            hasher.update(chunk)
        return hasher.hexdigest()


class QueryUtils:
    """Database query utilities"""

    @staticmethod
    def get_or_none(model, **kwargs):
        """Get object or return None instead of raising exception"""
        try:
            return model.objects.get(**kwargs)
        except model.DoesNotExist:
            return None

    @staticmethod
    def bulk_create_or_update(model, objects: List[Dict[str, Any]], unique_fields: List[str]):
        """Bulk create or update objects"""
        from django.db.models import Q
        existing = model.objects.filter(
            Q(**{field: obj[field] for field in unique_fields})
            for obj in objects
        )
        # Implementation details...
        pass
```

---

## Section 3: Error Handling & Validation

### 3.1 Custom Exception Hierarchy

```python
# app_name/exceptions.py

class AppBaseException(Exception):
    """Base exception for all app-specific exceptions"""
    default_message = "An error occurred"
    status_code = 400

    def __init__(self, message: str = None, **kwargs):
        self.message = message or self.default_message
        self.extra_data = kwargs
        super().__init__(self.message)


class ValidationError(AppBaseException):
    """Validation error"""
    default_message = "Validation failed"
    status_code = 400


class PermissionDeniedError(AppBaseException):
    """Permission denied"""
    default_message = "You don't have permission to perform this action"
    status_code = 403


class ResourceNotFoundError(AppBaseException):
    """Resource not found"""
    default_message = "The requested resource was not found"
    status_code = 404


class FileUploadError(AppBaseException):
    """File upload error"""
    default_message = "File upload failed"
    status_code = 400


class MLInferenceError(AppBaseException):
    """ML model inference error"""
    default_message = "Model prediction failed"
    status_code = 500
```

### 3.2 Custom Validators

```python
# app_name/validators.py

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from .constants import FileUploadLimits
import magic  # python-magic for file type detection


def validate_image_file(file):
    """Comprehensive image file validation"""
    # Check file size
    if file.size > FileUploadLimits.MAX_IMAGE_SIZE:
        raise ValidationError(
            f"File size exceeds maximum allowed size of "
            f"{FileUploadLimits.MAX_IMAGE_SIZE / (1024*1024)}MB"
        )

    # Check file extension
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in FileUploadLimits.ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            f"File extension '{ext}' is not allowed. "
            f"Allowed: {', '.join(FileUploadLimits.ALLOWED_IMAGE_EXTENSIONS)}"
        )

    # Check actual file type (not just extension)
    file_type = magic.from_buffer(file.read(1024), mime=True)
    file.seek(0)  # Reset file pointer

    if file_type not in FileUploadLimits.ALLOWED_IMAGE_TYPES:
        raise ValidationError(
            f"File type '{file_type}' is not allowed. "
            f"Expected image file."
        )


def validate_age_range(age: int, min_age: int = 0, max_age: int = 150):
    """Validate age is within reasonable range"""
    if not min_age <= age <= max_age:
        raise ValidationError(
            f"Age must be between {min_age} and {max_age}"
        )


def validate_phone_number(phone: str):
    """Validate phone number format"""
    import re
    pattern = r'^\+?1?\d{9,15}$'
    if not re.match(pattern, phone):
        raise ValidationError(
            "Phone number must be in format: '+999999999' (9-15 digits)"
        )
```

### 3.3 Error Response Handlers

```python
# app_name/error_handlers.py

from django.http import JsonResponse
from django.shortcuts import render
from .exceptions import AppBaseException
import logging

logger = logging.getLogger(__name__)


def handle_app_exception(request, exception: AppBaseException):
    """Handle custom app exceptions"""
    logger.error(
        f"AppException: {exception.message}",
        extra={
            'user': request.user.username if request.user.is_authenticated else 'anonymous',
            'path': request.path,
            'method': request.method,
            **exception.extra_data
        }
    )

    if request.accepts('application/json'):
        return JsonResponse({
            'error': exception.message,
            'status': exception.status_code,
            **exception.extra_data
        }, status=exception.status_code)

    return render(request, 'error.html', {
        'error_message': exception.message,
        'status_code': exception.status_code
    }, status=exception.status_code)
```

---

## Section 4: Cross-Module Communication

### 4.1 Django Signals Best Practices

```python
# app_name/signals.py

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver, Signal
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

# Custom signals
prediction_completed = Signal()
report_generated = Signal()
user_role_changed = Signal()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when User is created"""
    if created:
        from .models import UserProfile
        UserProfile.objects.create(user=instance)
        logger.info(f"UserProfile created for user: {instance.username}")


@receiver(prediction_completed)
def send_prediction_notification(sender, prediction, **kwargs):
    """Send notification when prediction is completed"""
    from notifications.services import NotificationService

    NotificationService.send_prediction_result(
        user=prediction.xray.patient.user,
        prediction=prediction
    )
    logger.info(f"Notification sent for prediction: {prediction.id}")


# Signal connection best practices:
# 1. Always use receiver decorator for clarity
# 2. Log signal actions for debugging
# 3. Keep signal handlers lightweight
# 4. For heavy operations, queue background tasks
# 5. Avoid circular imports by importing models inside functions
```

### 4.2 Service-to-Service Communication

```python
# app_name/services/communication.py

from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ServiceRegistry:
    """Registry for cross-module service communication"""
    _services = {}

    @classmethod
    def register(cls, name: str, service_class):
        """Register a service"""
        cls._services[name] = service_class
        logger.debug(f"Service registered: {name}")

    @classmethod
    def get_service(cls, name: str):
        """Get registered service"""
        service = cls._services.get(name)
        if not service:
            raise ValueError(f"Service '{name}' not registered")
        return service


# Usage:
# In each app's apps.py:
class DetectionConfig(AppConfig):
    def ready(self):
        from .services import XRayProcessingService
        ServiceRegistry.register('xray_processing', XRayProcessingService)

# In other modules:
service_class = ServiceRegistry.get_service('xray_processing')
service = service_class()
result = service.process(data)
```

---

## Section 5: Advanced Model Patterns

### 5.1 Abstract Base Models

**CRITICAL:** Use these abstract base models for ALL new models to eliminate field duplication.

```python
# app_name/models/base.py

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """Abstract base model with timestamp fields"""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']
        get_latest_by = 'created_at'


class SoftDeleteModel(models.Model):
    """Abstract base model with soft delete functionality"""
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(app_label)s_%(class)s_deleted'
    )

    class Meta:
        abstract = True

    def soft_delete(self, user=None):
        """Soft delete the object"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])

    def restore(self):
        """Restore soft-deleted object"""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])


class AuditableModel(TimeStampedModel):
    """Abstract base with audit fields"""
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(app_label)s_%(class)s_created'
    )
    updated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(app_label)s_%(class)s_updated'
    )

    class Meta:
        abstract = True


class FullAuditModel(TimeStampedModel, SoftDeleteModel, AuditableModel):
    """Complete audit trail model"""
    class Meta:
        abstract = True
```

#### Usage:

```python
# app_name/models.py
from .models.base import TimeStampedModel, AuditableModel

class Patient(TimeStampedModel):  # Inherits created_at, updated_at
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # NO MORE: created_at = models.DateTimeField(auto_now_add=True)
    # NO MORE: updated_at = models.DateTimeField(auto_now=True)


class MedicalRecord(AuditableModel):  # Inherits timestamps + audit fields
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    # Automatically has: created_at, updated_at, created_by, updated_by
```

### 5.2 Custom Manager Patterns

```python
# app_name/managers.py

from django.db import models
from django.utils import timezone


class SoftDeleteManager(models.Manager):
    """Manager that excludes soft-deleted objects"""

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def deleted(self):
        """Get only deleted objects"""
        return super().get_queryset().filter(is_deleted=True)

    def with_deleted(self):
        """Get all objects including deleted"""
        return super().get_queryset()


class TimestampedQuerySet(models.QuerySet):
    """QuerySet with timestamp-related methods"""

    def created_today(self):
        """Objects created today"""
        today = timezone.now().date()
        return self.filter(created_at__date=today)

    def created_within_days(self, days):
        """Objects created within last X days"""
        threshold = timezone.now() - timezone.timedelta(days=days)
        return self.filter(created_at__gte=threshold)

    def updated_recently(self, hours=24):
        """Objects updated in last X hours"""
        threshold = timezone.now() - timezone.timedelta(hours=hours)
        return self.filter(updated_at__gte=threshold)


class PredictionQuerySet(models.QuerySet):
    """Custom queryset for Prediction model"""

    def covid_positive(self):
        """Get COVID-positive predictions"""
        from .constants import DiagnosisTypes
        return self.filter(diagnosis=DiagnosisTypes.COVID)

    def completed(self):
        """Get completed predictions"""
        from .constants import PredictionStatus
        return self.filter(status=PredictionStatus.COMPLETED)

    def with_patient_details(self):
        """Optimize query with related data"""
        return self.select_related(
            'xray__patient__user',
            'xray__patient__user__profile'
        ).prefetch_related('reports')


# Usage in models:
class Prediction(TimeStampedModel):
    # ... fields ...

    objects = models.Manager.from_queryset(PredictionQuerySet)()

    # Usage: Prediction.objects.covid_positive().completed()
```

---

## Section 6: Form & Widget Library

### 6.1 Reusable Bootstrap Widgets

**CRITICAL:** Use these instead of hardcoding Bootstrap classes in every form.

```python
# app_name/widgets.py

from django import forms


class BootstrapMixin:
    """Mixin to add Bootstrap classes to widgets"""
    bootstrap_class = 'form-control'

    def __init__(self, *args, **kwargs):
        attrs = kwargs.get('attrs', {})
        css_class = attrs.get('class', '')

        # Add Bootstrap class if not already present
        if self.bootstrap_class not in css_class:
            attrs['class'] = f'{css_class} {self.bootstrap_class}'.strip()

        kwargs['attrs'] = attrs
        super().__init__(*args, **kwargs)


class BootstrapTextInput(BootstrapMixin, forms.TextInput):
    """Bootstrap text input"""
    pass


class BootstrapEmailInput(BootstrapMixin, forms.EmailInput):
    """Bootstrap email input"""
    pass


class BootstrapPasswordInput(BootstrapMixin, forms.PasswordInput):
    """Bootstrap password input"""
    pass


class BootstrapTextarea(BootstrapMixin, forms.Textarea):
    """Bootstrap textarea"""
    def __init__(self, *args, rows=3, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs['rows'] = rows


class BootstrapSelect(BootstrapMixin, forms.Select):
    """Bootstrap select dropdown"""
    bootstrap_class = 'form-select'


class BootstrapFileInput(BootstrapMixin, forms.FileInput):
    """Bootstrap file input"""
    def __init__(self, accept=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if accept:
            self.attrs['accept'] = accept


class BootstrapDateInput(BootstrapMixin, forms.DateInput):
    """Bootstrap date picker"""
    input_type = 'date'


class BootstrapCheckboxInput(forms.CheckboxInput):
    """Bootstrap checkbox"""
    def __init__(self, *args, **kwargs):
        attrs = kwargs.get('attrs', {})
        attrs['class'] = attrs.get('class', '') + ' form-check-input'
        kwargs['attrs'] = attrs
        super().__init__(*args, **kwargs)
```

#### Usage in Forms:

```python
# app_name/forms.py
from django import forms
from .widgets import (
    BootstrapTextInput,
    BootstrapEmailInput,
    BootstrapFileInput,
    BootstrapSelect,
    BootstrapTextarea
)

class PatientRegistrationForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'email', 'phone', 'address']
        widgets = {
            'first_name': BootstrapTextInput(),  # Automatic form-control class!
            'last_name': BootstrapTextInput(),
            'email': BootstrapEmailInput(),
            'phone': BootstrapTextInput(attrs={'placeholder': '+1234567890'}),
            'address': BootstrapTextarea(rows=4),
        }


class XRayUploadForm(forms.ModelForm):
    class Meta:
        model = XRayImage
        fields = ['original_image', 'notes']
        widgets = {
            'original_image': BootstrapFileInput(accept='image/*'),
            'notes': BootstrapTextarea(rows=3),
        }
```

### 6.2 Form Mixins

```python
# app_name/forms/mixins.py

class BootstrapFormMixin:
    """Automatically add Bootstrap classes to all form fields"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget

            if isinstance(widget, (forms.TextInput, forms.EmailInput, forms.PasswordInput, forms.Textarea)):
                widget.attrs['class'] = widget.attrs.get('class', '') + ' form-control'
            elif isinstance(widget, forms.Select):
                widget.attrs['class'] = widget.attrs.get('class', '') + ' form-select'
            elif isinstance(widget, forms.CheckboxInput):
                widget.attrs['class'] = widget.attrs.get('class', '') + ' form-check-input'


class CrispyFormMixin:
    """Add crispy forms helper"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, 'helper'):
            return

        from crispy_forms.helper import FormHelper
        from crispy_forms.layout import Submit

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit', css_class='btn btn-primary'))
```

---

## Section 7: Template Tag & Filter Library

### 7.1 Custom Template Tags

```python
# app_name/templatetags/common_tags.py

from django import template
from django.utils.safestring import mark_safe
from django.urls import reverse
import json

register = template.Library()


@register.filter
def badge_class(status):
    """Return Bootstrap badge class based on status"""
    mapping = {
        'pending': 'bg-warning',
        'processing': 'bg-info',
        'completed': 'bg-success',
        'failed': 'bg-danger',
        'cancelled': 'bg-secondary',
        'approved': 'bg-success',
        'rejected': 'bg-danger',
    }
    return mapping.get(status.lower(), 'bg-info')


@register.filter
def diagnosis_badge_class(diagnosis):
    """Return badge class for diagnosis type"""
    mapping = {
        'COVID': 'bg-danger',
        'Normal': 'bg-success',
        'Viral Pneumonia': 'bg-warning',
        'Lung Opacity': 'bg-info',
    }
    return mapping.get(diagnosis, 'bg-secondary')


@register.filter
def percentage(value, decimals=1):
    """Format as percentage"""
    try:
        return f"{float(value) * 100:.{decimals}f}%"
    except (ValueError, TypeError):
        return "0%"


@register.filter
def truncate_chars(value, length=50):
    """Truncate string to specified length"""
    if len(str(value)) <= length:
        return value
    return f"{str(value)[:length]}..."


@register.simple_tag
def user_can(user, action, obj=None):
    """Check if user has permission for action"""
    # Complex permission checking logic
    if not user.is_authenticated:
        return False

    if user.profile.is_admin():
        return True

    # Add more permission logic here
    return False


@register.inclusion_tag('components/pagination.html', takes_context=True)
def render_pagination(context, page_obj, param_name='page'):
    """Render pagination component"""
    return {
        'page_obj': page_obj,
        'param_name': param_name,
        'request': context['request'],
    }


@register.inclusion_tag('components/status_badge.html')
def status_badge(status, label=None):
    """Render status badge component"""
    return {
        'status': status,
        'label': label or status.title(),
        'badge_class': badge_class(status),
    }


@register.simple_tag
def json_encode(value):
    """Convert Python object to JSON for JavaScript"""
    return mark_safe(json.dumps(value))


@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    return dictionary.get(key)


@register.filter
def add_class(field, css_class):
    """Add CSS class to form field"""
    return field.as_widget(attrs={'class': css_class})
```

#### Usage in Templates:

```django
{% load common_tags %}

<!-- Status badge -->
<span class="badge {{ prediction.status|badge_class }}">
    {{ prediction.status|title }}
</span>

<!-- Or use inclusion tag -->
{% status_badge prediction.status %}

<!-- Diagnosis badge -->
<span class="badge {{ prediction.diagnosis|diagnosis_badge_class }}">
    {{ prediction.diagnosis }}
</span>

<!-- Percentage -->
Confidence: {{ prediction.confidence|percentage:2 }}

<!-- Pagination -->
{% render_pagination page_obj %}

<!-- Permission check -->
{% user_can request.user 'delete' object as can_delete %}
{% if can_delete %}
    <button>Delete</button>
{% endif %}
```

### 7.2 Template Components

Create reusable template components in `templates/components/`:

```django
<!-- templates/components/pagination.html -->
{% if page_obj.has_other_pages %}
<nav aria-label="Page navigation">
    <ul class="pagination">
        {% if page_obj.has_previous %}
            <li class="page-item">
                <a class="page-link" href="?{{ param_name }}=1">First</a>
            </li>
            <li class="page-item">
                <a class="page-link" href="?{{ param_name }}={{ page_obj.previous_page_number }}">Previous</a>
            </li>
        {% endif %}

        {% for num in page_obj.paginator.page_range %}
            {% if page_obj.number == num %}
                <li class="page-item active">
                    <span class="page-link">{{ num }}</span>
                </li>
            {% elif num > page_obj.number|add:'-3' and num < page_obj.number|add:'3' %}
                <li class="page-item">
                    <a class="page-link" href="?{{ param_name }}={{ num }}">{{ num }}</a>
                </li>
            {% endif %}
        {% endfor %}

        {% if page_obj.has_next %}
            <li class="page-item">
                <a class="page-link" href="?{{ param_name }}={{ page_obj.next_page_number }}">Next</a>
            </li>
            <li class="page-item">
                <a class="page-link" href="?{{ param_name }}={{ page_obj.paginator.num_pages }}">Last</a>
            </li>
        {% endif %}
    </ul>
</nav>
{% endif %}
```

```django
<!-- templates/components/status_badge.html -->
<span class="badge {{ badge_class }}">{{ label }}</span>
```

---

## Section 8: API Patterns & Standards

### 8.1 Serializer Reusability

```python
# app_name/serializers/base.py

from rest_framework import serializers
from django.contrib.auth.models import User


class TimestampedSerializerMixin:
    """Mixin for timestamp fields"""
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class UserBasicSerializer(serializers.ModelSerializer):
    """Reusable user serializer for nested relationships"""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name']
        read_only_fields = ['id', 'username', 'email']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class DynamicFieldsSerializerMixin:
    """Allow clients to specify which fields to return"""

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        exclude = kwargs.pop('exclude', None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        if exclude is not None:
            for field_name in exclude:
                self.fields.pop(field_name, None)
```

### 8.2 Standard API Response Format

```python
# api/responses.py

from rest_framework.response import Response
from rest_framework import status
from typing import Any, Dict, Optional


class APIResponse:
    """Standardized API response format"""

    @staticmethod
    def success(data: Any = None, message: str = "Success", status_code: int = status.HTTP_200_OK):
        """Success response"""
        return Response({
            'success': True,
            'message': message,
            'data': data
        }, status=status_code)

    @staticmethod
    def error(message: str, errors: Optional[Dict] = None, status_code: int = status.HTTP_400_BAD_REQUEST):
        """Error response"""
        response_data = {
            'success': False,
            'message': message,
        }
        if errors:
            response_data['errors'] = errors
        return Response(response_data, status=status_code)

    @staticmethod
    def paginated(data: Any, page_obj, message: str = "Success"):
        """Paginated response"""
        return Response({
            'success': True,
            'message': message,
            'data': data,
            'pagination': {
                'count': page_obj.paginator.count,
                'num_pages': page_obj.paginator.num_pages,
                'current_page': page_obj.number,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
                'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
            }
        }, status=status.HTTP_200_OK)
```

### 8.3 Pagination Standards

```python
# api/pagination.py

from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for all API endpoints"""
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class LargeResultsSetPagination(PageNumberPagination):
    """Pagination for large datasets"""
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 500


# In settings.py:
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'api.pagination.StandardResultsSetPagination',
}
```

---

## Section 9: Authentication & Authorization Patterns

### 9.1 Centralized Decorators

**CRITICAL:** All permission decorators should be in ONE location.

```python
# app_name/decorators.py

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from .constants import UserRoles


def role_required(*roles):
    """
    Generic role-based access decorator
    Usage: @role_required(UserRoles.STAFF, UserRoles.ADMIN)
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if not hasattr(request.user, 'profile'):
                messages.error(request, "User profile not found.")
                return redirect('home')

            if request.user.profile.role not in roles:
                messages.error(
                    request,
                    f"Access denied. This page requires {', '.join(roles)} privileges."
                )
                return redirect('home')

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# Convenience decorators
admin_required = role_required(UserRoles.ADMIN)
staff_required = role_required(UserRoles.STAFF, UserRoles.ADMIN)
patient_required = role_required(UserRoles.PATIENT)


def ajax_required(view_func):
    """Require AJAX request"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'AJAX request required'}, status=400)
        return view_func(request, *args, **kwargs)
    return wrapper


def object_owner_required(get_object_func):
    """Require user to be owner of object"""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            obj = get_object_func(request, *args, **kwargs)

            # Admin can access anything
            if request.user.profile.is_admin():
                return view_func(request, *args, **kwargs)

            # Check ownership
            if hasattr(obj, 'user') and obj.user != request.user:
                raise Http404("Object not found")
            elif hasattr(obj, 'patient') and obj.patient.user != request.user:
                raise Http404("Object not found")

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
```

### 9.2 Permission Helper Functions

```python
# app_name/permissions.py

from typing import Optional
from django.contrib.auth.models import User
from .constants import UserRoles


class PermissionChecker:
    """Centralized permission checking logic"""

    @staticmethod
    def can_view_patient_data(user: User, patient) -> bool:
        """Check if user can view patient data"""
        if not user.is_authenticated:
            return False

        # Admin and staff can view all
        if user.profile.role in [UserRoles.ADMIN, UserRoles.STAFF]:
            return True

        # Patients can only view their own data
        if user.profile.role == UserRoles.PATIENT:
            return patient.user == user

        return False

    @staticmethod
    def can_edit_patient_data(user: User, patient) -> bool:
        """Check if user can edit patient data"""
        if not user.is_authenticated:
            return False

        # Admin can edit all
        if user.profile.is_admin():
            return True

        # Staff can edit medical records but not personal info
        if user.profile.is_staff():
            return True  # Implement field-level permissions separately

        # Patients can edit their own profile
        if user.profile.role == UserRoles.PATIENT:
            return patient.user == user

        return False

    @staticmethod
    def can_delete_prediction(user: User, prediction) -> bool:
        """Check if user can delete prediction"""
        if not user.is_authenticated:
            return False

        # Admin can delete anything
        if user.profile.is_admin():
            return True

        # Staff can delete only pending predictions
        if user.profile.is_staff():
            from .constants import PredictionStatus
            return prediction.status == PredictionStatus.PENDING

        return False
```

---

## Section 10: Testing Patterns & Fixtures

### 10.1 Test Factories

```python
# app_name/tests/factories.py

from django.contrib.auth.models import User
from django.utils import timezone
import factory
from factory.django import DjangoModelFactory
from ..models import Patient, XRayImage, Prediction
from ..constants import UserRoles, DiagnosisTypes


class UserFactory(DjangoModelFactory):
    """Factory for User model"""
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True


class PatientFactory(DjangoModelFactory):
    """Factory for Patient model"""
    class Meta:
        model = Patient

    user = factory.SubFactory(UserFactory)
    date_of_birth = factory.Faker('date_of_birth', minimum_age=18, maximum_age=90)
    gender = factory.Iterator(['M', 'F', 'O'])
    phone_number = factory.Faker('phone_number')
    address = factory.Faker('address')


class XRayImageFactory(DjangoModelFactory):
    """Factory for XRayImage model"""
    class Meta:
        model = XRayImage

    patient = factory.SubFactory(PatientFactory)
    original_image = factory.django.ImageField(color='blue')
    notes = factory.Faker('text', max_nb_chars=200)


class PredictionFactory(DjangoModelFactory):
    """Factory for Prediction model"""
    class Meta:
        model = Prediction

    xray = factory.SubFactory(XRayImageFactory)
    diagnosis = factory.Iterator([DiagnosisTypes.COVID, DiagnosisTypes.NORMAL])
    confidence = factory.Faker('pyfloat', left_digits=0, right_digits=2, positive=True, max_value=1)
    model_version = "v1.0.0"
```

#### Usage in Tests:

```python
# app_name/tests/test_views.py

from django.test import TestCase
from .factories import UserFactory, PatientFactory, PredictionFactory


class PredictionViewTest(TestCase):
    def setUp(self):
        # Create test data easily
        self.admin_user = UserFactory(profile__role=UserRoles.ADMIN)
        self.patient = PatientFactory()
        self.prediction = PredictionFactory(xray__patient=self.patient)

    def test_admin_can_view_all_predictions(self):
        self.client.force_login(self.admin_user)
        response = self.client.get('/predictions/')
        self.assertEqual(response.status_code, 200)
```

### 10.2 Reusable Test Mixins

```python
# app_name/tests/mixins.py

from django.test import TestCase
from django.contrib.auth.models import User
from ..constants import UserRoles


class AuthenticatedTestMixin:
    """Mixin for tests requiring authentication"""

    def setUp(self):
        super().setUp()
        self.user = self.create_user()
        self.client.force_login(self.user)

    def create_user(self, role=UserRoles.PATIENT):
        """Create user with specific role"""
        from .factories import UserFactory
        return UserFactory(profile__role=role)


class AdminTestMixin(AuthenticatedTestMixin):
    """Mixin for admin-only tests"""

    def setUp(self):
        super().setUp()
        self.admin_user = self.create_user(role=UserRoles.ADMIN)
        self.client.force_login(self.admin_user)


class APITestMixin:
    """Mixin for API tests"""

    def api_get(self, url, **kwargs):
        """Make authenticated API GET request"""
        return self.client.get(url, HTTP_AUTHORIZATION=f'Bearer {self.token}', **kwargs)

    def api_post(self, url, data=None, **kwargs):
        """Make authenticated API POST request"""
        return self.client.post(
            url,
            data=data,
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}',
            **kwargs
        )
```

---

## Section 11: Logging & Monitoring

### 11.1 Standard Logging Configuration

```python
# config/logging_config.py

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        }
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/django.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose'
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/security.log',
            'maxBytes': 10485760,
            'backupCount': 10,
            'formatter': 'json'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'detection': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
```

### 11.2 Logging Patterns

```python
# app_name/views.py

import logging
from django.utils import timezone

logger = logging.getLogger(__name__)
security_logger = logging.getLogger('security')


def upload_xray(request):
    """Upload X-ray with comprehensive logging"""
    logger.info(
        f"X-ray upload initiated",
        extra={
            'user_id': request.user.id,
            'user_role': request.user.profile.role,
            'timestamp': timezone.now().isoformat()
        }
    )

    try:
        # Process upload
        result = process_upload(request.FILES['xray'])

        logger.info(
            f"X-ray uploaded successfully",
            extra={
                'user_id': request.user.id,
                'xray_id': result.id,
                'file_size': request.FILES['xray'].size
            }
        )

    except Exception as e:
        logger.error(
            f"X-ray upload failed: {str(e)}",
            extra={
                'user_id': request.user.id,
                'error_type': type(e).__name__
            },
            exc_info=True
        )

        # Log security events
        if isinstance(e, SecurityError):
            security_logger.warning(
                f"Security violation: {str(e)}",
                extra={
                    'user_id': request.user.id,
                    'ip_address': request.META.get('REMOTE_ADDR'),
                    'user_agent': request.META.get('HTTP_USER_AGENT')
                }
            )
```

---

## Section 12: Background Tasks & Async

### 12.1 Celery Task Patterns

```python
# app_name/tasks.py

from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone
import logging

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3)
def process_xray_async(self, xray_id):
    """
    Process X-ray image asynchronously

    Args:
        xray_id: ID of XRayImage to process

    Returns:
        Prediction ID
    """
    from .models import XRayImage, Prediction
    from .services import MLInferenceService

    try:
        logger.info(f"Processing X-ray {xray_id}")

        xray = XRayImage.objects.get(id=xray_id)
        service = MLInferenceService()
        prediction = service.predict(xray)

        logger.info(f"X-ray {xray_id} processed successfully: Prediction {prediction.id}")
        return prediction.id

    except XRayImage.DoesNotExist:
        logger.error(f"X-ray {xray_id} not found")
        raise

    except Exception as exc:
        logger.error(f"Error processing X-ray {xray_id}: {str(exc)}", exc_info=True)
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def cleanup_old_files():
    """Clean up old temporary files - runs daily"""
    from .models import XRayImage

    threshold = timezone.now() - timezone.timedelta(days=30)
    old_images = XRayImage.objects.filter(
        created_at__lt=threshold,
        is_temporary=True
    )

    count = old_images.count()
    old_images.delete()

    logger.info(f"Cleaned up {count} old temporary images")
    return count
```

---

## Section 13: File Upload Security & Processing

### 13.1 Secure File Upload Pattern

```python
# app_name/services/file_upload.py

from django.core.files.uploadedfile import UploadedFile
from django.core.exceptions import ValidationError
from ..validators import validate_image_file
from ..utils import FileUtils
from ..constants import FileUploadLimits
import magic
import logging

logger = logging.getLogger(__name__)


class SecureFileUploadService:
    """Secure file upload with comprehensive validation"""

    def __init__(self, file: UploadedFile, user, allowed_types=None):
        self.file = file
        self.user = user
        self.allowed_types = allowed_types or FileUploadLimits.ALLOWED_IMAGE_TYPES

    def validate(self):
        """Comprehensive file validation"""
        # Size check
        if not FileUtils.validate_file_size(self.file, FileUploadLimits.MAX_IMAGE_SIZE):
            raise ValidationError("File size exceeds maximum allowed size")

        # Extension check
        ext = FileUtils.get_file_extension(self.file.name)
        if ext not in FileUploadLimits.ALLOWED_IMAGE_EXTENSIONS:
            raise ValidationError(f"File extension {ext} not allowed")

        # MIME type check
        file_type = magic.from_buffer(self.file.read(1024), mime=True)
        self.file.seek(0)

        if file_type not in self.allowed_types:
            raise ValidationError(f"File type {file_type} not allowed")

        # File hash (for duplicate detection)
        file_hash = FileUtils.get_file_hash(self.file)
        self.file.seek(0)

        logger.info(
            f"File validated: {self.file.name}",
            extra={
                'user_id': self.user.id,
                'file_size': self.file.size,
                'file_type': file_type,
                'file_hash': file_hash
            }
        )

        return True

    def process(self):
        """Process and save file securely"""
        self.validate()

        # Generate secure filename
        secure_filename = FileUtils.generate_unique_filename(
            self.file.name,
            prefix=f"user_{self.user.id}_"
        )

        # Save with secure filename
        self.file.name = secure_filename

        return self.file
```

---

## Section 14: Frontend-Backend Integration

### 14.1 AJAX Patterns

```javascript
// static/js/ajax_utils.js

class AjaxHelper {
    /**
     * Get CSRF token from cookie
     */
    static getCSRFToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    /**
     * Make AJAX POST request with CSRF token
     */
    static async post(url, data) {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    /**
     * Make AJAX GET request
     */
    static async get(url) {
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    /**
     * Submit form via AJAX
     */
    static async submitForm(form) {
        const formData = new FormData(form);

        const response = await fetch(form.action, {
            method: form.method || 'POST',
            headers: {
                'X-CSRFToken': this.getCSRFToken(),
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        });

        return await response.json();
    }
}

// Usage:
// AjaxHelper.post('/api/predict/', {xray_id: 123}).then(data => console.log(data));
```

---

## Section 15: Database Optimization Patterns

### 15.1 Query Optimization

```python
# app_name/views.py

from django.db.models import Prefetch, Count, Q, F


def list_predictions_optimized(request):
    """List predictions with optimized queries"""

    # ✅ GOOD: Use select_related for foreign keys
    predictions = Prediction.objects.select_related(
        'xray__patient__user',
        'xray__patient__user__profile'
    )

    # ✅ GOOD: Use prefetch_related for reverse FK and M2M
    predictions = predictions.prefetch_related(
        'reports',
        'reports__generated_by',
        Prefetch(
            'reports',
            queryset=Report.objects.filter(is_published=True),
            to_attr='published_reports'
        )
    )

    # ✅ GOOD: Use annotations to avoid extra queries
    predictions = predictions.annotate(
        report_count=Count('reports'),
        days_since_created=F('created_at') - timezone.now()
    )

    # ✅ GOOD: Filter at database level
    if request.user.profile.is_patient():
        predictions = predictions.filter(xray__patient__user=request.user)

    # ✅ GOOD: Use only() to fetch specific fields
    # predictions = predictions.only('id', 'diagnosis', 'confidence', 'created_at')

    # ✅ GOOD: Use defer() to exclude large fields
    predictions = predictions.defer('preprocessed_image')

    return predictions


# ❌ BAD: N+1 query problem
def list_predictions_bad(request):
    predictions = Prediction.objects.all()
    for pred in predictions:
        print(pred.xray.patient.user.username)  # Query for EACH prediction!
        print(pred.reports.count())  # Another query for EACH!
```

### 15.2 Database Indexing

```python
# app_name/models.py

from django.db import models


class Prediction(TimeStampedModel):
    diagnosis = models.CharField(
        max_length=50,
        db_index=True  # ✅ Index frequently filtered fields
    )
    status = models.CharField(
        max_length=20,
        db_index=True  # ✅ Index frequently filtered fields
    )
    confidence = models.FloatField()

    class Meta:
        indexes = [
            # ✅ Composite index for common query patterns
            models.Index(fields=['diagnosis', 'status']),
            models.Index(fields=['xray', 'created_at']),
            models.Index(fields=['-created_at']),  # For ordering
        ]
        ordering = ['-created_at']
```

---

## Anti-Patterns to Avoid

### ❌ 1. Magic Strings

```python
# ❌ BAD
if user.profile.role == "staff":
    pass

# ✅ GOOD
from .constants import UserRoles
if user.profile.role == UserRoles.STAFF:
    pass
```

### ❌ 2. Repeated Model Fields

```python
# ❌ BAD
class Model1(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# ✅ GOOD
class Model1(TimeStampedModel):
    pass  # Inherits timestamp fields!
```

### ❌ 3. Inline Permission Checks

```python
# ❌ BAD
def view(request):
    if not request.user.profile.is_staff() and not request.user.profile.is_admin():
        return HttpResponseForbidden()

# ✅ GOOD
@staff_required
def view(request):
    pass
```

### ❌ 4. No Query Optimization

```python
# ❌ BAD
predictions = Prediction.objects.all()
for pred in predictions:
    print(pred.xray.patient.user.username)  # N+1!

# ✅ GOOD
predictions = Prediction.objects.select_related('xray__patient__user')
for pred in predictions:
    print(pred.xray.patient.user.username)  # Single query!
```

### ❌ 5. Hardcoded Bootstrap Classes

```python
# ❌ BAD
widgets = {
    'name': forms.TextInput(attrs={'class': 'form-control'}),
    'email': forms.EmailInput(attrs={'class': 'form-control'}),
}

# ✅ GOOD
from .widgets import BootstrapTextInput, BootstrapEmailInput
widgets = {
    'name': BootstrapTextInput(),
    'email': BootstrapEmailInput(),
}
```

### ❌ 6. Business Logic in Views

```python
# ❌ BAD
def view(request):
    # 100 lines of complex logic
    pass

# ✅ GOOD
def view(request):
    service = MyService(request.data)
    result = service.process()
    return render(request, 'template.html', {'result': result})
```

### ❌ 7. No Pagination

```python
# ❌ BAD
predictions = Prediction.objects.all()  # Could be thousands!

# ✅ GOOD
from django.core.paginator import Paginator
paginator = Paginator(Prediction.objects.all(), 25)
page_obj = paginator.get_page(request.GET.get('page'))
```

---

## Integration with Existing Skills

This skill **extends and consolidates** the following existing skills:

- **django-module-creation**: Adds concrete patterns for models, managers, services
- **component-reusability**: Adds widget library, template tags, form mixins
- **code-quality-standards**: Adds testing patterns, factories, fixtures
- **performance-optimization**: Adds query patterns, optimization examples
- **security-best-practices**: References for input validation, error handling
- **user-role-permissions**: References for permission patterns

**Cross-References:**
- See `user-role-permissions` skill for RBAC implementation details
- See `security-best-practices` skill for OWASP Top 10 protection
- See `performance-optimization` skill for caching and ML inference
- See `standard-folder-structure` skill for file organization

---

## Implementation Checklist

When implementing a new feature, ensure:

- [ ] Constants defined in `constants.py`
- [ ] Utilities organized in `utils.py`
- [ ] Custom exceptions in `exceptions.py`
- [ ] Models inherit from abstract bases (TimeStampedModel, etc.)
- [ ] Custom managers and querysets for complex queries
- [ ] Reusable form widgets from widget library
- [ ] Template tags for common UI patterns
- [ ] Centralized decorators for permissions
- [ ] Comprehensive logging with structured data
- [ ] Test factories for easy test data creation
- [ ] Query optimization with select_related/prefetch_related
- [ ] API responses use standard format
- [ ] File uploads use secure validation
- [ ] Background tasks for long-running operations
- [ ] Pagination for list views

---

## Summary

This skill provides a **comprehensive framework** for building maintainable, efficient, and consistent Django applications by:

1. **Centralizing** common patterns (constants, utilities, decorators)
2. **Eliminating** code duplication (abstract models, widget library)
3. **Standardizing** cross-cutting concerns (error handling, logging, validation)
4. **Optimizing** performance (query patterns, caching)
5. **Ensuring** security (file validation, permission checking)
6. **Facilitating** testing (factories, fixtures, mixins)

**Result:** Maximum code reuse, DRY compliance, consistency, and efficiency across the entire full-stack application.

---

## Section 16: Performance Optimization & Database Tuning

**Ensures optimal performance for database queries, ML inference, and caching**

### Core Performance Principles

1. **Measure First**: Profile before optimizing
2. **N+1 Queries**: Avoid with select_related/prefetch_related
3. **Caching**: Cache expensive operations
4. **Lazy Loading**: Load data only when needed
5. **Pagination**: Never load unlimited data
6. **Indexes**: Add indexes for filtered/ordered fields

### Database Query Optimization

**Avoid N+1 Queries:**

```python
# ❌ BAD: N+1 query problem
predictions = Prediction.objects.all()
for pred in predictions:
    print(pred.xray.patient.user.username)  # New query each iteration!

# ✅ GOOD: Use select_related for ForeignKey/OneToOne
predictions = Prediction.objects.select_related(
    'xray__patient__user'
).all()
for pred in predictions:
    print(pred.xray.patient.user.username)  # No additional queries!

# ✅ GOOD: Use prefetch_related for ManyToMany/Reverse FK
patients = Patient.objects.prefetch_related('xrays__predictions').all()
for patient in patients:
    for xray in patient.xrays.all():  # Prefetched!
        for pred in xray.predictions.all():  # Prefetched!
            print(pred.final_diagnosis)
```

**Query Optimization Patterns:**

```python
# QuerySet Optimization
class PredictionListView(ListView):
    def get_queryset(self):
        return Prediction.objects.select_related(
            'xray__patient__user',
            'reviewed_by'
        ).prefetch_related(
            'xray__predictions'
        ).only(  # Load only needed fields
            'id',
            'final_diagnosis',
            'consensus_confidence',
            'created_at',
            'is_validated',
            'xray__patient__user__username'
        )

# Use .values() for large datasets (if you don't need model instances)
stats = Prediction.objects.values('final_diagnosis').annotate(
    count=Count('id'),
    avg_confidence=Avg('consensus_confidence')
)

# Use .exists() instead of .count() for boolean checks
# ❌ BAD
if Prediction.objects.filter(is_validated=False).count() > 0:
    pass

# ✅ GOOD
if Prediction.objects.filter(is_validated=False).exists():
    pass

# Use .iterator() for very large querysets (streaming)
for prediction in Prediction.objects.iterator(chunk_size=100):
    # Process one at a time without loading all into memory
    process_prediction(prediction)
```

**Database Indexes:**

```python
# models.py
class Prediction(TimeStampedModel):
    # ... fields ...

    class Meta:
        indexes = [
            # Index frequently filtered fields
            models.Index(fields=['-created_at']),
            models.Index(fields=['final_diagnosis']),
            models.Index(fields=['is_validated']),
            # Compound index for common filter combinations
            models.Index(fields=['final_diagnosis', '-created_at']),
            models.Index(fields=['is_validated', '-created_at']),
        ]
```

### Caching Strategies

**Django Cache Framework:**

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'TIMEOUT': 300,  # 5 minutes default
    }
}

# For development (memory cache)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
```

**View-Level Caching:**

```python
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

# Cache view for 15 minutes
@method_decorator(cache_page(60 * 15), name='dispatch')
class PredictionStatsView(View):
    def get(self, request):
        # Expensive aggregation query
        stats = Prediction.objects.aggregate(
            total=Count('id'),
            covid_cases=Count('id', filter=Q(final_diagnosis='COVID')),
            avg_confidence=Avg('consensus_confidence')
        )
        return JsonResponse(stats)
```

**Low-Level Caching:**

```python
from django.core.cache import cache

class StatisticsService:
    @staticmethod
    def get_statistics() -> dict:
        """Get prediction statistics with caching"""
        cache_key = 'prediction_statistics'
        stats = cache.get(cache_key)

        if stats is None:
            # Expensive query
            stats = Prediction.objects.aggregate(
                total=Count('id'),
                covid_cases=Count('id', filter=Q(final_diagnosis='COVID')),
                avg_confidence=Avg('consensus_confidence')
            )
            # Cache for 5 minutes
            cache.set(cache_key, stats, 300)

        return stats

    @staticmethod
    def invalidate_statistics_cache():
        """Call this when creating new predictions"""
        cache.delete('prediction_statistics')

# In save/create methods
def create_prediction(xray):
    prediction = Prediction.objects.create(...)
    StatisticsService.invalidate_statistics_cache()  # Clear cache
    return prediction
```

**Template Fragment Caching:**

```django
{% load cache %}

{% cache 900 sidebar request.user.id %}
    <!-- Expensive sidebar rendering -->
    <div class="sidebar">
        {% for item in navigation_items %}
            ...
        {% endfor %}
    </div>
{% endcache %}
```

### ML Inference Optimization (RTX 4060 8GB VRAM)

**Memory Management:**

```python
# ml_engine.py
import torch
import gc

class ModelEnsemble:
    def predict_all_models(self, image_path: str) -> dict:
        """
        Predict with all models sequentially to manage VRAM.
        Optimized for RTX 4060 8GB.
        """
        results = {}

        # Load and predict one model at a time
        for model_name in self.model_names:
            # 1. Load model
            model = self.load_model(model_name)

            # 2. Run prediction
            with torch.no_grad():  # Disable gradient computation
                with torch.cuda.amp.autocast():  # Mixed precision
                    result = self.predict_single(model, image_path)

            results[model_name] = result

            # 3. Unload model and free VRAM
            del model
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()

        return results

    @torch.no_grad()  # Decorator for inference
    def predict_single(self, model, image_path: str):
        """Single model prediction"""
        # Process image
        image = self.preprocess(image_path)

        # Move to GPU
        image = image.to(self.device)

        # Predict
        output = model(image)

        # Move back to CPU immediately
        output = output.cpu()

        return self.postprocess(output)
```

**Image Preprocessing with Caching:**

```python
from functools import lru_cache
import cv2

@lru_cache(maxsize=100)  # Cache processed images
def apply_clahe(image_path: str, output_path: str = None) -> str:
    """
    Apply CLAHE with caching for frequently accessed images.
    """
    # Load image
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Apply CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(img)

    # Save
    if output_path is None:
        output_path = image_path.replace('.jpg', '_clahe.jpg')

    cv2.imwrite(output_path, enhanced, [cv2.IMWRITE_JPEG_QUALITY, 95])

    return output_path

# Clear cache when needed
def clear_preprocessing_cache():
    apply_clahe.cache_clear()
```

### Pagination (Always Required)

```python
# views.py
from django.core.paginator import Paginator

class PredictionListView(ListView):
    model = Prediction
    paginate_by = 25  # Always paginate!
    template_name = 'detection/prediction_list.html'

    def get_queryset(self):
        return Prediction.objects.select_related(
            'xray__patient__user'
        ).order_by('-created_at')
```

### Template Optimization

**Minimize Database Queries in Templates:**

```django
<!-- ❌ BAD: Query in template -->
{% for prediction in predictions %}
    <p>{{ prediction.xray.patient.user.username }}</p>  <!-- N+1 query! -->
{% endfor %}

<!-- ✅ GOOD: Prefetch in view -->
<!-- predictions = Prediction.objects.select_related('xray__patient__user') -->
{% for prediction in predictions %}
    <p>{{ prediction.xray.patient.user.username }}</p>  <!-- No query! -->
{% endfor %}
```

### Performance Monitoring

**Custom Profiling Decorator:**

```python
# common/utils.py
import time
import functools
import logging

logger = logging.getLogger(__name__)

def profile_execution_time(func):
    """Decorator to profile function execution time"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time

        logger.info(
            f"{func.__name__} executed in {execution_time:.4f} seconds"
        )

        return result
    return wrapper

# Usage
@profile_execution_time
def create_prediction(xray):
    # ... prediction logic
    pass
```

### Performance Checklist

**Before completing any feature:**

- ✅ Database queries optimized (no N+1)
- ✅ Proper indexes on filtered/ordered fields
- ✅ select_related/prefetch_related used
- ✅ Expensive operations cached
- ✅ Large querysets paginated
- ✅ ML inference uses CUDA efficiently
- ✅ Memory cleared after each prediction
- ✅ Images optimized (compressed, proper size)
- ✅ No database queries in templates
- ✅ Template fragments cached where appropriate

### Performance Targets

**For RTX 4060 8GB system:**

- **Single prediction**: < 10 seconds (all 6 models)
- **Page load**: < 2 seconds (with caching)
- **Database query**: < 100ms (with proper indexes)
- **VRAM usage**: < 8GB (sequential loading)
- **Pagination**: 25-50 items per page max

---

**Last Updated:** 2025-11-24
**Version:** 2.0.0 (includes Performance Optimization)
**Status:** Active
**Includes:** 16 comprehensive sections covering full-stack patterns + performance optimization
