# Verify Implementation Quality

Review the current implementation and verify it follows all project standards.

## Checklist to Verify

### 1. Reusable (foundation-components)
- [ ] CSS extracted to `static/css/` (no inline styles >20 lines)
- [ ] JavaScript extracted to `static/js/` (no inline scripts >20 lines)
- [ ] Uses `common.widgets` (BootstrapTextInput, BootstrapSelect, etc.)
- [ ] Uses `common.mixins` (PageTitleMixin, RoleRequiredMixin, etc.)
- [ ] Uses `common.utils` (validate_phone, validate_image_file, etc.)
- [ ] Uses `detection.constants` (RoleChoices, GenderChoices, etc.)
- [ ] Uses `templates/components/` (alert.html, card.html, etc.)
- [ ] No code duplication - DRY principle applied

### 2. Model Base Classes (foundation-components) - AUTO-ENFORCED
- [ ] ALL models inherit from `TimeStampedModel` (minimum) → `created_at`, `updated_at`
- [ ] Medical/sensitive data uses `FullAuditModel` → adds `created_by`, `updated_by`, `is_deleted`, `deleted_at`, `deleted_by`
- [ ] Deletable records use `TimeStampedSoftDeleteModel` → adds soft delete fields
- [ ] Audit trail records use `TimeStampedAuditableModel` → adds `created_by`, `updated_by`
- [ ] Soft-delete models have `objects = ActiveManager()` and `all_objects = models.Manager()`

**Auto-Enforcement:** Django system checks (`common/checks.py`) run on `runserver`, `migrate`, `check`:
| Check ID | Violation |
|----------|-----------|
| `common.W001` | Model missing `created_at`/`updated_at` (must inherit TimeStampedModel) |
| `common.W002` | Has `is_deleted` but missing `all_objects` manager |
| `common.W003` | Has `created_by` but missing `updated_by` |
| `common.W004` | Incomplete soft-delete fields |

### 3. Class-Based (full-stack-django-patterns)
- [ ] Views use CBV (FormView, TemplateView, ListView, etc.) with mixins
- [ ] Constants use class pattern (e.g., `ProfileFieldDisplayNames.get_display()`)
- [ ] Forms inherit from ModelForm or Form with proper Meta class
- [ ] JavaScript uses class pattern where appropriate (e.g., `FormValidator`)
- [ ] Services use class methods with `@staticmethod`
- [ ] Utilities grouped in utility classes (DateTimeUtils, FileUtils, etc.)

### 4. Thin Views / Service Layer (three-tier-architecture)
- [ ] Views are < 50 lines (thin controllers)
- [ ] Complex workflows use service layer (`services/` folder)
- [ ] Business logic NOT embedded in views
- [ ] Services are framework-agnostic (no request/response objects)
- [ ] Services have structured logging (`logger.info()`)

### 5. User Role Permissions (user-role-permissions)
- [ ] Views have `@login_required` or `LoginRequiredMixin`
- [ ] Staff-only views use `@staff_required` or `RoleRequiredMixin`
- [ ] Admin-only views properly restricted
- [ ] Patient views filter by `patient__user=request.user`
- [ ] Templates use `{% if user.profile.is_admin %}` checks
- [ ] API views have proper `permission_classes`
- [ ] Object-level permissions for sensitive data

### 6. Security (security-best-practices)
- [ ] CSRF token present (`{% csrf_token %}`)
- [ ] No raw SQL queries (use ORM only)
- [ ] File uploads validate: extension, MIME type, size
- [ ] User input sanitized before display (template auto-escaping)
- [ ] Sensitive operations audit logged
- [ ] No secrets in code (use environment variables)
- [ ] XSS prevention (no `|safe` filter on user input)
- [ ] Login rate limiting implemented (5 attempts / 15 min lockout)
- [ ] Session timeout configured (SESSION_COOKIE_AGE)
- [ ] All PHI access logged in `AccessLog` model

### 7. Validation - Server-Side (dual-layer-validation)
- [ ] Every form field has `clean_<field>()` method
- [ ] Form has `clean()` method for cross-field validation
- [ ] Model fields have appropriate validators
- [ ] API serializers have `validate_<field>()` methods
- [ ] File uploads validate type, size, and MIME type
- [ ] Uniqueness constraints checked with `__iexact` (case-insensitive)

### 8. Validation - Client-Side (dual-layer-validation)
- [ ] All inputs have HTML5 attributes: `required`, `minlength`, `maxlength`, `pattern`, `type`
- [ ] JavaScript validation on `blur` and before `submit`
- [ ] Visual feedback with `is-valid`/`is-invalid` classes
- [ ] Error messages displayed in `invalid-feedback` elements
- [ ] Uses `FormValidator` class from `static/js/form-validation.js`
- [ ] Consistent rules with server-side (same min/max, patterns)

### 9. Input Normalization (dual-layer-validation)
- [ ] **Username**: Server `.strip().lower()` + Client `normalize: 'lowercase'`
- [ ] **Email**: Server `.strip().lower()` + Client `normalize: 'lowercase'`
- [ ] **Names**: Server `.strip().title()` + Client `normalize: 'titlecase'`
- [ ] **Uniqueness checks**: Use `__iexact` for case-insensitive matching
- [ ] **Passwords**: NEVER normalized (keep as-is)
- [ ] Normalization applied on blur AND before submit

### 10. Malaysia Date/Time (foundation-components)
- [ ] Python uses `timezone.now()` NOT `datetime.now()`
- [ ] Templates use `{% format_datetime %}` / `{% format_date %}` tags
- [ ] JavaScript uses `toLocaleString('en-MY', { timeZone: 'Asia/Kuala_Lumpur' })`
- [ ] Date validation uses `timezone.now().date()` for comparison
- [ ] Display format: "22 Nov 2025, 2:30 PM" (d M Y, g:i A)

### 11. UI/UX Design (ui-design-system)
- [ ] Mobile-first approach (start with `col-12`, then add breakpoints)
- [ ] Tables wrapped in `<div class="table-responsive">`
- [ ] Images have `class="img-fluid"`
- [ ] Buttons have minimum 44x44px touch target on mobile
- [ ] Viewport meta tag present in template
- [ ] No fixed pixel widths (use responsive classes)
- [ ] Bootstrap color classes used (no hardcoded colors)

### 12. Accessibility (ui-design-system)
- [ ] All images have `alt` attributes
- [ ] Form inputs have associated `<label>` elements
- [ ] Icon-only buttons have `aria-label`
- [ ] Color contrast meets WCAG 2.1 AA (4.5:1 for text)
- [ ] Focus indicators visible (don't remove `:focus` outlines)
- [ ] Semantic HTML used (`<nav>`, `<main>`, `<article>`, etc.)

### 13. Code Quality (code-quality-standards)
- [ ] PEP 8 compliant (naming, indentation, line length)
- [ ] Type hints for all public functions
- [ ] Docstrings for all classes and functions (Google style)
- [ ] No unused imports or variables
- [ ] No `print()` statements (use `logging`)
- [ ] No hardcoded values (use constants or settings)
- [ ] Virtual environment used for all Python commands

### 14. Testing (testing-automation)
- [ ] Unit tests for models, forms, services
- [ ] View tests with permission scenarios
- [ ] API tests with different user roles
- [ ] Test coverage ≥ 80%
- [ ] Test naming: `test_<what>_<condition>_<expected_result>`

### 15. File Organization (foundation-components)
- [ ] Every module has `constants.py` (MANDATORY - no magic strings)
- [ ] No single file exceeds 500 lines (split if needed)
- [ ] Services in `services/` folder (not in views.py)
- [ ] Tests in `tests/` folder with proper structure
- [ ] Static files in module's `static/` or project `static/`
- [ ] Templates in module's `templates/` folder

### 16. Query Optimization (full-stack-django-patterns)
- [ ] `select_related()` used for ForeignKey/OneToOne fields
- [ ] `prefetch_related()` used for ManyToMany/reverse FK
- [ ] `.only()` or `.defer()` used for large fields when appropriate
- [ ] `.values()` or `.values_list()` for aggregations
- [ ] `.exists()` used instead of `.count() > 0`
- [ ] No N+1 queries (check with Django Debug Toolbar)
- [ ] Database indexes on frequently filtered/ordered fields

### 17. List Views & Pagination (full-stack-django-patterns)
- [ ] All list views have pagination (25-50 items per page max)
- [ ] Uses Django's `Paginator` or `ListView.paginate_by`
- [ ] Template uses `{% render_pagination page_obj %}` tag
- [ ] API endpoints use `StandardResultsSetPagination`
- [ ] No unlimited querysets returned to templates

### 18. Healthcare UI Patterns (ui-design-system)
- [ ] Patient data cards show "PHI Protected" badge
- [ ] Diagnosis results use color-coded severity (danger/warning/success)
- [ ] Emergency alerts use `aria-live="assertive"`
- [ ] Medical forms have multi-step progress indicators
- [ ] X-ray viewer has zoom controls and metadata display
- [ ] Timeline view for treatment/appointment history

### 19. AJAX Partial Refresh (full-stack-django-patterns)
- [ ] Partial templates in `templates/app/partials/` folder (NO extends)
- [ ] Views detect AJAX with `is_ajax()` helper function
- [ ] Return HTML fragment for AJAX, full page otherwise
- [ ] Container has unique ID for JavaScript targeting
- [ ] Use `PartialRefresh` class for list/table updates
- [ ] Use `AutoRefresh` class for dashboard auto-updates
- [ ] Loading indicators shown during fetch
- [ ] Error handling with user feedback (toast/alert)
- [ ] URL history updated (browser back/forward works)
- [ ] Pagination links have `ajax-link` class

### 20. Scroll Restoration (full-stack-django-patterns)
- [ ] AJAX updates preserve scroll position (save before, restore after)
- [ ] Use `requestAnimationFrame()` for scroll restoration after DOM update
- [ ] Include `scrollY` in `history.pushState()` state object
- [ ] Handle `popstate` event for browser back/forward scroll restore
- [ ] Form errors auto-scroll to first `.is-invalid` field
- [ ] Add `data-form-errors="true"` attribute for server-side errors
- [ ] New items scroll into view with highlight animation
- [ ] Anchor links use smooth scroll with navbar offset
- [ ] Back-to-top button visible after scrolling 300px
- [ ] CSS `scroll-padding-top` set for fixed navbar offset

### 21. Loading States & Feedback (ui-design-system)
- [ ] Long operations show progress indicator (ML inference, file upload)
- [ ] Progress bar with percentage and status message
- [ ] Estimated time remaining displayed
- [ ] Skeleton loaders for async data fetching
- [ ] Toast notifications for AJAX success/error feedback
- [ ] Button loading state (spinner + disabled) during submission
- [ ] `aria-busy="true"` on loading containers
- [ ] Multi-step forms show progress indicator
- [ ] Real-time validation shows inline feedback icons

### 22. Form State Persistence (full-stack-django-patterns)
- [ ] Django bound form retains values on validation errors (built-in)
- [ ] Important forms have `FormPersistence` class initialized
- [ ] Form data auto-saved to sessionStorage on input change (debounced)
- [ ] Form data restored on page load with "Draft restored" indicator
- [ ] Form data cleared on successful submit
- [ ] Passwords and CSRF tokens excluded from persistence (`data-no-persist="true"`)
- [ ] Server-rendered values preserved with `data-has-server-value="true"`
- [ ] Multi-step forms persist data across steps (FormWizardPersistence)
- [ ] localStorage used for non-sensitive drafts, sessionStorage for sensitive forms
- [ ] File inputs NEVER persisted (only file metadata displayed)

---

## Action Required

Please review the implementation against this checklist and fix any gaps found.

---

## Quick Reference Patterns

### Server-Side Validation
```python
def clean_field_name(self):
    value = self.cleaned_data.get('field_name', '').strip()
    if not value:
        raise ValidationError("Field is required.")
    if len(value) < 2:
        raise ValidationError("Must be at least 2 characters.")
    return value  # Return normalized value
```

### Client-Side Validation
```html
<input type="text" id="id_field" required minlength="2" maxlength="100">
<div class="invalid-feedback" id="field-feedback"></div>
```

```javascript
new FormValidator('formId', {
    field_name: {
        required: true,
        minLength: 2,
        maxLength: 100,
        normalize: 'lowercase',  // or 'titlecase'
        messages: { required: 'Field is required.' }
    }
});
```

### Malaysia Date/Time
```python
# Python - Always use timezone.now()
from django.utils import timezone
now = timezone.now()  # Malaysia time
today = timezone.now().date()  # Malaysia date
```

```django
{# Template - Use foundation tags #}
{% load common_tags %}
{% format_datetime appointment.scheduled_date %}
```

```javascript
// JavaScript - Format for Malaysia
date.toLocaleString('en-MY', {
    timeZone: 'Asia/Kuala_Lumpur',
    day: '2-digit', month: 'short', year: 'numeric',
    hour: 'numeric', minute: '2-digit', hour12: true
});
```

### Thin View Pattern
```python
# View should be < 50 lines, delegate to service
class UploadXRayView(LoginRequiredMixin, RoleRequiredMixin, FormView):
    template_name = "detection/upload.html"
    form_class = XRayUploadForm
    allowed_roles = [RoleChoices.ADMIN, RoleChoices.STAFF]

    def form_valid(self, form):
        # Delegate complex logic to service
        prediction = PredictionService.create_prediction_from_xray(
            xray_image_file=form.cleaned_data['image'],
            patient=form.cleaned_data['patient'],
            uploaded_by=self.request.user
        )
        return redirect('detection:results', pk=prediction.pk)
```

### Role-Based Access Control
```python
# View decorator
@login_required
@staff_required
def staff_only_view(request):
    pass

# CBV mixin
class StaffDashboardView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    allowed_roles = [RoleChoices.ADMIN, RoleChoices.STAFF]

# Template check
{% if user.profile.is_admin %}
    <!-- Admin content -->
{% elif user.profile.is_staff %}
    <!-- Staff content -->
{% endif %}
```

### Responsive Design
```html
<!-- Mobile-first grid -->
<div class="row g-4">
    <div class="col-12 col-sm-6 col-md-4 col-lg-3">
        <!-- Content -->
    </div>
</div>

<!-- Responsive table -->
<div class="table-responsive">
    <table class="table table-hover">...</table>
</div>

<!-- Responsive image -->
<img src="..." class="img-fluid" alt="Description">
```

### Model Base Classes
```python
from common.models import TimeStampedModel, FullAuditModel, TimeStampedSoftDeleteModel

# Minimum - ALL models must have this
class SimpleModel(TimeStampedModel):
    # Auto: created_at, updated_at
    name = models.CharField(max_length=100)

# Medical/sensitive data - full audit trail
class MedicalRecord(FullAuditModel):
    # Auto: created_at, updated_at, created_by, updated_by,
    #       is_deleted, deleted_at, deleted_by
    # Managers: objects (active), all_objects (all)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

# Deletable records - soft delete support
class Appointment(TimeStampedSoftDeleteModel):
    # Auto: created_at, updated_at, is_deleted, deleted_at, deleted_by
    # Managers: objects (active), all_objects (all)
    scheduled_date = models.DateTimeField()
```

**Base Model Selection Guide:**
| Data Type | Base Model | Fields Added |
|-----------|------------|--------------|
| All models (minimum) | `TimeStampedModel` | `created_at`, `updated_at` |
| Needs audit trail | `TimeStampedAuditableModel` | + `created_by`, `updated_by` |
| Needs soft delete | `TimeStampedSoftDeleteModel` | + `is_deleted`, `deleted_at`, `deleted_by` |
| Medical/sensitive | `FullAuditModel` | All of the above |

### Constants Pattern (MANDATORY)
```python
# module/constants.py - Every module MUST have this file
class StatusChoices:
    """Prediction status choices."""
    PENDING = 'pending'
    VALIDATED = 'validated'
    REJECTED = 'rejected'

    CHOICES = [
        (PENDING, 'Pending Validation'),
        (VALIDATED, 'Validated'),
        (REJECTED, 'Rejected'),
    ]

class DiagnosisDisplayNames:
    """Diagnosis display name mapping."""
    MAPPING = {
        'COVID': 'COVID-19 Positive',
        'Normal': 'Normal',
        'Viral Pneumonia': 'Viral Pneumonia',
    }

    @classmethod
    def get_display(cls, key: str) -> str:
        return cls.MAPPING.get(key, key)
```

### Query Optimization
```python
# ❌ BAD - N+1 query problem
predictions = Prediction.objects.all()
for p in predictions:
    print(p.xray.patient.user.username)  # 3 queries per iteration!

# ✅ GOOD - Single optimized query
predictions = Prediction.objects.select_related(
    'xray__patient__user'
).all()
for p in predictions:
    print(p.xray.patient.user.username)  # No additional queries

# ✅ GOOD - Prefetch for reverse/M2M
patients = Patient.objects.prefetch_related(
    'xrays', 'predictions'
).all()
```

### Pagination
```python
# View with pagination
class PatientListView(LoginRequiredMixin, ListView):
    model = Patient
    template_name = 'detection/patient_list.html'
    paginate_by = 25  # REQUIRED for list views

# Template pagination
{% load common_tags %}
{% render_pagination page_obj %}
```

### Healthcare UI - PHI Badge
```html
<div class="card-header bg-primary text-white d-flex justify-content-between">
    <h5 class="mb-0"><i class="bi bi-person-circle"></i> Patient Info</h5>
    <span class="badge bg-light text-primary">
        <i class="bi bi-shield-lock"></i> PHI Protected
    </span>
</div>
```

### Healthcare UI - Diagnosis Severity
```html
{% if diagnosis == 'COVID' %}
<div class="alert alert-danger" role="alert" aria-live="polite">
    <i class="bi bi-shield-exclamation"></i> <strong>COVID-19 Detected</strong>
</div>
{% elif diagnosis == 'Normal' %}
<div class="alert alert-success" role="alert">
    <i class="bi bi-shield-check"></i> <strong>Normal - No COVID-19</strong>
</div>
{% endif %}
```

### Rate Limiting (Login)
```python
from django.core.cache import cache

class RateLimitMixin:
    """Prevent brute force attacks"""
    def dispatch(self, request, *args, **kwargs):
        ip = self.get_client_ip(request)
        cache_key = f'login_attempts_{ip}'
        attempts = cache.get(cache_key, 0)

        if attempts >= 5:
            return HttpResponseForbidden("Too many login attempts. Try again in 15 minutes.")
        return super().dispatch(request, *args, **kwargs)

    def form_invalid(self, form):
        ip = self.get_client_ip(self.request)
        cache_key = f'login_attempts_{ip}'
        attempts = cache.get(cache_key, 0)
        cache.set(cache_key, attempts + 1, 900)  # 15 minutes
        return super().form_invalid(form)
```

### PHI Access Logging
```python
# Every PHI access must be logged
from audit.models import AccessLog

def patient_detail(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    # Log access (REQUIRED for all PHI)
    AccessLog.objects.create(
        user=request.user,
        action='VIEW',
        patient=patient,
        resource_type='Patient',
        resource_id=patient.id,
        ip_address=get_client_ip(request),
    )

    return render(request, 'patient_detail.html', {'patient': patient})
```

### Async Uniqueness Check (Client-Side)
```javascript
// Check uniqueness via API on blur
emailInput.addEventListener('blur', async function() {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const response = await fetch('/api/check-email/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ email: this.value })
    });
    const data = await response.json();
    if (data.exists) {
        setInvalid(this, 'Email already registered.');
    } else {
        setValid(this);
    }
});
```

### AJAX Partial Refresh - Server-Side View
```python
from django.template.loader import render_to_string

def is_ajax(request):
    """Check if request is AJAX"""
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'

@login_required
def prediction_list(request):
    predictions = Prediction.objects.select_related('xray__patient')
    paginator = Paginator(predictions, 25)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    context = {'predictions': page_obj, 'page_obj': page_obj}

    # Return partial for AJAX, full page otherwise
    if is_ajax(request):
        html = render_to_string(
            'detection/partials/prediction_table.html',
            context, request=request
        )
        return HttpResponse(html)

    return render(request, 'detection/prediction_list.html', context)
```

### AJAX Partial Refresh - Template Structure
```django
{# Main template: prediction_list.html #}
{% extends "base.html" %}
{% block content %}
<div id="predictions-container">
    {% include "detection/partials/prediction_table.html" %}
</div>
{% endblock %}

{# Partial template: partials/prediction_table.html #}
{# ⭐ NO extends - this is a fragment #}
{% load common_tags %}
<table class="table">
    {% for p in predictions %}
    <tr id="row-{{ p.id }}">...</tr>
    {% endfor %}
</table>
{% render_pagination page_obj %}
```

### AJAX Partial Refresh - JavaScript
```javascript
// Initialize partial refresh
const refresh = new PartialRefresh({
    containerId: 'predictions-container',
    filterFormId: 'filter-form',
    url: '/predictions/'
});

// Auto-refresh for dashboards (every 30s)
const autoRefresh = new AutoRefresh({
    containerId: 'dashboard-stats',
    url: '/partials/stats/',
    interval: 30000
});
```

### Scroll Restoration - AJAX Update
```javascript
// Preserve scroll during AJAX update
async loadUrl(url) {
    const scrollY = window.scrollY;  // ⭐ Save BEFORE

    const response = await fetch(url, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    });
    container.innerHTML = await response.text();

    // ⭐ Restore AFTER DOM update
    requestAnimationFrame(() => window.scrollTo(0, scrollY));

    // Include in history state
    history.pushState({ scrollY: scrollY }, '', url);
}

// Handle browser back/forward
window.addEventListener('popstate', (e) => {
    if (e.state?.scrollY !== undefined) {
        setTimeout(() => window.scrollTo(0, e.state.scrollY), 100);
    }
});
```

### Scroll Restoration - Form Errors
```django
{# Template: Add flag for errors #}
<form id="my-form" {% if form_has_errors %}data-form-errors="true"{% endif %}>
```

```javascript
// Auto-scroll to first error on page load
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('[data-form-errors="true"]');
    if (form) {
        const firstError = form.querySelector('.is-invalid');
        if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            firstError.focus();
        }
    }
});
```

### Scroll Restoration - New Item Highlight
```javascript
// Scroll to and highlight newly created item
const newRow = document.getElementById(`row-${data.id}`);
if (newRow) {
    newRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
    newRow.classList.add('highlight-new');
    setTimeout(() => newRow.classList.remove('highlight-new'), 3000);
}
```

```css
/* CSS highlight animation */
@keyframes highlightNew {
    0% { background-color: #cce5ff; }
    100% { background-color: transparent; }
}
tr.highlight-new { animation: highlightNew 3s ease-out; }

/* Fixed navbar scroll offset */
html { scroll-padding-top: 80px; }
```

### Loading States - Button Spinner
```html
<!-- Button with loading state -->
<button type="submit" id="submit-btn" class="btn btn-primary">
    <span class="btn-text">Save</span>
    <span class="btn-loading d-none">
        <span class="spinner-border spinner-border-sm me-1"></span>
        Saving...
    </span>
</button>
```

```javascript
// Toggle button loading state
function setButtonLoading(btn, loading) {
    btn.disabled = loading;
    btn.querySelector('.btn-text').classList.toggle('d-none', loading);
    btn.querySelector('.btn-loading').classList.toggle('d-none', !loading);
}
```

### Loading States - Skeleton Loader
```html
<!-- Skeleton loader for patient card -->
<div class="card skeleton-loader" aria-busy="true" aria-label="Loading...">
    <div class="card-body">
        <div class="skeleton skeleton-text mb-2" style="width: 60%;"></div>
        <div class="skeleton skeleton-text" style="width: 40%;"></div>
    </div>
</div>
```

```css
.skeleton {
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: loading 1.5s infinite;
}
.skeleton-text { height: 16px; border-radius: 4px; }
@keyframes loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}
```

### Loading States - Progress Modal (ML Inference)
```html
<div class="modal" id="processing-modal" data-bs-backdrop="static">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content text-center p-4">
            <h5>Analyzing X-Ray...</h5>
            <div class="progress mb-3" style="height: 25px;">
                <div id="progress-bar" class="progress-bar progress-bar-striped progress-bar-animated"
                     role="progressbar" style="width: 0%">0%</div>
            </div>
            <p id="status-message" class="text-muted small">Preprocessing image...</p>
        </div>
    </div>
</div>
```

### Form State Persistence - Django Server-Side (Built-in)
```python
# Django automatically retains form values on validation errors
# When form.is_valid() is False, the bound form preserves all values

def patient_registration(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)  # Bound form with data
        if form.is_valid():
            form.save()
            return redirect('success')
        # form still has all user input - renders with errors AND values
    else:
        form = PatientForm()  # Unbound form - empty
    return render(request, 'registration.html', {'form': form})
```

### Form State Persistence - Client-Side (JavaScript)
```javascript
// Initialize persistence on important forms
const formPersistence = new FormPersistence({
    formId: 'patient-form',
    storageKey: 'patient_registration_draft',  // Optional custom key
    useLocalStorage: false,  // Use sessionStorage (default, more secure)
    excludeFields: ['password', 'password1', 'password2'],  // Never persist
    onRestore: function() {
        showToast('Draft restored from your previous session', 'info');
    }
});

// Clear on successful submit
document.getElementById('patient-form').addEventListener('submit', function(e) {
    if (this.checkValidity()) {
        formPersistence.clear();
    }
});
```

### Form State Persistence - Template Integration
```django
{# Mark fields that should NOT be persisted #}
<input type="password" name="password" data-no-persist="true">
<input type="hidden" name="csrfmiddlewaretoken" data-no-persist="true">

{# Mark fields with server-rendered values (don't overwrite) #}
{% if form.email.value %}
<input type="email" name="email" value="{{ form.email.value }}" data-has-server-value="true">
{% else %}
<input type="email" name="email">
{% endif %}

{# Initialize persistence #}
<script>
document.addEventListener('DOMContentLoaded', function() {
    new FormPersistence({ formId: 'registration-form' });
});
</script>
```

### Form State Persistence - Multi-Step Wizard
```javascript
// For multi-step forms, persist across all steps
const wizardPersistence = new FormWizardPersistence({
    wizardId: 'registration-wizard',
    steps: ['personal-info', 'contact-info', 'medical-history'],
    storageKey: 'registration_wizard_data'
});

// Navigate between steps
function nextStep(currentStep) {
    wizardPersistence.saveStep(currentStep);
    wizardPersistence.showStep(currentStep + 1);
}

// Clear all data on final submit
function submitWizard() {
    const allData = wizardPersistence.getAllData();
    // Submit allData to server...
    wizardPersistence.clearAll();
}
```
