# Dual-Layer Validation Skill - Quick Reference

**Created:** 2025-11-24
**Skill Location:** `.claude/skills/dual-layer-validation/skill.md`
**Status:** Active - Auto-applies to all user inputs

---

## What This Skill Does

The **Dual-Layer Validation** skill enforces a defense-in-depth approach to input validation by ensuring that **BOTH** server-side and client-side validation are implemented for all user inputs.

### Core Principle: Defense in Depth

```
┌─────────────────────────────────────────┐
│  CLIENT-SIDE VALIDATION (Layer 1)      │  ← User Experience
│  - HTML5 validation attributes          │  ← Instant feedback
│  - JavaScript real-time validation      │  ← Prevents bad UX
│  - Async uniqueness checks              │  ← Can be bypassed!
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  SERVER-SIDE VALIDATION (Layer 2)      │  ← Security Boundary
│  - Django form validation               │  ← MANDATORY
│  - DRF serializer validation            │  ← Cannot be bypassed
│  - Model-level validation               │  ← Last line of defense
└─────────────────────────────────────────┘
```

**Key Rule:** Server-side validation is the **security boundary**. Client-side validation is a **UX enhancement**.

---

## When This Skill Auto-Triggers

The skill automatically applies when you:

- ✅ Create any Django form (`forms.py`)
- ✅ Create any DRF serializer (`serializers.py`)
- ✅ Add model fields with constraints (`models.py`)
- ✅ Implement file upload functionality
- ✅ Create API endpoints that accept user input
- ✅ Write JavaScript that accepts user input
- ✅ Implement search or filter functionality
- ✅ Create registration or profile update forms

**Critical Rule:** Every user input field must have validation on BOTH sides.

---

## Quick Implementation Guide

### 1. Server-Side Validation (Django Forms)

```python
from django import forms
from common.widgets import BootstrapTextInput, BootstrapEmailInput
from common.utils import validate_phone, validate_nric

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'ic_number', 'phone', 'email']
        widgets = {
            'name': BootstrapTextInput(),
            'ic_number': BootstrapTextInput(),
            'phone': BootstrapTextInput(),
            'email': BootstrapEmailInput(),
        }

    # ✅ Field-level validation
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or len(name.strip()) < 2:
            raise forms.ValidationError("Name must be at least 2 characters.")
        return name.strip()

    def clean_ic_number(self):
        ic_number = self.cleaned_data.get('ic_number')
        if not validate_nric(ic_number):
            raise forms.ValidationError("Invalid Malaysian IC number format.")
        return ic_number

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not validate_phone(phone):
            raise forms.ValidationError("Invalid Malaysian phone number.")
        return phone

    # ✅ Form-level validation (cross-field)
    def clean(self):
        cleaned_data = super().clean()
        # Cross-field validation logic here
        return cleaned_data
```

---

### 2. Client-Side Validation (HTML5 + JavaScript)

```django
<!-- Template: patient_form.html -->
<form method="post" novalidate>
    {% csrf_token %}

    <!-- Name Field -->
    <div class="mb-3">
        <label for="{{ form.name.id_for_label }}" class="form-label">
            Full Name <span class="text-danger">*</span>
        </label>
        {{ form.name }}
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const nameInput = document.getElementById('{{ form.name.id_for_label }}');
                nameInput.required = true;
                nameInput.minLength = 2;
                nameInput.maxLength = 200;
                nameInput.pattern = "[A-Za-z '-.]+(?: [A-Za-z '-\\.]+)*";
            });
        </script>
    </div>

    <!-- IC Number Field -->
    <div class="mb-3">
        <label for="{{ form.ic_number.id_for_label }}" class="form-label">
            IC Number <span class="text-danger">*</span>
        </label>
        {{ form.ic_number }}
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const icInput = document.getElementById('{{ form.ic_number.id_for_label }}');
                icInput.required = true;
                icInput.pattern = "\\d{6}-\\d{2}-\\d{4}";
                icInput.placeholder = "XXXXXX-XX-XXXX";
            });
        </script>
    </div>

    <button type="submit" class="btn btn-primary">Submit</button>
</form>
```

---

### 3. Real-Time JavaScript Validation

```javascript
// static/js/validation.js

document.addEventListener('DOMContentLoaded', function() {
    const icInput = document.querySelector('#id_ic_number');

    if (icInput) {
        icInput.addEventListener('input', function() {
            const icPattern = /^\d{6}-\d{2}-\d{4}$/;
            const value = this.value.trim();

            if (!icPattern.test(value)) {
                setInvalid(this, 'IC number must be in format: XXXXXX-XX-XXXX');
            } else {
                setValid(this);
            }
        });
    }
});

function setInvalid(input, message) {
    input.classList.remove('is-valid');
    input.classList.add('is-invalid');
    // Show error message
    let feedback = input.parentElement.querySelector('.invalid-feedback');
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        input.parentElement.appendChild(feedback);
    }
    feedback.textContent = message;
    feedback.style.display = 'block';
}

function setValid(input) {
    input.classList.remove('is-invalid');
    input.classList.add('is-valid');
    const feedback = input.parentElement.querySelector('.invalid-feedback');
    if (feedback) {
        feedback.style.display = 'none';
    }
}
```

---

## Validation Utilities (`common/utils.py`)

The skill includes centralized validation utilities that should be used across the application:

```python
# Already in common/utils.py or ADD these:

def validate_nric(nric: str) -> bool:
    """Validate Malaysian IC number format (XXXXXX-XX-XXXX)"""
    import re
    if not nric:
        return False
    pattern = r'^\d{6}-\d{2}-\d{4}$'
    return bool(re.match(pattern, nric.strip()))

def validate_phone(phone: str) -> bool:
    """Validate Malaysian phone number (01X-XXXXXXX)"""
    import re
    if not phone:
        return False
    pattern = r'^01[0-9]-\d{7,8}$'
    return bool(re.match(pattern, phone.strip()))

def validate_image_file(file, max_size_mb: int = 10) -> bool:
    """Validate uploaded image file"""
    if not file:
        return False
    # Check size
    max_size_bytes = max_size_mb * 1024 * 1024
    if file.size > max_size_bytes:
        return False
    # Check extension
    from pathlib import Path
    allowed_extensions = ['.jpg', '.jpeg', '.png']
    ext = Path(file.name).suffix.lower()
    return ext in allowed_extensions
```

---

## Validation Checklist

Before deploying any feature with user input, verify:

### Server-Side (MANDATORY):
- ✅ All form fields have `clean_<field>()` methods
- ✅ All forms have `clean()` method for cross-field validation
- ✅ All API serializers have `validate_<field>()` methods
- ✅ All model fields have appropriate validators
- ✅ File uploads validate type, size, and MIME type
- ✅ Uniqueness constraints are checked in validation
- ✅ Business rules are enforced in validation

### Client-Side (MANDATORY):
- ✅ All input fields have HTML5 validation attributes (required, pattern, min, max)
- ✅ Custom JavaScript validation for complex rules
- ✅ Real-time validation feedback (on input/blur events)
- ✅ File uploads validate type and size before submission
- ✅ Form submission is blocked if validation fails
- ✅ Clear error messages are displayed
- ✅ Visual feedback (is-valid/is-invalid classes)

### Both Layers:
- ✅ Error messages are consistent between client and server
- ✅ Validation rules are consistent between client and server
- ✅ Server-side validation is NEVER bypassed
- ✅ Client-side validation enhances UX but doesn't replace security

---

## Common Patterns

### Pattern 1: Required Field with Length Constraint

**Server:**
```python
def clean_name(self):
    name = self.cleaned_data.get('name')
    if not name or len(name) < 2:
        raise forms.ValidationError("Name must be at least 2 characters.")
    return name.strip()
```

**Client:**
```html
<input type="text" id="id_name" required minlength="2" maxlength="200">
```

---

### Pattern 2: Email with Uniqueness Check

**Server:**
```python
def clean_email(self):
    email = self.cleaned_data.get('email')
    if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
        raise forms.ValidationError("Email already registered.")
    return email.lower()
```

**Client:**
```javascript
emailInput.addEventListener('blur', async function() {
    const response = await fetch('/api/check-email/', {
        method: 'POST',
        body: JSON.stringify({ email: this.value })
    });
    const data = await response.json();
    if (data.exists) {
        setInvalid(this, 'Email already registered.');
    }
});
```

---

### Pattern 3: Date Range Validation

**Server:**
```python
def clean_date_of_birth(self):
    dob = self.cleaned_data.get('date_of_birth')
    from datetime import date
    if dob > date.today():
        raise forms.ValidationError("Date cannot be in future.")
    return dob
```

**Client:**
```javascript
dobInput.max = new Date().toISOString().split('T')[0];
```

---

### Pattern 4: File Upload Validation

**Server:**
```python
def clean_original_image(self):
    image = self.cleaned_data.get('original_image')
    from common.utils import validate_image_file
    if not validate_image_file(image, max_size_mb=10):
        raise forms.ValidationError("Invalid image or size exceeds 10MB.")
    return image
```

**Client:**
```javascript
fileInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file.size > 10 * 1024 * 1024) {
        setInvalid(this, 'File must be under 10MB.');
        this.value = '';  // Clear invalid file
    }
});
```

---

## Anti-Patterns (NEVER DO THIS)

### ❌ Client-Side Only Validation (SECURITY VULNERABILITY)

```python
# ❌ WRONG - No server-side validation
class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'email']
    # ❌ Missing clean_* methods - CAN BE BYPASSED!
```

**Why Wrong:** Attackers can bypass client-side validation using curl, Postman, or browser dev tools.

---

### ❌ No Client-Side Validation (POOR UX)

```html
<!-- ❌ No client-side validation -->
<input type="text" id="id_name">  <!-- No required, no pattern -->
```

**Why Wrong:** Poor user experience - users only see errors after form submission.

---

### ❌ Inconsistent Error Messages

**Server:** `"Invalid IC number format."`
**Client:** `"IC number is wrong."`

**Why Wrong:** Confuses users - keep messages consistent.

---

## Integration with Existing Skills

### With `security-best-practices`:
- Server-side validation is the **security boundary**
- This skill enforces validation **implementation**
- Security skill enforces **WHAT** to validate (injection, XSS, etc.)

### With `foundation-components`:
- Use `common.widgets` for form rendering
- Use `common.utils` for validation logic
- Use Bootstrap classes for validation feedback

### With `full-stack-django-patterns`:
- Follow form patterns for validation structure
- Use service layer for complex cross-model validation

---

## Success Metrics

With this skill properly applied, you should achieve:

- ✅ **Zero bypassed validations** - All server-side validation in place
- ✅ **Excellent UX** - Real-time feedback on all forms
- ✅ **Consistent errors** - Same messages on client and server
- ✅ **Security** - Defense in depth principle enforced
- ✅ **Maintainability** - Centralized validation utilities

---

## Quick Start

1. **For Forms:** Add `clean_<field>()` methods for each field
2. **For Templates:** Add HTML5 validation attributes to all inputs
3. **For JavaScript:** Add real-time validation event listeners
4. **For APIs:** Add `validate_<field>()` methods to serializers
5. **For Files:** Use `validate_image_file()` utility on both sides

**Remember:** Server-side = Security, Client-side = UX, Both = Excellence!

---

**Full Skill Documentation:** `.claude/skills/dual-layer-validation/skill.md` (850+ lines)

**Status:** Active and auto-applying to all user input handling
