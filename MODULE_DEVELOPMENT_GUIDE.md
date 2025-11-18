# Module Development Guide
## COVID-19 Detection Web Application

**Version:** 1.0
**Last Updated:** 2025-11-18
**Purpose:** Comprehensive guide for creating, extending, and maintaining modules across multiple development sessions

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Module Architecture](#module-architecture)
3. [Creating New Modules](#creating-new-modules)
4. [Module Templates](#module-templates)
5. [Extension Guidelines](#extension-guidelines)
6. [Validation Checklist](#validation-checklist)
7. [Session Handoff](#session-handoff)

---

## 🎯 Project Overview

### Current State

**Project:** COVID-19 Detection System using Django + AI
**Purpose:** Multi-model COVID-19 detection from chest X-rays
**Tech Stack:** Django 4.2.7, Bootstrap 5, PyTorch (RTX 4060 8GB)

### Existing Modules

| Module | Purpose | Status | Dependencies |
|--------|---------|--------|--------------|
| **config** | Main project settings | ✅ Complete | - |
| **accounts** | User authentication | ✅ Complete | Django auth |
| **detection** | COVID-19 detection core | ✅ Complete | All other modules |
| **dashboards** | Role-based dashboards | 🚧 Stub | detection, accounts |

### Spotlight Features

1. **Multi-Model Comparison** (Spotlight #1)
   - Location: `detection/ml_engine.py`, `detection/views.py`
   - Status: ✅ Framework complete (stub mode)

2. **Explainable AI** (Spotlight #2)
   - Location: `detection/explainability.py`
   - Status: ✅ Framework complete (stub mode)

---

## 🏗️ Module Architecture

### Standard Django App Structure

```
app_name/
├── __init__.py
├── models.py              # Database models (inherit from BaseModel)
├── views.py               # Class-based views with mixins
├── urls.py                # URL routing
├── forms.py               # Form definitions with Bootstrap widgets
├── admin.py               # Admin panel configuration
├── services.py            # Business logic (service layer)
├── mixins.py              # Reusable view mixins
├── managers.py            # Custom model managers
├── validators.py          # Custom field validators
├── signals.py             # Django signals
├── apps.py                # App configuration
├── templatetags/          # Custom template tags
│   ├── __init__.py
│   └── app_tags.py
├── templates/app_name/    # App-specific templates
│   ├── components/        # Reusable components
│   └── pages/             # Full page templates
├── static/app_name/       # App-specific static files
│   ├── css/
│   ├── js/
│   └── images/
└── tests/                 # Test suite
    ├── __init__.py
    ├── test_models.py
    ├── test_views.py
    ├── test_forms.py
    ├── test_services.py
    └── factories.py       # Test factories
```

### Module Communication Pattern

```
User Request
    ↓
URL Router (urls.py)
    ↓
View (views.py) ← Mixins (mixins.py)
    ↓
Service Layer (services.py) ← Business Logic
    ↓
Model Layer (models.py) ← Managers (managers.py)
    ↓
Database
```

### Reusable Components

All modules must use:
- **Base Models:** `TimeStampedModel`, `UserTrackingModel`
- **View Mixins:** `RoleRequiredMixin`, `PageTitleMixin`, `FilterMixin`
- **Template Components:** Cards, badges, tables, pagination
- **Form Widgets:** Bootstrap-styled inputs
- **Template Tags:** Diagnosis badges, confidence colors, etc.

---

## 🆕 Creating New Modules

### Step-by-Step Process

#### 1. Planning Phase

**Before writing code, document:**

```markdown
# Module Name: [e.g., Reporting]

## Purpose
What problem does this module solve?

## User Stories
- As a [doctor/patient/admin], I want to [action] so that [benefit]

## Models Required
- ReportTemplate (fields: name, content, type)
- GeneratedReport (fields: report, patient, created_by)

## Views/Pages
- Report list
- Report detail
- Report generation form

## Permissions
- Doctors: Can create/view all reports
- Patients: Can view own reports
- Admin: Full access

## Dependencies
- detection (for predictions)
- accounts (for user auth)

## Integration Points
- Add "Generate Report" button to prediction detail page
- Add reports section to patient dashboard
```

#### 2. Create Module Structure

```bash
# Create Django app
python manage.py startapp module_name

# Create required directories
mkdir -p module_name/templates/module_name/{components,pages}
mkdir -p module_name/static/module_name/{css,js,images}
mkdir -p module_name/templatetags
mkdir -p module_name/tests
```

#### 3. Configure Settings

```python
# config/settings.py
INSTALLED_APPS = [
    # ...
    'module_name',  # Add new module
]
```

#### 4. Create Base Files

**models.py** - Start with base models:
```python
from django.db import models
from detection.models import TimeStampedModel, UserTrackingModel

class ModuleModel(TimeStampedModel):
    """
    Description of what this model represents.

    Attributes:
        field_name: Description
    """
    # Fields here

    class Meta:
        verbose_name = "Module Model"
        verbose_name_plural = "Module Models"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
        ]

    def __str__(self) -> str:
        return f"{self.field_name}"
```

**services.py** - Business logic:
```python
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)


class ModuleService:
    """
    Service layer for module business logic.

    Separates business logic from views for:
    - Testability
    - Reusability
    - Maintainability
    """

    @staticmethod
    def create_something(data: dict) -> ModelClass:
        """
        Create something with validation.

        Args:
            data: Dictionary with required fields

        Returns:
            Created model instance

        Raises:
            ValueError: If data is invalid
        """
        # Validation
        if not data.get('required_field'):
            raise ValueError("Required field missing")

        # Business logic
        instance = ModelClass.objects.create(**data)

        logger.info(f"Created {instance}")
        return instance
```

**views.py** - Class-based views:
```python
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from detection.mixins import DoctorRequiredMixin, PageTitleMixin

class ModuleListView(DoctorRequiredMixin, PageTitleMixin, ListView):
    """
    List view for module items.

    Features:
    - Pagination (25 per page)
    - Filtering
    - Optimized queries
    """
    model = ModuleModel
    template_name = 'module_name/pages/list.html'
    context_object_name = 'items'
    paginate_by = 25
    page_title = "Module List"

    def get_queryset(self):
        """Optimize and filter queryset"""
        return ModuleModel.objects.select_related('user').all()
```

**urls.py** - URL patterns:
```python
from django.urls import path
from . import views

app_name = 'module_name'

urlpatterns = [
    path('', views.ModuleListView.as_view(), name='list'),
    path('<int:pk>/', views.ModuleDetailView.as_view(), name='detail'),
    path('create/', views.ModuleCreateView.as_view(), name='create'),
]
```

**forms.py** - Forms with validation:
```python
from django import forms
from .models import ModuleModel
from detection.widgets import BootstrapTextInput, BootstrapSelect

class ModuleForm(forms.ModelForm):
    """
    Form for creating/editing module items.
    """
    class Meta:
        model = ModuleModel
        fields = ['field1', 'field2']
        widgets = {
            'field1': BootstrapTextInput(),
            'field2': BootstrapSelect(),
        }

    def clean_field1(self):
        """Validate field1"""
        value = self.cleaned_data.get('field1')
        # Validation logic
        return value
```

**admin.py** - Admin configuration:
```python
from django.contrib import admin
from .models import ModuleModel

@admin.register(ModuleModel)
class ModuleModelAdmin(admin.ModelAdmin):
    """Admin interface for ModuleModel"""
    list_display = ['field1', 'field2', 'created_at']
    list_filter = ['created_at', 'field2']
    search_fields = ['field1']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
```

#### 5. Create Templates

**Base template** (`templates/module_name/base.html`):
```django
{% extends 'base.html' %}

{% block content %}
<div class="row mb-4">
    <div class="col">
        <h2><i class="bi bi-icon"></i> {% block page_title %}Module{% endblock %}</h2>
        {% block page_description %}{% endblock %}
    </div>
</div>

{% block module_content %}{% endblock %}
{% endblock %}
```

**List template** (`templates/module_name/pages/list.html`):
```django
{% extends 'module_name/base.html' %}

{% block page_title %}{{ page_title }}{% endblock %}

{% block module_content %}
<div class="card">
    <div class="card-body">
        {% if items %}
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead class="table-light">
                        <tr>
                            <th>Field 1</th>
                            <th>Field 2</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for item in items %}
                        <tr>
                            <td>{{ item.field1 }}</td>
                            <td>{{ item.field2 }}</td>
                            <td>
                                <a href="{% url 'module_name:detail' item.pk %}"
                                   class="btn btn-sm btn-outline-primary">
                                    <i class="bi bi-eye"></i> View
                                </a>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>

            {% include 'components/pagination.html' %}
        {% else %}
            {% include 'components/empty_state.html' with
                icon="inbox"
                title="No items yet"
                description="Create your first item to get started"
                action_url="{% url 'module_name:create' %}"
                action_text="Create Item"
            %}
        {% endif %}
    </div>
</div>
{% endblock %}
```

#### 6. Create Tests

```python
# tests/test_models.py
from django.test import TestCase
from module_name.models import ModuleModel

class ModuleModelTest(TestCase):
    """Test ModuleModel"""

    def setUp(self):
        """Set up test data"""
        self.item = ModuleModel.objects.create(
            field1="Test",
            field2="Value"
        )

    def test_str_representation(self):
        """Test __str__ method"""
        self.assertEqual(str(self.item), "Test")

    def test_creation(self):
        """Test model creation"""
        self.assertIsNotNone(self.item.id)
        self.assertEqual(self.item.field1, "Test")


# tests/test_views.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class ModuleViewsTest(TestCase):
    """Test module views"""

    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.user = User.objects.create_user('test', 'test@test.com', 'pass')
        self.user.profile.role = 'doctor'
        self.user.profile.save()

    def test_list_view_requires_auth(self):
        """Test authentication requirement"""
        response = self.client.get(reverse('module_name:list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_list_view_accessible_by_doctor(self):
        """Test doctor can access list"""
        self.client.login(username='test', password='pass')
        response = self.client.get(reverse('module_name:list'))
        self.assertEqual(response.status_code, 200)
```

#### 7. Run Migrations

```bash
python manage.py makemigrations module_name
python manage.py migrate
```

#### 8. Register URLs

```python
# config/urls.py
urlpatterns = [
    # ...
    path('module-name/', include('module_name.urls')),
]
```

---

## 📦 Module Templates

### Template: Basic CRUD Module

**Use for:** Simple data management (e.g., Categories, Tags, Settings)

**Includes:**
- List view with pagination
- Detail view
- Create/Update forms
- Delete confirmation
- Admin panel integration

**Copy from:** `templates/module_templates/basic_crud/`

### Template: Dashboard Module

**Use for:** Analytics, statistics, reporting

**Includes:**
- Statistics cards
- Charts (Chart.js integration)
- Filters and date ranges
- Export functionality
- Cached queries

**Copy from:** `templates/module_templates/dashboard/`

### Template: File Management Module

**Use for:** Document uploads, image galleries

**Includes:**
- File upload with validation
- File preview
- Download functionality
- Storage management
- Thumbnail generation

**Copy from:** `templates/module_templates/file_management/`

### Template: API Module

**Use for:** REST API endpoints (Django REST Framework)

**Includes:**
- Serializers
- ViewSets
- Authentication
- Pagination
- Filtering

**Copy from:** `templates/module_templates/api/`

---

## 🔄 Extension Guidelines

### Extending Existing Modules

#### 1. Adding New Models to Existing Module

```python
# In existing module's models.py

class NewModel(TimeStampedModel):
    """New model that extends module functionality"""

    # Link to existing model if needed
    existing_model = models.ForeignKey(
        ExistingModel,
        on_delete=models.CASCADE,
        related_name='new_models'
    )

    # New fields
    new_field = models.CharField(max_length=100)
```

**Don't forget:**
- Add to `admin.py`
- Create tests
- Run migrations
- Update documentation

#### 2. Adding New Views

```python
# In existing module's views.py

class NewFeatureView(DoctorRequiredMixin, PageTitleMixin, TemplateView):
    """New view that extends module"""
    template_name = 'module_name/pages/new_feature.html'
    page_title = "New Feature"
```

**Add URL:**
```python
# In module's urls.py
path('new-feature/', views.NewFeatureView.as_view(), name='new_feature'),
```

#### 3. Extending Services

```python
# In module's services.py

class ModuleService:
    # ... existing methods ...

    @staticmethod
    def new_feature(data: dict) -> Result:
        """
        New feature added to service.

        Args:
            data: Input data

        Returns:
            Result object
        """
        # Implementation
        pass
```

#### 4. Adding Template Components

```django
{# templates/module_name/components/new_component.html #}
<div class="new-component {{ component_class }}">
    {{ content }}
</div>

{# Usage in other templates #}
{% include 'module_name/components/new_component.html' with content="..." %}
```

### Module Integration Patterns

#### Pattern 1: Cross-Module References

```python
# In new module
from detection.models import Prediction

class NewModel(models.Model):
    prediction = models.ForeignKey(Prediction, on_delete=models.CASCADE)
```

#### Pattern 2: Shared Services

```python
# In new module's services.py
from detection.services import PredictionService

class NewModuleService:
    @staticmethod
    def process_with_prediction(prediction_id: int):
        # Use existing service
        prediction = PredictionService.get_by_id(prediction_id)
        # New logic here
```

#### Pattern 3: Template Extension

```django
{# New module extends detection template #}
{% extends 'detection/base.html' %}

{% block detection_content %}
    {# New module content #}
{% endblock %}
```

---

## ✅ Validation Checklist

### Before Committing New Module

#### Code Quality
- [ ] All files follow PEP 8
- [ ] Type hints on all public functions
- [ ] Docstrings for all classes/methods
- [ ] No unused imports or code
- [ ] Logging added for important operations

#### Functionality
- [ ] Models inherit from base classes
- [ ] Views use appropriate mixins
- [ ] Services handle business logic
- [ ] Forms validate all inputs
- [ ] Admin panel configured

#### Security
- [ ] Authentication required for sensitive views
- [ ] Authorization checks (role-based)
- [ ] Input validation on all forms
- [ ] CSRF protection on forms
- [ ] No SQL injection vulnerabilities

#### UI/UX
- [ ] Mobile responsive (all breakpoints)
- [ ] Consistent with design system
- [ ] Bootstrap components used correctly
- [ ] Icons consistent with icon mapping
- [ ] Loading/empty/error states included

#### Performance
- [ ] N+1 queries prevented
- [ ] Indexes on filtered fields
- [ ] select_related/prefetch_related used
- [ ] Pagination on large datasets
- [ ] Caching where appropriate

#### Testing
- [ ] Model tests written
- [ ] View tests written
- [ ] Form tests written
- [ ] Service tests written
- [ ] Minimum 80% coverage

#### Documentation
- [ ] Module purpose documented
- [ ] API/public methods documented
- [ ] Integration points documented
- [ ] README updated
- [ ] This guide updated if needed

---

## 📝 Session Handoff

### Starting a New Session

**Read these files first:**
1. `README.md` - Project overview
2. `MODULE_DEVELOPMENT_GUIDE.md` - This file
3. `PROJECT_STRUCTURE.md` - Current structure
4. `TESTING_GUIDE.md` - How to test

**Check current state:**
```bash
# Check which modules exist
ls -la

# Check what's been committed
git log --oneline -10

# Check current branch
git branch

# Check for uncommitted changes
git status
```

### Ending a Session

**Before finishing:**

1. **Commit all changes:**
```bash
git add .
git commit -m "Descriptive message about what was added/changed"
git push
```

2. **Update documentation:**
- Update `PROJECT_STRUCTURE.md` if structure changed
- Update `MODULE_DEVELOPMENT_GUIDE.md` if patterns changed
- Update module-specific README if created

3. **Create session summary:**
```markdown
# Session Summary - [Date]

## What Was Completed
- Created X module
- Added Y feature
- Fixed Z bug

## Current State
- All tests passing: ✅/❌
- Migrations applied: ✅/❌
- Documentation updated: ✅/❌

## Next Steps
1. TODO item 1
2. TODO item 2

## Known Issues
- Issue 1
- Issue 2

## Notes
- Important decision: reason
- Consideration for next session
```

Save as `docs/sessions/session_YYYYMMDD.md`

---

## 🎯 Module Development Workflow

### Recommended Process

```
Session 1: Planning & Structure
├── Define module purpose
├── Create user stories
├── Plan models and relationships
├── Design UI mockups (on paper/figma)
└── Document in session notes

Session 2: Backend Implementation
├── Create models
├── Write services
├── Add admin panel
├── Write model/service tests
└── Run migrations

Session 3: Views & URLs
├── Create views (CBV + mixins)
├── Configure URLs
├── Write view tests
└── Test with curl/Postman

Session 4: Frontend Implementation
├── Create templates
├── Add components
├── Style with Bootstrap
├── Test responsive design

Session 5: Integration & Testing
├── Integrate with existing modules
├── End-to-end testing
├── Fix bugs
└── Performance optimization

Session 6: Documentation & Polish
├── Update documentation
├── Add inline comments
├── Create user guide
└── Final validation checklist
```

---

## 📚 Reference Materials

### Essential Files to Reference

1. **Skills** (`.claude/skills/`)
   - Apply automatically during development
   - Reference for specific patterns

2. **Existing Modules**
   - `detection/` - Main module (reference for patterns)
   - `accounts/` - Authentication (reference for user management)

3. **Documentation**
   - `README.md` - Project overview
   - `TESTING_GUIDE.md` - Testing instructions
   - `files/INDEX.md` - Original requirements

### Quick Reference Commands

```bash
# Start development server
python manage.py runserver

# Create new app
python manage.py startapp app_name

# Database operations
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Run tests
python manage.py test
python manage.py test app_name

# Shell access
python manage.py shell

# Check for issues
python manage.py check

# Collect static files
python manage.py collectstatic

# Create admin user
python manage.py createsuperuser
```

---

## 🔗 Module Dependency Graph

Current dependencies:

```
config (settings)
    ├── accounts (authentication)
    │   └── User model (Django)
    │
    ├── detection (main COVID-19 detection)
    │   ├── accounts (for users)
    │   ├── Prediction model
    │   ├── XRayImage model
    │   ├── Patient model
    │   └── ml_engine (PyTorch)
    │
    └── dashboards (role-based dashboards)
        ├── accounts (for users)
        └── detection (for data)
```

**Rule:** Avoid circular dependencies! Always check dependency direction before importing.

---

## 🎓 Best Practices Recap

1. **Always inherit from base models** (TimeStampedModel, UserTrackingModel)
2. **Use mixins for common view functionality**
3. **Business logic goes in services, not views**
4. **Test every public method**
5. **Document with docstrings (Google style)**
6. **Validate all user input**
7. **Optimize database queries**
8. **Keep UI consistent with design system**
9. **Make everything mobile-responsive**
10. **Follow security best practices**

---

## 📞 Troubleshooting

### Common Issues

**Import Errors:**
```python
# Check app is in INSTALLED_APPS
# Check __init__.py exists in module
# Check circular imports
```

**Migration Errors:**
```bash
# Delete migrations and recreate
rm module_name/migrations/0001_*.py
python manage.py makemigrations module_name
```

**URL Not Found:**
```python
# Check app_name in urls.py
# Check URL is registered in config/urls.py
# Check URL name is correct
```

**Template Not Found:**
```django
# Check template directory structure
# Check TEMPLATES setting
# Check template name spelling
```

---

**This guide should be updated as patterns evolve and new best practices emerge!**

**Version History:**
- v1.0 (2025-11-18): Initial creation
