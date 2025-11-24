---
name: Foundation Components & Structure
description: Enforces use of centralized foundation components (common/ app) and standard folder structure for maximum code reuse, DRY compliance, and UI consistency. Auto-applies when creating forms, models, templates, organizing files, or any module code.
---

# Foundation Components

**Version:** 1.0.0
**Last Updated:** 2025-11-23
**Status:** ⭐ CRITICAL - Must be used by ALL modules
**Auto-apply:** YES - Every time you write models, forms, templates, or module code

---

## Purpose

This skill ensures that ALL modules use the centralized foundation components instead of creating custom implementations. The foundation components eliminate code duplication, ensure consistency, and provide a single source of truth for common patterns.

**Foundation App Location:** `common/`

**Result:** 20-30% code reduction, 100% UI consistency, zero hardcoded Bootstrap classes

---

## When This Skill Auto-Triggers

**ALWAYS apply when:**
- Creating any new Django model
- Creating any Django form
- Writing any template
- Adding validation logic
- Implementing file uploads
- Formatting dates or data
- Creating UI components
- Writing permission checks
- Organizing module structure

**Critical Rule:** If you're about to write code that might exist elsewhere, CHECK `common/` FIRST.

---

## Foundation Components Library

### 1. Abstract Base Models (`common/models.py`)

**MANDATORY for ALL models** - Never create manual timestamp fields

#### Available Base Models

| Base Model | Fields Added | When to Use | Import |
|------------|--------------|-------------|--------|
| `TimeStampedModel` | `created_at`, `updated_at`, ordering | **ALL models** (minimum requirement) | `from common.models import TimeStampedModel` |
| `SoftDeleteModel` | `is_deleted`, `deleted_at`, `deleted_by` + `ActiveManager` | Models needing soft delete | `from common.models import SoftDeleteModel` |
| `AuditableModel` | `created_by`, `updated_by` | Models needing user tracking | `from common.models import AuditableModel` |
| `FullAuditModel` | All above fields combined | Medical records, sensitive data | `from common.models import FullAuditModel` |

#### Usage Examples

**✅ CORRECT:**
```python
from common.models import TimeStampedModel

class Announcement(TimeStampedModel):  # ✅ Inherits timestamps automatically
    """
    Automatically gets:
    - created_at (auto-set on creation)
    - updated_at (auto-updated on save)
    - Meta.ordering = ['-created_at']
    """
    title = models.CharField(max_length=200)
    message = models.TextField()
    # NO timestamp fields needed - inherited from base!
```

**❌ WRONG:**
```python
class Announcement(models.Model):  # ❌ Don't do this!
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # ❌ Manual timestamps
    updated_at = models.DateTimeField(auto_now=True)      # ❌ Duplication

    class Meta:
        ordering = ['-created_at']  # ❌ Manual ordering
```

**Code Savings:** 7-10 lines per model

---

### 2. Bootstrap Widget Library (`common/widgets.py`)

**MANDATORY for ALL forms** - Never hardcode `attrs={'class': 'form-control'}`

#### Available Widgets

| Widget | Bootstrap Class | Usage | Import |
|--------|----------------|-------|--------|
| `BootstrapTextInput` | `form-control` | Name, address, text fields | `from common.widgets import BootstrapTextInput` |
| `BootstrapEmailInput` | `form-control` + email validation | Email fields | `from common.widgets import BootstrapEmailInput` |
| `BootstrapPasswordInput` | `form-control` | Password fields | `from common.widgets import BootstrapPasswordInput` |
| `BootstrapTextarea` | `form-control` | Long text, descriptions | `from common.widgets import BootstrapTextarea` |
| `BootstrapSelect` | `form-select` | Dropdowns, choice fields | `from common.widgets import BootstrapSelect` |
| `BootstrapCheckboxInput` | `form-check-input` | Boolean fields | `from common.widgets import BootstrapCheckboxInput` |
| `BootstrapRadioSelect` | `form-check` | Radio buttons | `from common.widgets import BootstrapRadioSelect` |
| `BootstrapDateInput` | `form-control` + type=date | Date fields | `from common.widgets import BootstrapDateInput` |
| `BootstrapDateTimeInput` | `form-control` + type=datetime-local | DateTime fields | `from common.widgets import BootstrapDateTimeInput` |
| `BootstrapFileInput` | `form-control` | File/image uploads | `from common.widgets import BootstrapFileInput` |

#### Usage Examples

**✅ CORRECT:**
```python
from common.widgets import (
    BootstrapTextInput,
    BootstrapTextarea,
    BootstrapSelect,
    BootstrapDateTimeInput
)

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'message', 'priority', 'expires_at']
        widgets = {
            'title': BootstrapTextInput(attrs={'placeholder': 'Enter title'}),  # ✅ Widget
            'message': BootstrapTextarea(attrs={'rows': 5}),                     # ✅ Widget
            'priority': BootstrapSelect(),                                        # ✅ Widget
            'expires_at': BootstrapDateTimeInput(),                               # ✅ Widget
        }
    # Bootstrap classes applied automatically!
```

**❌ WRONG:**
```python
class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'message', 'priority', 'expires_at']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',           # ❌ Hardcoded Bootstrap class
                'placeholder': 'Enter title',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',           # ❌ Hardcoded Bootstrap class
                'rows': 5,
            }),
            # ... more hardcoded classes ...     # ❌ NOT DRY!
        }
```

**Code Savings:** 3-5 lines per field, zero hardcoded classes

**Benefit:** Change Bootstrap styling project-wide by editing one file (`common/widgets.py`)

---

### 3. Template Tags & Filters (`common/templatetags/common_tags.py`)

**MANDATORY in ALL templates** - Always `{% load common_tags %}`

#### Available Tags & Filters

| Tag/Filter | Purpose | Example Usage | Output |
|------------|---------|---------------|--------|
| `{% status_badge status %}` | Render color-coded badge | `{% status_badge "pending" %}` | <span class="badge bg-warning">Pending</span> |
| `{% diagnosis_badge diagnosis %}` | Diagnosis badge with icon | `{% status_badge "COVID" %}` | <span class="badge bg-danger">🦠 COVID</span> |
| `{% format_datetime dt %}` | Consistent datetime format | `{% format_datetime announcement.created_at %}` | "22 Nov 2025, 2:30 PM" |
| `{% format_date date %}` | Consistent date format | `{% format_date patient.dob %}` | "22 Nov 2000" |
| `{% time_since dt %}` | Human-readable time | `{% time_since appointment.created_at %}` | "2 hours ago" |
| `{% render_pagination page_obj %}` | Full pagination UI | `{% render_pagination predictions %}` | Complete pagination HTML |

#### Usage Examples

**✅ CORRECT:**
```django
{% extends "base.html" %}
{% load common_tags %}  {# ✅ ALWAYS load this first #}

{% block content %}
<div class="container">
    {% for announcement in announcements %}
        <div class="card mb-3">
            <div class="card-body">
                <h5>{{ announcement.title }}</h5>

                {# ✅ Use template tag for badge #}
                {% status_badge announcement.priority %}

                {# ✅ Use template tag for datetime #}
                <p class="text-muted">
                    Posted: {% format_datetime announcement.created_at %}
                </p>
            </div>
        </div>
    {% endfor %}

    {# ✅ Use pagination tag #}
    {% if page_obj.has_other_pages %}
        {% render_pagination page_obj %}
    {% endif %}
</div>
{% endblock %}
```

**❌ WRONG:**
```django
{% extends "base.html" %}
{# ❌ Forgot to load common_tags #}

{% block content %}
<div class="container">
    {% for announcement in announcements %}
        <div class="card mb-3">
            <div class="card-body">
                <h5>{{ announcement.title }}</h5>

                {# ❌ Manual badge HTML - NOT DRY! #}
                <span class="badge bg-{{ announcement.get_priority_class }}">
                    {{ announcement.get_priority_display }}
                </span>

                {# ❌ Manual date formatting - Inconsistent! #}
                <p class="text-muted">
                    Posted: {{ announcement.created_at|date:"d M Y, g:i A" }}
                </p>
            </div>
        </div>
    {% endfor %}

    {# ❌ Manual pagination HTML - Duplicated! #}
    <nav>
        <ul class="pagination">
            <!-- 20 lines of duplicated pagination HTML -->
        </ul>
    </nav>
</div>
{% endblock %}
```

**Benefit:** Consistent formatting project-wide, change format once applies everywhere

---

### 4. Reusable Template Components (`templates/components/`)

**MANDATORY for ALL templates** - Use `{% include %}` instead of duplicating HTML

#### Available Components

| Component | File | Usage | Parameters |
|-----------|------|-------|------------|
| Card | `components/card.html` | Container with header/body | `title`, `title_icon` (optional) |
| Alert | `components/alert.html` | Message display | `message`, `type` (success/info/warning/danger), `dismissible` |
| Loading Spinner | `components/loading_spinner.html` | Loading indicator | `text` (optional message) |
| Pagination | `components/pagination.html` | Use `{% render_pagination %}` tag instead | N/A (use tag) |

#### Usage Examples

**✅ CORRECT:**
```django
{% extends "base.html" %}

{% block content %}
{# ✅ Use alert component for messages #}
{% if messages %}
    {% for message in messages %}
        {% include 'components/alert.html' with message=message type=message.tags dismissible=True %}
    {% endfor %}
{% endif %}

{# ✅ Use card component for content #}
{% include 'components/card.html' with title="Announcements" title_icon="megaphone" %}
    {% block card_body %}
        <p>Your content here...</p>
    {% endblock %}
{% endinclude %}

{# ✅ Use loading spinner component #}
<div id="loading" style="display:none;">
    {% include 'components/loading_spinner.html' with text="Processing..." %}
</div>
{% endblock %}
```

**❌ WRONG:**
```django
{% extends "base.html" %}

{% block content %}
{# ❌ Manual alert HTML - Duplicated! #}
{% if messages %}
    {% for message in messages %}
        <div class="alert alert-{{ message.tags }} alert-dismissible fade show">
            {{ message }}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    {% endfor %}
{% endif %}

{# ❌ Manual card HTML - Duplicated! #}
<div class="card mb-3">
    <div class="card-header bg-primary text-white">
        <h5 class="card-title mb-0">
            <i class="bi bi-megaphone"></i> Announcements
        </h5>
    </div>
    <div class="card-body">
        <p>Your content here...</p>
    </div>
</div>
{# 20-30 lines of duplicated HTML every time! #}
{% endblock %}
```

**Code Savings:** 20-50 lines of HTML per page

**Benefit:** Update component design once, applies to ALL pages using it

---

### 5. Common Utilities (`common/utils.py`)

**MANDATORY for ALL validation/file operations** - Never reimplement these functions

#### Available Utilities

**Validation Functions:**
- `validate_phone(phone: str) -> None` - Malaysian phone validation (raises `ValidationError`)
- `validate_image_file(file, max_size_mb: int = 10) -> bool` - Image file validation
- `validate_nric(nric: str) -> bool` - Malaysian NRIC validation

**File Handling:**
- `sanitize_filename(filename: str) -> str` - Remove dangerous characters
- `generate_unique_filename(filename: str, prefix: str = '') -> str` - UUID-based unique names
- `format_file_size(size_bytes: int) -> str` - Human-readable file sizes

**Date/Time Utilities:**
- `calculate_age(date_of_birth: datetime) -> int` - Calculate age from DOB
- `time_since(dt: datetime) -> str` - Human-readable time difference

#### Usage Examples

**✅ CORRECT:**
```python
from common.utils import (
    validate_phone,
    validate_image_file,
    generate_unique_filename,
    calculate_age
)

class PatientForm(forms.ModelForm):
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        # ✅ Use utility function
        try:
            validate_phone(phone)
        except ValidationError:
            raise forms.ValidationError("Invalid Malaysian phone number.")
        return phone

    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image')
        # ✅ Use utility function
        if image and not validate_image_file(image, max_size_mb=5):
            raise forms.ValidationError("Invalid image or size exceeds 5MB.")
        return image

# File upload handling
def handle_xray_upload(file):
    # ✅ Use utility function
    unique_name = generate_unique_filename(file.name, prefix='xray')
    # Save with safe, unique name...
    return unique_name

# Calculate patient age
def get_patient_age(patient):
    # ✅ Use utility function
    return calculate_age(patient.date_of_birth)
```

**❌ WRONG:**
```python
import re
from uuid import uuid4

class PatientForm(forms.ModelForm):
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        # ❌ Manual validation - Duplicated logic!
        if not re.match(r'^(\+?6?01)[0-46-9]-*[0-9]{7,8}$', phone):
            raise forms.ValidationError("Invalid phone number.")
        return phone

    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image')
        # ❌ Manual validation - Duplicated logic!
        if image:
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("File too large.")
            if not image.name.endswith(('.jpg', '.png')):
                raise forms.ValidationError("Invalid file type.")
        return image

# ❌ Manual filename generation - Duplicated logic!
def handle_xray_upload(file):
    filename = f"xray_{uuid4()}_{file.name}"
    # Duplicated across multiple modules!
```

**Code Savings:** 10-30 lines per module

**Benefit:** Centralized validation rules, fix bug once applies everywhere

---

### 6. Permission Decorators (`reporting/decorators.py`)

**MANDATORY for ALL views** - Never write manual permission checks

#### Available Decorators

| Decorator | Permission Level | Usage |
|-----------|-----------------|-------|
| `@login_required` | Any authenticated user | All protected views (Django built-in) |
| `@staff_required` | Staff or admin only | Create/update operations |
| `@admin_required` | Admin only | User management, deletions |
| `@patient_owner_required` | Patient owns the resource | Patient self-service views |

#### Usage Examples

**✅ CORRECT:**
```python
from django.contrib.auth.decorators import login_required
from reporting.decorators import staff_required, admin_required

@login_required  # ✅ One line - any authenticated user
def announcement_list(request):
    """All authenticated users can view announcements."""
    announcements = Announcement.objects.filter(is_active=True)
    return render(request, 'announcements/announcement_list.html', {
        'announcements': announcements
    })

@staff_required  # ✅ One line - staff/admin only
def announcement_create(request):
    """Only staff and admin can create announcements."""
    # Permission automatically enforced
    # No manual checks needed!
    form = AnnouncementForm()
    return render(request, 'announcements/announcement_form.html', {'form': form})

@admin_required  # ✅ One line - admin only
def user_delete(request, user_id):
    """Only admin can delete users."""
    # Permission automatically enforced
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('user_list')
```

**❌ WRONG:**
```python
def announcement_list(request):
    # ❌ Manual authentication check - Duplicated!
    if not request.user.is_authenticated:
        return redirect('login')

    announcements = Announcement.objects.filter(is_active=True)
    return render(request, 'announcements/announcement_list.html', {
        'announcements': announcements
    })

def announcement_create(request):
    # ❌ Manual permission checks - Duplicated across ALL staff views!
    if not request.user.is_authenticated:
        messages.error(request, "Please login.")
        return redirect('login')

    if not request.user.profile.is_staff_or_admin():
        messages.error(request, "Permission denied.")
        return redirect('home')

    # 5-7 lines of boilerplate every time!
    form = AnnouncementForm()
    return render(request, 'announcements/announcement_form.html', {'form': form})
```

**Code Savings:** 5-7 lines per view

**Benefit:** Consistent permission enforcement, impossible to forget

---

## Foundation Components Checklist

**Before committing ANY module, verify:**

### Models ✅
- [ ] Inherits from `TimeStampedModel` (minimum) or other base models
- [ ] NO manual `created_at` or `updated_at` fields
- [ ] NO manual `Meta.ordering` for timestamps (inherited)
- [ ] Type hints on all methods
- [ ] Comprehensive docstrings

### Forms ✅
- [ ] Uses `common.widgets` for ALL form fields
- [ ] NO hardcoded `attrs={'class': 'form-control'}` anywhere
- [ ] Validation uses `common.utils` functions
- [ ] Help texts and labels defined
- [ ] Custom validation in `clean_*()` methods

### Views ✅
- [ ] Uses permission decorators (`@staff_required`, etc.)
- [ ] NO manual permission checking code
- [ ] Thin views (<50 lines per view)
- [ ] Type hints on function signatures
- [ ] Uses constants from `constants.py`

### Templates ✅
- [ ] Loads `{% load common_tags %}` at top
- [ ] Uses `{% include 'components/card.html' %}` for cards
- [ ] Uses `{% include 'components/alert.html' %}` for messages
- [ ] Uses `{% status_badge %}` for status badges
- [ ] Uses `{% format_datetime %}` for datetime formatting
- [ ] Uses `{% render_pagination %}` for pagination
- [ ] NO duplicated card/alert/pagination HTML

### Utilities ✅
- [ ] Phone validation uses `validate_phone()`
- [ ] Image validation uses `validate_image_file()`
- [ ] File naming uses `generate_unique_filename()`
- [ ] Age calculation uses `calculate_age()`
- [ ] NO reimplemented validation logic

### Constants ✅
- [ ] All magic strings in `constants.py`
- [ ] NO hardcoded status values in code
- [ ] NO hardcoded message strings in views
- [ ] Centralized and reusable

---

### 7. Reusable View Mixins (`reporting/decorators.py` & view mixins)

**RECOMMENDED for complex views** - Share functionality across class-based views

#### Available Mixins Pattern

While not in `common/`, you can create reusable view mixins following this pattern:

```python
# Example: Create mixins in your module
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect

class RoleRequiredMixin(LoginRequiredMixin):
    """Base mixin for role-based access"""
    required_role: str = None

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            messages.error(request, "User profile not found.")
            return redirect('home')

        if self.required_role and request.user.profile.role != self.required_role:
            messages.error(request, f"Access denied. {self.required_role.title()}s only.")
            return redirect('home')

        return super().dispatch(request, *args, **kwargs)


class PageTitleMixin:
    """Add page title to context"""
    page_title: str = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        return context


class FilterMixin:
    """Add filtering capability to list views"""
    filter_fields: list = []

    def get_queryset(self):
        qs = super().get_queryset()
        for field in self.filter_fields:
            value = self.request.GET.get(field)
            if value:
                qs = qs.filter(**{field: value})
        return qs


# Usage: Combine multiple mixins
from django.views.generic import ListView

class AnnouncementListView(PageTitleMixin, FilterMixin, ListView):
    model = Announcement
    page_title = "Announcements"
    filter_fields = ['priority', 'is_active']
    paginate_by = 10
```

**Benefit:** Reusable view behavior across multiple views

---

### 8. Additional Template Components (Examples)

Beyond the core components in `templates/components/`, here are patterns for module-specific components:

#### Empty State Component
```django
{# templates/components/empty_state.html #}
<div class="text-center py-5">
    <i class="bi bi-{{ icon|default:'inbox' }} display-1 text-muted"></i>
    <h4 class="mt-3">{{ title }}</h4>
    <p class="text-muted">{{ description }}</p>
    {% if action_url %}
    <a href="{{ action_url }}" class="btn btn-primary">
        <i class="bi bi-{{ action_icon|default:'plus' }}"></i> {{ action_text }}
    </a>
    {% endif %}
</div>

{# Usage #}
{% include 'components/empty_state.html' with
    icon="image"
    title="No X-rays uploaded yet"
    description="Upload an X-ray to get started"
    action_url="/detection/upload/"
    action_text="Upload X-Ray"
%}
```

#### Stats Card Component
```django
{# templates/components/stats_card.html #}
<div class="card text-center h-100">
    <div class="card-body">
        <i class="bi bi-{{ icon }} display-4 text-{{ color|default:'primary' }}"></i>
        <h3 class="mt-3">{{ value }}</h3>
        <p class="text-muted mb-0">{{ label }}</p>
    </div>
</div>

{# Usage in dashboard #}
<div class="row g-4">
    <div class="col-md-3">
        {% include 'components/stats_card.html' with
            icon="bar-chart"
            value=total_predictions
            label="Total Predictions"
            color="primary"
        %}
    </div>
</div>
```

**Benefit:** Consistent dashboard and empty state patterns

---

### 9. Template Tag Patterns

#### Additional Useful Template Tags

```python
# common/templatetags/common_tags.py (extend with these patterns)
from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag
def active_nav(request, url_name: str) -> str:
    """Return 'active' if current page matches url_name"""
    current_url = request.path
    target_url = reverse(url_name)
    return 'active' if current_url == target_url else ''


@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs) -> str:
    """
    Update URL query parameters while preserving existing ones.
    Useful for pagination with filters.

    Usage:
        <a href="?{% query_transform page=2 %}">Next</a>
    """
    query = context['request'].GET.copy()
    for k, v in kwargs.items():
        query[k] = v
    return query.urlencode()


# Usage in templates
{% load common_tags %}

<!-- Active navigation highlighting -->
<li class="nav-item">
    <a class="nav-link {% active_nav request 'announcement_list' %}"
       href="{% url 'announcement_list' %}">
        Announcements
    </a>
</li>

<!-- Pagination with query params -->
<a href="?{% query_transform page=page_obj.next_page_number %}">Next</a>
```

**Benefit:** Reusable navigation and pagination patterns

---

### 10. Component Reusability Checklist

When creating new features, ask yourself:

- ✅ Can this be a reusable component?
- ✅ Should this logic be in a mixin?
- ✅ Can this template be split into includes?
- ✅ Should this be a custom template tag?
- ✅ Is there an existing component I can reuse?
- ✅ Can this model inherit from a base class?
- ✅ Can this form widget be made generic?
- ✅ Is this business logic better in a service layer?
- ✅ Am I hardcoding Bootstrap classes? (Use widgets instead)
- ✅ Am I duplicating validation logic? (Use common.utils)

**Rule of thumb:** If you write the same code twice, make it reusable!

---

## Anti-Patterns to Avoid

### ❌ NEVER Do This

**1. Manual Timestamp Fields**
```python
# ❌ WRONG
class MyModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```
**✅ DO THIS:** `class MyModel(TimeStampedModel):`

**2. Hardcoded Bootstrap Classes**
```python
# ❌ WRONG
widgets = {
    'title': forms.TextInput(attrs={'class': 'form-control'})
}
```
**✅ DO THIS:** `'title': BootstrapTextInput()`

**3. Manual Permission Checks**
```python
# ❌ WRONG
def my_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.profile.is_staff_or_admin():
        return redirect('home')
```
**✅ DO THIS:** `@staff_required`

**4. Duplicated HTML Components**
```python
# ❌ WRONG
<div class="card">
    <div class="card-header">...</div>
    <div class="card-body">...</div>
</div>
```
**✅ DO THIS:** `{% include 'components/card.html' with title=... %}`

**5. Reimplemented Validation**
```python
# ❌ WRONG
if not re.match(r'^(\+?6?01)[0-46-9]-*[0-9]{7,8}$', phone):
    raise ValidationError("Invalid phone")
```
**✅ DO THIS:** `validate_phone(phone)`

---

## Code Reduction Metrics

**Real-world results from announcements module:**

| File | Without Foundation | With Foundation | Savings |
|------|-------------------|-----------------|---------|
| models.py | 110 lines | 100 lines | 10 lines (10%) |
| forms.py | 120 lines | 110 lines | 10 lines (8%) |
| views.py | 180 lines | 140 lines | 40 lines (22%) |
| Templates (3 files) | 250 lines | 180 lines | 70 lines (28%) |
| **Total** | **660 lines** | **530 lines** | **130 lines (20%)** |

**Hardcoded Values Eliminated:**
- ❌ **0** hardcoded Bootstrap classes
- ❌ **0** manual timestamp fields
- ❌ **0** duplicated permission checks
- ❌ **0** duplicated card/alert HTML
- ❌ **0** inconsistent date formats

**Result:** 100% DRY compliance

---

## Integration with Other Skills

This skill integrates with:
- **full-stack-django-patterns** - Comprehensive Django patterns framework
- **ui-design-system** - Widgets ensure consistent UI
- **code-quality-standards** - Reduces code, increases quality
- **module-creation-lifecycle** - Phase 3 quality checklist includes foundation verification
- **three-tier-architecture** - Service layer works with foundation models

---

## Reference Implementation

**See:** `announcements/` module for complete demonstration of all foundation components

**Documentation:**
- `.claude/ANNOUNCEMENTS_MODULE_DEMO.md` - Before/after comparisons
- `.claude/FOUNDATION_TEST_RESULTS.md` - Test verification results

---

## Enforcement

**This skill is CRITICAL and MANDATORY.**

When reviewing code, if you see:
- Manual timestamp fields → REFACTOR to use `TimeStampedModel`
- Hardcoded Bootstrap classes → REFACTOR to use widget library
- Manual permission checks → REFACTOR to use decorators
- Duplicated HTML → REFACTOR to use components
- Reimplemented validation → REFACTOR to use `common.utils`

**No exceptions.** Foundation components are the single source of truth.

---

## Part 7: Standard Folder Structure

**Enforces consistent folder structure across all Django modules**

### Project Root Structure

```
fyp-webapp/
├── config/                     # Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── static/                     # Static files
│   ├── css/
│   ├── js/
│   ├── images/
│   └── ml_models/              # ML model weights (.pth files)
│
├── media/                      # User-uploaded files
│   ├── xrays/
│   │   ├── original/
│   │   ├── processed/
│   │   └── heatmaps/
│   └── exports/
│
├── templates/                  # Global templates
│   ├── base.html
│   ├── home.html
│   ├── components/             # Reusable components
│   │   ├── card.html
│   │   ├── alert.html
│   │   ├── pagination.html
│   │   └── loading_spinner.html
│   └── registration/
│
├── common/                     # ⭐ Foundation components app
│   ├── models.py              # Abstract base models
│   ├── widgets.py             # Bootstrap widget library
│   ├── utils.py               # Common utilities
│   └── templatetags/
│       └── common_tags.py     # Template tags & filters
│
├── [module_name]/             # Django app (Standard Module Structure)
│   ├── __init__.py
│   ├── models.py              # Database models (inherit TimeStampedModel)
│   ├── views.py               # View classes (use CBVs)
│   ├── forms.py               # Form classes (use Bootstrap widgets)
│   ├── urls.py                # URL routing
│   ├── admin.py               # Admin configuration
│   ├── constants.py           # Module constants (MANDATORY)
│   ├── services.py            # Business logic layer (if complex)
│   ├── managers.py            # Custom model managers
│   ├── validators.py          # Custom validators
│   ├── signals.py             # Django signals
│   ├── apps.py                # App configuration
│   │
│   ├── templates/             # Module templates
│   │   └── [module_name]/
│   │       └── *.html
│   │
│   ├── static/                # Module static files (optional)
│   │   └── [module_name]/
│   │       ├── css/
│   │       └── js/
│   │
│   ├── migrations/            # Database migrations
│   │   └── 0001_initial.py
│   │
│   └── tests/                 # Module tests (MANDATORY)
│       ├── __init__.py
│       ├── test_models.py
│       ├── test_views.py
│       ├── test_forms.py
│       ├── test_services.py
│       └── factories.py
│
├── tests/                     # Project-wide tests
├── docs/                      # Documentation
├── .claude/                   # Claude Code configuration
│   └── skills/
├── requirements.txt
├── manage.py
├── pytest.ini
└── README.md
```

### Standard Module Structure Template

**When creating a new module, use this structure:**

```
[module_name]/
├── __init__.py
├── models.py              # Fat models - inherit TimeStampedModel
├── views.py               # Thin views - use CBVs
├── forms.py               # Use Bootstrap widgets from common/
├── urls.py                # URL patterns
├── admin.py               # Admin interface
├── constants.py           # ⭐ MANDATORY - All magic strings/values here
├── services.py            # Service layer (for complex workflows only)
├── managers.py            # Custom querysets (optional)
├── validators.py          # Custom field validators (optional)
├── signals.py             # Signal handlers (optional)
├── apps.py                # App configuration
│
├── templates/
│   └── [module_name]/
│       └── *.html         # Use {% load common_tags %}
│
├── static/                # Optional - only if module-specific assets needed
│   └── [module_name]/
│       ├── css/
│       └── js/
│
├── migrations/
│   └── 0001_initial.py
│
└── tests/                 # ⭐ MANDATORY
    ├── __init__.py
    ├── test_models.py
    ├── test_views.py
    ├── test_forms.py
    ├── test_services.py  # If services/ exists
    └── factories.py
```

### File Organization Rules

**1. Models (models.py)**
- Inherit from `TimeStampedModel` (minimum) or other base models
- Related models in same file
- Maximum 500 lines per file; split if larger

**2. Views (views.py)**
- Use class-based views (CBVs)
- Thin views (<50 lines per view)
- Maximum 500 lines; create `views/` package if needed

**3. Forms (forms.py)**
- Use Bootstrap widgets from `common/widgets.py`
- One form per class
- No hardcoded Bootstrap classes

**4. Constants (constants.py)**
- ⭐ MANDATORY for all modules
- Centralize all magic strings, choices, limits
- Example:
  ```python
  # MANDATORY constants.py
  PRIORITY_CHOICES = [
      ('high', 'High'),
      ('medium', 'Medium'),
      ('low', 'Low'),
  ]

  MAX_TITLE_LENGTH = 200
  DEFAULT_EXPIRY_DAYS = 30
  ```

**5. Services (services.py)**
- Only create if complex multi-step workflows exist
- Don't create for simple CRUD operations
- Framework-agnostic business logic

**6. Templates**
- Always `{% load common_tags %}` at top
- Use `{% include 'components/card.html' %}` for reusable UI
- Never exceed 300 lines per template

**7. Tests**
- ⭐ MANDATORY for all modules
- One test file per module file
- Use factories for test data
- Aim for 80%+ coverage

### Naming Conventions

**Files:**
- `snake_case.py` for Python files
- `kebab-case.html` for templates
- `kebab-case.css/js` for assets

**Directories:**
- `snake_case/` for Python packages

**Templates:**
- `list.html` - List view
- `detail.html` - Detail view
- `create.html` - Create form
- `update.html` - Update form
- `delete.html` - Delete confirmation

### When to Split Files

**Create package structure when:**
- File exceeds 500 lines
- Module has > 5 models/views/forms
- Logic becomes complex

**Example - Split views.py:**
```
views/
├── __init__.py
├── dashboard.py
├── upload.py
└── results.py
```

### Folder Structure Checklist

**Before creating a new module:**
- ✅ Plan folder structure
- ✅ Create `constants.py` (MANDATORY)
- ✅ Create `tests/` directory (MANDATORY)
- ✅ Add `__init__.py` to make packages
- ✅ Add module to `INSTALLED_APPS`
- ✅ Use `TimeStampedModel` for all models
- ✅ Use Bootstrap widgets for all forms
- ✅ Load `common_tags` in all templates

**Before committing:**
- ✅ No file exceeds 500 lines
- ✅ Related code is grouped together
- ✅ Imports organized (stdlib, Django, third-party, local)
- ✅ Templates use `{% load common_tags %}`
- ✅ Tests mirror source structure
- ✅ All directories have `__init__.py`
- ✅ No hardcoded Bootstrap classes in forms
- ✅ No manual timestamp fields in models

---

**Last Updated:** 2025-11-24
**Status:** ⭐ CRITICAL
**Coverage:** 100% of all modules must use foundation components AND standard structure
**Code Reduction:** 20-30% proven in production
**Includes:** Foundation components + folder structure enforcement

**Foundation components + standard structure are the cornerstone of code quality, consistency, and maintainability in this project.**
