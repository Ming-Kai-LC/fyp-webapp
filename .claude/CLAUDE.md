# Claude Code Project Rules and Guidelines

This document serves as the primary reference for all project rules, conventions, and best practices for the COVID-19 Detection Web Application.

---

## Core Project Skills

The following skills define the fundamental rules and patterns for this project. **Always refer to these skills** when working on related features.

### 1. User Role Permissions and Access Control ⭐ **PRIMARY RULE**

**Skill:** `user-role-permissions`

**Critical Access Control Rules:**

1. **Only admin can create staff users** - Staff accounts must be created through admin panel or admin-only views
2. **Public registration is patient-only** - Public self-registration creates patient accounts exclusively
3. **Admin has full privileges** - Complete CRUD access to all resources
4. **Staff have read/update + limited create/delete** - Can view all records, update medical data, create X-rays/reports/predictions, delete own pending items
5. **Patients have self-service only** - Can register, view, and update their own profile and medical records only

**Apply this skill when:**
- Implementing authentication, authorization, or user management
- Creating views, APIs, or models handling user data
- Adding role-specific features (dashboards, uploads, reports)
- Implementing access control in templates or UI

---

### 2. Full-Stack Django Patterns (includes Django Module Creation)

**Skill:** `full-stack-django-patterns`

**Key Principles:**
- Fat Models, Thin Views pattern
- Service layer for business logic
- Class-based views with mixins
- Type hints and comprehensive docstrings
- Custom managers and querysets
- Centralized constants, utilities, and decorators
- Abstract base models and reusable patterns

**Apply this skill when:**
- Creating new Django apps or modules
- Adding new models, views, or business logic
- Refactoring existing code
- Implementing any full-stack Django feature

**Note:** This skill now includes all django-module-creation patterns (consolidated 2025-11-23)

---

### 3. Security Best Practices

**Skill:** `security-best-practices`

**Key Principles:**
- OWASP Top 10 protection
- Healthcare-grade security (HIPAA-like standards)
- Input validation and sanitization
- CSRF/XSS prevention
- Secure file upload handling
- Audit logging for sensitive operations
- Data encryption and anonymization

**Apply this skill when:**
- Handling user input or file uploads
- Implementing authentication/authorization
- Working with sensitive medical data
- Adding audit logging features

---

### 4. Standard Folder Structure

**Skill:** `standard-folder-structure`

**Key Principles:**
- Consistent module organization across all apps
- Separation of concerns (models, views, services, forms, etc.)
- 500-line file limit (split when exceeded)
- Dedicated folders for templates, static files, tests

**Apply this skill when:**
- Creating new Django apps
- Organizing or refactoring code
- Adding new files to existing modules

---

### 5. UI/UX Design System (includes UI/UX Consistency & Mobile Responsive)

**Skill:** `ui-design-system`

**Key Principles:**
- Bootstrap 5 design system with design tokens
- Consistent color schemes and typography
- Role-specific UI patterns
- Mobile-first responsive design
- Accessible components (WCAG 2.1 AA compliance)
- Responsive breakpoints and grid patterns

**Apply this skill when:**
- Creating templates or UI components
- Designing dashboards or forms
- Implementing navigation or layouts
- Building mobile-responsive interfaces

**Note:** This skill consolidates ui-ux-consistency and mobile-responsive patterns (consolidated 2025-11-23)

---

### 6. Code Quality Standards

**Skill:** `code-quality-standards`

**Key Principles:**
- PEP 8 compliance
- Type hints for all functions/methods
- Comprehensive docstrings
- 80%+ test coverage
- No unused imports or variables

**Apply this skill when:**
- Writing any Python code
- Creating tests
- Refactoring existing code

---

### 7. Foundation Components (includes Component Reusability)

**Skill:** `foundation-components`

**Key Principles:**
- DRY (Don't Repeat Yourself) principle
- Centralized common/ app components (models, widgets, utils, template tags)
- Template components and includes
- View mixins for shared functionality (RoleRequiredMixin, PageTitleMixin)
- Abstract models for common fields (TimeStampedModel, FullAuditModel)
- Reusable Bootstrap widget library

**Apply this skill when:**
- Creating new components or features
- Noticing code duplication
- Refactoring to reduce redundancy
- Building any new Django module (MANDATORY)

**Note:** This skill consolidates component-reusability patterns into the foundation components (consolidated 2025-11-23)

---

### 8. Dual-Layer Validation ⭐ **INPUT SECURITY & UX**

**Skill:** `dual-layer-validation`

**Key Principles:**
- Server-side validation: MANDATORY (security boundary)
- Client-side validation: MANDATORY (user experience)
- Defense in depth: Both layers must be implemented
- Never trust client input
- Consistent error messages across layers
- Real-time validation feedback

**Apply this skill when:**
- Creating any Django form
- Creating any DRF serializer
- Adding model fields with constraints
- Implementing file upload functionality
- Creating API endpoints
- Writing JavaScript that accepts user input
- Implementing search or filter functionality

**What This Skill Provides:**
- Server-side validation patterns (Django forms, serializers, models)
- Client-side validation patterns (HTML5, JavaScript)
- Centralized validation utilities
- File upload validation (both layers)
- Real-time validation with async uniqueness checks
- Common validation patterns and anti-patterns
- Complete validation checklist

**Result:** Security through server-side validation, excellent UX through client-side validation, defense in depth through both.

---

### 9. Performance Optimization

**Note:** This has been consolidated into `full-stack-django-patterns` skill (Section 15)

**Key Principles:**
- N+1 query prevention
- select_related/prefetch_related usage
- ML inference optimization for RTX 4060 8GB VRAM
- Caching strategies (Redis/Memcached)
- Database indexing

---

### 10. Virtual Environment

**Note:** This has been consolidated into `code-quality-standards` skill

**Key Principles:**
- Always use virtual environment for Python operations
- Use `venv/Scripts/python.exe` on Windows
- Use `venv/Scripts/pip.exe` for package installation
- Never install packages globally

---

### 11. Full-Stack Django Patterns ⭐ **COMPREHENSIVE FRAMEWORK**

**Skill:** `full-stack-django-patterns`

**Key Principles:**
- Define once, use everywhere (DRY)
- Centralized constants, utilities, and decorators
- Reusable widgets, template tags, and form mixins
- Abstract base models (TimeStampedModel, AuditableModel)
- Standard error handling and validation patterns
- Query optimization and database patterns
- API standards and response formats
- Logging and monitoring patterns
- Secure file upload patterns
- Testing factories and fixtures

**Apply this skill when:**
- Creating any new Django module or feature
- Noticing repeated code patterns across modules
- Writing forms, widgets, or templates
- Implementing business logic or services
- Adding API endpoints or serializers
- Writing tests or fixtures
- Handling file uploads or media
- Optimizing database queries
- Setting up logging or error handling
- Refactoring existing code

**What This Skill Provides:**
- 15 comprehensive sections covering full-stack patterns
- Concrete examples from the codebase
- Anti-patterns to explicitly avoid
- Integration with all existing skills
- Constants management (`constants.py`)
- Utilities library (`utils.py`)
- Error handling & custom exceptions
- Cross-module communication patterns
- Advanced model patterns (abstract bases, managers)
- Form & widget library (Bootstrap components)
- Template tag & filter library
- API patterns & standards
- Authentication & authorization patterns
- Testing patterns & factories
- Logging & monitoring standards
- Background tasks & async patterns
- File upload security & processing
- Frontend-backend integration
- Database optimization patterns

**Result:** Maximum code reuse, DRY compliance, consistency, and efficiency across the entire full-stack application.

---

### 12. Three-Tier Architecture ⭐ **ARCHITECTURAL PATTERN**

**Skill:** `three-tier-architecture`

**Key Principles:**
- Hybrid three-tier architecture with selective service layers
- Presentation Tier: Thin views/APIs (HTTP handling only)
- Application Tier: Service layer (reusable business logic)
- Data Tier: Django ORM models (data persistence)
- Use services for complex workflows, keep simple CRUD in views
- Services are framework-agnostic and testable

**Apply this skill when:**
- Implementing complex multi-step workflows
- Adding functionality shared between web views and API
- Writing business logic involving multiple models
- Integrating with external services (email, SMS, APIs)
- Noticing code duplication between views and API endpoints
- Refactoring fat views (>100 lines)
- Creating features that need independent testing

**What This Skill Provides:**
- Clear guidelines for when to use service layers
- Service class patterns and naming conventions
- Real implementation examples from detection module
- View refactoring checklist
- Testing strategies for services
- Common pitfalls and solutions
- Migration strategy for existing code

**Service Layer Examples:**
- `PredictionService` - Core prediction workflow orchestration
- `XRayService` - X-ray upload and preprocessing
- `StatisticsService` - Dashboard statistics aggregation
- Pattern: Workflow orchestration, permission-aware access, external integration

**Results from detection/ module:**
- `upload_xray()` view: 133 lines → 66 lines (50% reduction)
- `staff_dashboard()` view: 27 lines → 18 lines (33% reduction)
- Business logic now reusable across web, API, CLI, and Celery tasks
- Single source of truth for prediction workflow

**When NOT to use:**
- Simple CRUD operations (list, retrieve)
- Basic ORM queries
- Model-specific methods (belongs in model)
- Simple form validation (belongs in forms)

**Result:** Code reusability across all interfaces, improved testability, better separation of concerns, and 30-50% reduction in view complexity.

---

### 13. Module Creation Lifecycle Orchestration ⭐ **DEVELOPMENT LIFECYCLE**

**Skill:** `module-creation-lifecycle`

**Key Principles:**
- Complete end-to-end module creation process
- Four-phase lifecycle: Planning → Code Generation → Quality Verification → Integration
- Automated validation gates at each phase
- Integration with all existing skills
- TodoWrite integration for progress tracking

**Auto-triggers when:**
- User requests "create a new module/app"
- User asks to "add a new feature" requiring new Django app
- Detects phrases: "new module", "create app", "build system for"

**What This Skill Orchestrates:**

**Phase 1: Planning (Before Code)**
- Clarifying questions (models, APIs, permissions, workflows)
- Model and relationship design
- API endpoint planning
- Permission requirements identification
- Service layer planning (if complex logic)

**Phase 2: Code Generation (Strict Order)**
1. Create Django app with proper naming
2. Create folder structure (services/, tests/, templates/, static/)
3. Create models.py (inherit abstract bases)
4. Create constants.py (ALWAYS - no exceptions)
5. Create and run migrations
6. Create admin.py (with role-based permissions)
7. Create forms.py (using widget library)
8. Create services/ (if complex workflows)
9. Create views.py (thin controllers)
10. Create urls.py
11. Create templates/ (Bootstrap 5, responsive)
12. Create serializers.py (if API needed)
13. Create comprehensive tests (during development, not after)

**Phase 3: Quality Checklist (Auto-Verify)**
- Models: Abstract bases, type hints, docstrings, indexes
- Constants: All magic strings centralized
- Forms: Widget library used, validation patterns
- Views: Thin (<50 lines), permissions applied
- Services: Framework-agnostic, structured logging
- Security: Input validation, object-level permissions
- Code quality: PEP 8, type hints, no unused imports

**Phase 4: Integration & Validation**
- Update INSTALLED_APPS
- Include URLs in config/urls.py
- Run migrations
- Run tests (verify ≥80% coverage)
- Manual testing (admin, web, API)
- Update documentation

**Apply this skill when:**
- Creating any new Django module
- User requests new feature requiring new app
- Building complete feature from scratch

**Result:** Fully functional, tested, documented modules created autonomously following all best practices without user reminders.

---

### 14. Testing Automation & Workflow ⭐ **QUALITY ASSURANCE**

**Skill:** `testing-automation`

**Key Principles:**
- Four-level testing automation
- Test-driven development (TDD) approach
- Comprehensive test coverage (unit, integration, permission, API, E2E)
- Automated quality gates
- Coverage enforcement (≥80%)

**Auto-triggers when:**
- Any code is written or modified
- Module creation reaches testing phase
- User asks to "test this" or "run tests"
- Before creating git commits
- Before creating pull requests

**What This Skill Provides:**

**Level 1: Pre-commit Hooks**
- `.pre-commit-config.yaml` configuration
- Fast quality checks before commits (<10 seconds)
- Checks: black, isort, flake8, mypy, django-check, fast unit tests, bandit, secrets detection
- Blocks commits if any check fails

**Level 2: GitHub Actions CI/CD**
- `.github/workflows/django-ci.yml` workflow
- Full test suite on every push/PR
- Matrix testing (Python 3.11+, multiple Django versions)
- Steps: install → migrate → test → coverage → security scan
- Uploads to Codecov
- Blocks merge if tests fail or coverage <80%

**Level 3: Test Generation Guidance**
- Comprehensive test patterns for all code types
- Test organization structure (conftest.py, factories.py, test_*.py)
- Fixtures and factories for test data
- Test types: models, forms, views, services, API, integration, E2E
- Permission testing for all user roles
- Mocking patterns for external services

**Level 4: Coverage Enforcement**
- pytest configuration with coverage reporting
- Minimum coverage: 80% overall
- Module-specific targets: Models 90%, Services 85%, Forms 85%, Views 80%
- HTML, terminal, and XML coverage reports
- Branch coverage enabled

**Test Creation Timeline:**
- After models → Create test_models.py
- After forms → Create test_forms.py
- After views → Create test_views.py + permission tests
- After services → Create test_services.py
- After API → Create test_api.py
- Before commit → Run pre-commit hooks
- Before PR → Run full test suite locally

**Apply this skill when:**
- Writing any code
- Creating new features
- Refactoring existing code
- Before committing changes
- Before creating pull requests

**Result:** Automated testing at every stage, comprehensive coverage, quality gates prevent regressions, all tests documented and maintainable.

---

### 15. Development Workflow & Git Standards ⭐ **VERSION CONTROL**

**Skill:** `development-workflow` (consolidated into `testing-automation`)

**Key Principles:**
- Git Flow inspired workflow
- Conventional Commits standard
- Comprehensive PR templates
- Code review guidelines
- Automated git workflow integration

**Auto-triggers when:**
- Creating git commits
- Creating pull requests
- Branching or merging
- Code review scenarios

**What This Skill Enforces:**

**Branch Naming Standards:**
- `feature/<short-description>` - New features
- `bugfix/<issue-number>-<description>` - Bug fixes
- `hotfix/<critical-issue>` - Critical production fixes
- `release/v<major>.<minor>.<patch>` - Release preparation

**Conventional Commits Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:** feat, fix, docs, style, refactor, perf, test, chore, ci, security

**Examples:**
- `feat(appointments): Add appointment scheduling system`
- `fix(auth): Correct staff permission check in dashboard`
- `test(api): Add comprehensive API endpoint tests`

**PR Template (`.github/pull_request_template.md`):**
- Summary (what/why)
- Type of change checklist
- Related issues
- Changes made (detailed list)
- Testing done (unit, integration, manual)
- Database changes checklist
- Security considerations
- Performance impact
- Documentation updates
- Complete verification checklist

**Code Review Guidelines:**
- Self-review checklist before requesting review
- Reviewer checklist: correctness, security, performance, tests, quality
- Comment guidelines (constructive, specific, respectful)
- Approval criteria

**Commit Process (Auto-Applied):**
1. Check status and diff
2. Analyze changes for commit type and scope
3. Draft Conventional Commit message
4. Stage relevant files (never .env, credentials, secrets)
5. Create commit with proper formatting (HEREDOC)
6. Verify commit message

**PR Process (Auto-Applied):**
1. Verify branch status and up to date
2. Run tests locally
3. Push branch to remote
4. Analyze all commits and changes
5. Generate comprehensive PR description
6. Create PR using gh CLI
7. Monitor CI/CD status

**Apply this skill when:**
- Committing any changes
- Creating pull requests
- Reviewing code
- Branching or merging

**Result:** Consistent git history, comprehensive PR descriptions, high-quality code reviews, automated workflow reduces errors.

---

## Foundation Components - Critical Infrastructure

**IMPORTANT:** The following foundation files are **MANDATORY** for all modules to ensure consistency, reusability, and DRY principles across the entire application. Always use these instead of creating custom implementations.

### 1. Abstract Base Models (`common/models.py`)

**Location:** `common/models.py`

**ALWAYS inherit from these base models:**

| Model | Purpose | Fields Added | When to Use |
|-------|---------|--------------|-------------|
| `TimeStampedModel` | Auto-timestamp tracking | `created_at`, `updated_at` | **ALL models** (mandatory) |
| `SoftDeleteModel` | Soft delete functionality | `is_deleted`, `deleted_at`, `deleted_by` | Models requiring deletion tracking |
| `AuditableModel` | User tracking | `created_by`, `updated_by` | Models needing audit trail |
| `FullAuditModel` | Complete audit trail | All above fields | Medical records, sensitive data |
| `ActiveManager` | Query manager | N/A (manager) | Use with `SoftDeleteModel` |

**Example usage:**
```python
from common.models import TimeStampedModel, FullAuditModel

# Basic model with timestamps (minimum requirement)
class Appointment(TimeStampedModel):
    # Auto gets: created_at, updated_at
    patient = models.ForeignKey('detection.Patient', on_delete=models.CASCADE)
    scheduled_date = models.DateTimeField()

# Medical record with full audit trail
class MedicalRecord(FullAuditModel):
    # Auto gets: created_at, updated_at, created_by, updated_by,
    #            is_deleted, deleted_at, deleted_by
    # Use: objects (active only), all_objects (including deleted)
    patient = models.ForeignKey('detection.Patient', on_delete=models.CASCADE)
    diagnosis = models.TextField()
```

**Why:** Eliminates 5-10 lines of boilerplate per model, ensures consistency, enables project-wide audit capabilities.

---

### 2. Bootstrap Widget Library (`common/widgets.py`)

**Location:** `common/widgets.py`

**ALWAYS use these widgets instead of hardcoded `attrs={'class': 'form-control'}`:**

| Widget | Bootstrap Component | Usage |
|--------|---------------------|-------|
| `BootstrapTextInput` | Text input (form-control) | Name, address, text fields |
| `BootstrapEmailInput` | Email input with validation | Email fields |
| `BootstrapPasswordInput` | Password input | Password fields |
| `BootstrapTextarea` | Textarea (form-control) | Notes, descriptions, long text |
| `BootstrapSelect` | Select dropdown (form-select) | Choice fields, dropdowns |
| `BootstrapCheckboxInput` | Checkbox (form-check-input) | Boolean fields |
| `BootstrapRadioSelect` | Radio buttons (form-check) | Single choice from options |
| `BootstrapDateInput` | Date picker (date type) | Date fields |
| `BootstrapDateTimeInput` | DateTime picker | DateTime fields |
| `BootstrapFileInput` | File upload (form-control) | File/image uploads |

**Example usage:**
```python
from common.widgets import BootstrapTextInput, BootstrapSelect, BootstrapDateTimeInput

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'scheduled_date', 'appointment_type', 'notes']
        widgets = {
            'scheduled_date': BootstrapDateTimeInput(),  # ✅ Correct
            'appointment_type': BootstrapSelect(choices=AppointmentType.CHOICES),
            'notes': BootstrapTextarea(attrs={'rows': 3, 'placeholder': 'Notes...'}),
        }

# ❌ WRONG - Never do this:
widgets = {
    'scheduled_date': forms.DateTimeInput(attrs={
        'class': 'form-control', 'type': 'datetime-local'
    }),  # Hardcoded - DO NOT USE
}
```

**Why:** Ensures UI consistency, eliminates 3-5 lines of boilerplate per field, centralizes Bootstrap class management.

---

### 3. Template Tags & Filters (`common/templatetags/common_tags.py`)

**Location:** `common/templatetags/common_tags.py`

**ALWAYS load and use these tags in templates:**

| Tag/Filter | Purpose | Example |
|------------|---------|---------|
| `{% status_badge status %}` | Render color-coded status badge | `{% status_badge "pending" %}` → Yellow badge |
| `{% diagnosis_badge diagnosis %}` | Render diagnosis badge with icon | `{% diagnosis_badge "COVID" %}` → Red badge with virus icon |
| `{% format_datetime dt %}` | Format datetime consistently | `{% format_datetime appointment.created_at %}` → "22 Nov 2025, 2:30 PM" |
| `{% format_date date %}` | Format date | `{% format_date patient.dob %}` → "22 Nov 2000" |
| `{% time_since dt %}` | Human-readable time | `{% time_since appointment.created_at %}` → "2 hours ago" |
| `{% render_pagination page_obj %}` | Render pagination component | `{% render_pagination predictions %}` → Full pagination UI |

**Example usage:**
```django
{% extends "base.html" %}
{% load common_tags %}  {# ✅ Always load this #}

{% block content %}
<table class="table">
    <tr>
        <td>{{ patient.name }}</td>
        <td>{% status_badge appointment.status %}</td>  {# ✅ Correct #}
        <td>{% format_datetime appointment.scheduled_date %}</td>
        <td>{% diagnosis_badge prediction.diagnosis %}</td>
    </tr>
</table>

{% render_pagination page_obj %}
{% endblock %}
```

**Why:** Ensures consistent badge colors, date formats, and pagination across all modules. Eliminates template code duplication.

---

### 4. Reusable Template Components (`templates/components/`)

**Location:** `templates/components/`

**ALWAYS include these components instead of duplicating HTML:**

| Component | File | Usage |
|-----------|------|-------|
| Card | `card.html` | `{% include 'components/card.html' with title="..." %}` |
| Alert | `alert.html` | `{% include 'components/alert.html' with message="Success!" type="success" %}` |
| Loading Spinner | `loading_spinner.html` | `{% include 'components/loading_spinner.html' with text="Loading..." %}` |
| Pagination | `pagination.html` | Use `{% render_pagination page_obj %}` tag instead |

**Example usage:**
```django
{% extends "base.html" %}

{% block content %}
{# Display alert messages #}
{% if messages %}
    {% for message in messages %}
        {% include 'components/alert.html' with message=message type=message.tags dismissible=True %}
    {% endfor %}
{% endif %}

{# Card component with custom content #}
{% include 'components/card.html' with title="Appointments" title_icon="calendar" %}
    {% block card_body %}
        <p>Card content here...</p>
    {% endblock %}
{% endinclude %}

{# Loading spinner #}
<div id="loading" style="display:none;">
    {% include 'components/loading_spinner.html' with text="Processing X-ray..." %}
</div>
{% endblock %}
```

**Why:** Eliminates 20-50 lines of duplicated HTML per page, ensures consistent Bootstrap structure, enables global component updates.

---

### 5. Common Utilities (`common/utils.py`)

**Location:** `common/utils.py`

**ALWAYS use these utilities instead of reimplementing:**

**Validation Functions:**
- `validate_phone(phone: str) -> bool` - Malaysian phone number validation
- `validate_image_file(file, max_size_mb: int = 10) -> bool` - Image file validation
- `validate_nric(nric: str) -> bool` - Malaysian NRIC validation

**File Handling:**
- `sanitize_filename(filename: str) -> str` - Sanitize uploaded file names
- `generate_unique_filename(filename: str, prefix: str = '') -> str` - Generate unique file names with UUID
- `format_file_size(size_bytes: int) -> str` - Format bytes to human-readable (e.g., "2.5 MB")

**Date/Time Utilities:**
- `calculate_age(date_of_birth: datetime) -> int` - Calculate age from DOB
- `time_since(dt: datetime) -> str` - Human-readable time difference (e.g., "2 hours ago")

**Example usage:**
```python
from common.utils import validate_phone, validate_image_file, generate_unique_filename

class PatientForm(forms.ModelForm):
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not validate_phone(phone):  # ✅ Use utility
            raise forms.ValidationError("Invalid Malaysian phone number.")
        return phone

    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image')
        if image and not validate_image_file(image, max_size_mb=5):
            raise forms.ValidationError("Invalid image or size exceeds 5MB.")
        return image

# File upload handling
def handle_upload(file, prefix='xray'):
    unique_name = generate_unique_filename(file.name, prefix=prefix)
    # Save with unique name...
```

**Why:** Eliminates 10-30 lines of validation code per module, ensures consistent validation rules, centralizes business logic.

---

### 6. UI/UX Design System (`UI_UX_DESIGN_SYSTEM.md`)

**Location:** `UI_UX_DESIGN_SYSTEM.md`

**ALWAYS consult this document before creating UI components.**

**What it provides:**
- **Color Palette:** Primary (#0d6efd), secondary, success, danger, warning, info colors
- **Typography:** Font families (Inter, -apple-system), font scale (12px - 48px)
- **Spacing System:** Bootstrap spacing utilities (m-*, p-*, g-*, gap-*)
- **Component Patterns:** Cards, tables, forms, buttons, badges, modals, alerts
- **Accessibility Guidelines:** WCAG 2.1 AA compliance, color contrast ratios, ARIA labels
- **Responsive Breakpoints:** xs (<576px), sm (576px), md (768px), lg (992px), xl (1200px), xxl (1400px)

**Example reference:**
```django
{# Follow design system color palette #}
<div class="card border-primary">  {# Primary color from design system #}
    <div class="card-header bg-primary text-white">
        <h5>Diagnosis Results</h5>
    </div>
</div>

{# Use spacing system #}
<div class="mb-4 p-3">  {# mb-4 = 1.5rem, p-3 = 1rem from design system #}
    <p class="fs-5">Patient Details</p>  {# fs-5 from typography scale #}
</div>
```

**Why:** Ensures visual consistency, maintains accessibility standards, provides design reference for all developers.

---

### Foundation Files Checklist

**When creating a new module, ALWAYS verify:**

- ✅ All models inherit from `TimeStampedModel` (minimum) or other base models
- ✅ All forms use `common.widgets` (BootstrapTextInput, BootstrapSelect, etc.)
- ✅ Templates load `{% load common_tags %}` and use status_badge, format_datetime, etc.
- ✅ Templates include `components/card.html`, `components/alert.html` instead of duplicating HTML
- ✅ Validation uses `common.utils` (validate_phone, validate_image_file, etc.)
- ✅ UI design follows `UI_UX_DESIGN_SYSTEM.md` color palette and spacing
- ✅ NO hardcoded Bootstrap classes in widget attrs (use widget library)
- ✅ NO duplicated validation logic (use common utilities)
- ✅ NO custom timestamp fields (inherit TimeStampedModel)

**Enforcement:** The `module-creation-lifecycle` skill automatically enforces all foundation file usage. Violations will trigger quality checklist failures.

---

## Project Technology Stack

- **Framework:** Django 5.1
- **Database:** SQLite (development), PostgreSQL (production-ready)
- **ML Framework:** TensorFlow/Keras (COVID-19 detection model)
- **API:** Django REST Framework with JWT authentication
- **Frontend:** Bootstrap 5, vanilla JavaScript
- **Testing:** pytest with pytest-django
- **Documentation:** Swagger/OpenAPI (drf-yasg)

---

## Project Structure

```
fyp-webapp/
├── config/                 # Project settings
│   └── settings.py
├── common/                 # ⭐ Foundation components (MANDATORY for all modules)
│   ├── models.py          # Abstract base models (TimeStampedModel, SoftDeleteModel, etc.)
│   ├── widgets.py         # Bootstrap form widget library
│   ├── utils.py           # Common utilities (validation, file handling, etc.)
│   └── templatetags/
│       └── common_tags.py # Template tags & filters (status_badge, format_datetime, etc.)
├── accounts/               # User management (placeholder)
├── detection/              # Core COVID detection + user models
│   ├── models.py          # UserProfile, Patient, XRayImage, Prediction
│   ├── views.py           # Registration, dashboards, uploads
│   └── ml_service.py      # ML model inference
├── dashboards/             # Enhanced dashboards
├── medical_records/        # Patient medical records
├── reporting/              # Report generation
├── audit/                  # Audit logging and compliance
├── notifications/          # Notification system
├── appointments/           # Appointment scheduling
├── analytics/              # Analytics and insights
├── api/                    # RESTful API
│   ├── permissions.py     # Custom permission classes
│   └── views.py           # API ViewSets
└── templates/              # Django templates
    ├── base.html
    ├── components/        # ⭐ Reusable UI components (card, alert, pagination, spinner)
    ├── detection/
    ├── dashboards/
    └── registration/
```

**Key Foundation Files:**
- `common/` - MUST be used by all modules for models, widgets, utils, template tags
- `templates/components/` - MUST include these instead of duplicating HTML
- `UI_UX_DESIGN_SYSTEM.md` - MUST consult before creating UI components

---

## User Roles and Permissions Summary

| Feature | Admin | Staff | Patient |
|---------|-------|-------|---------|
| Create staff users | ✅ | ❌ | ❌ |
| Create patient users | ✅ | ❌ | ✅ (self-registration) |
| Upload X-rays | ✅ | ✅ | ❌ |
| View all predictions | ✅ | ✅ | ❌ (own only) |
| Create medical reports | ✅ | ✅ | ❌ |
| Update patient records | ✅ | ✅ | ✅ (own only) |
| Delete users | ✅ | ❌ | ❌ |
| Delete medical records | ✅ | ❌ (pending only) | ❌ |
| Access audit logs | ✅ | ❌ | ❌ |
| Access admin panel | ✅ | ❌ | ❌ |
| View analytics | ✅ | ✅ | ❌ |

---

## Development Workflow

**These workflows are now automated by the lifecycle skills:**

1. **Always activate virtual environment** before running commands (`virtual-environment` skill)
2. **Follow the complete module creation lifecycle** when building features (`module-creation-lifecycle` skill)
3. **Create tests during development** for all new code (`testing-automation` skill)
4. **Follow security-first approach** for user data and medical records (`security-best-practices` skill)
5. **Apply role-based access control** to all new views and APIs (`user-role-permissions` skill)
6. **Maintain 80%+ test coverage** with automated enforcement (`testing-automation` skill)
7. **Document all public APIs** with docstrings and Swagger
8. **Use Conventional Commits format** for all commits (`development-workflow` skill)
9. **Run automated quality gates** before commits (pre-commit hooks) and PRs (CI/CD)
10. **Follow PR template and code review guidelines** (`development-workflow` skill)

**Key Lifecycle Skills:**
- **`module-creation-lifecycle`** - Orchestrates complete module creation from planning to integration
- **`testing-automation`** - Enforces 4-level testing (pre-commit, CI/CD, test generation, coverage)
- **`development-workflow`** - Automates git workflow, commits, and pull requests

**With these skills, Claude Code autonomously follows best practices without user reminders.**

---

## Testing Standards

- **Unit tests:** Test individual functions and methods
- **Integration tests:** Test interactions between components
- **Permission tests:** Test all role-based access control scenarios
- **API tests:** Test all REST API endpoints with different roles
- **E2E tests:** Test complete user workflows (registration → upload → results)
- **Coverage:** Maintain 80%+ coverage for all modules

---

## Security Requirements

1. **All user input must be validated and sanitized**
2. **Medical data must be encrypted at rest** (for production)
3. **All sensitive operations must be audit logged**
4. **CSRF protection enabled** for all forms
5. **XSS protection** via template escaping
6. **SQL injection prevention** via ORM (no raw queries without params)
7. **File upload restrictions** (size, type, virus scanning)
8. **JWT tokens with short expiry** (60 min access, 7 day refresh)
9. **Role-based access control** on all views and APIs
10. **Object-level permissions** for patient data

---

## Quick Reference: Common Patterns

### Creating a Staff-Only View

```python
from reporting.decorators import staff_required

@staff_required
def staff_only_view(request):
    # Implementation
    pass
```

### Creating a Patient-Accessible API

```python
from rest_framework import viewsets
from api.permissions import IsPatientOwner

class MyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsPatientOwner]

    def get_queryset(self):
        if self.request.user.profile.is_patient():
            return MyModel.objects.filter(patient__user=self.request.user)
        return MyModel.objects.all()
```

### Checking User Role in Templates

```django
{% if user.profile.is_admin %}
    <!-- Admin-only content -->
{% elif user.profile.is_staff %}
    <!-- Staff-only content -->
{% else %}
    <!-- Patient content -->
{% endif %}
```

---

## Contact and Support

- **GitHub:** [fyp-webapp repository](https://github.com/Ming-Kai-LC/fyp-webapp)
- **Issues:** Report bugs and feature requests via GitHub Issues
- **Documentation:** See individual skill files in `.claude/skills/`

---

**Last Updated:** 2025-11-24
**Project Version:** 1.0.0
**Django Version:** 5.1
**Python Version:** 3.11+
**Total Skills:** 10 active (consolidated from 16 original)

**Recent Updates:**
- **2025-11-24:** Added new **Dual-Layer Validation** skill - Enforces both server-side and client-side validation for all user inputs (defense in depth)
- **2025-11-23:** Skills consolidation V2 - Reduced from 16 to 9 skills (44% reduction) by merging overlapping concerns:
  - `virtual-environment` merged into `code-quality-standards`
  - `standard-folder-structure` merged into `foundation-components`
  - `performance-optimization` merged into `full-stack-django-patterns`
  - `development-workflow` merged into `testing-automation`
  - `component-reusability` merged into `foundation-components`
  - `ui-ux-consistency` + `mobile-responsive` merged into new `ui-design-system`
  - `django-module-creation` merged into `full-stack-django-patterns`
- **2025-11-22:** Three new lifecycle skills added (Module Creation Lifecycle, Testing Automation, Development Workflow) to enable fully autonomous development following all best practices
