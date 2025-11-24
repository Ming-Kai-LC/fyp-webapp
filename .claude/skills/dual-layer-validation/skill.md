---
name: Dual-Layer Validation
description: Enforces both server-side and client-side validation for all user inputs. Server-side validation is MANDATORY for security, client-side validation is MANDATORY for UX. Auto-applies to all forms, APIs, and user input handling.
---

# Dual-Layer Validation

**Version:** 1.0.0
**Last Updated:** 2025-11-24
**Status:** ⭐ CRITICAL - Defense in depth principle
**Auto-apply:** YES - Every time you handle user input

---

## Core Validation Principles

### 1. **Defense in Depth**
- **Server-side validation: MANDATORY** - Never trust the client (security)
- **Client-side validation: MANDATORY** - Immediate feedback (UX)
- **Both layers must be implemented** - No exceptions

### 2. **Security First**
- Server-side validation is the **security boundary**
- Client-side validation is a **UX enhancement**
- If you implement only one, implement server-side

### 3. **Fail Securely**
- Invalid input must be rejected with clear error messages
- Never silently accept invalid data
- Log validation failures for suspicious patterns

---

## When This Skill Auto-Triggers

**ALWAYS apply when:**
- Creating any Django form
- Creating any DRF serializer
- Adding model fields with constraints
- Implementing file upload functionality
- Creating API endpoints that accept user input
- Writing JavaScript that accepts user input
- Implementing search or filter functionality
- Creating registration or profile update forms

**Critical Rule:** Every user input field must have validation on BOTH sides.

---

## Part 1: Server-Side Validation (Django)

### Django Forms - Primary Validation Layer

#### Pattern 1: Field-Level Validation

**✅ CORRECT:**
```python
from django import forms
from common.widgets import BootstrapTextInput, BootstrapEmailInput
from common.utils import validate_phone, validate_nric
from django.core.validators import MinLengthValidator, RegexValidator

class PatientRegistrationForm(forms.ModelForm):
    """Server-side validation is MANDATORY"""

    class Meta:
        model = Patient
        fields = ['name', 'ic_number', 'phone', 'email', 'date_of_birth']
        widgets = {
            'name': BootstrapTextInput(attrs={'placeholder': 'Full Name'}),
            'ic_number': BootstrapTextInput(attrs={'placeholder': 'XXXXXX-XX-XXXX'}),
            'phone': BootstrapTextInput(attrs={'placeholder': '01X-XXXXXXX'}),
            'email': BootstrapEmailInput(),
            'date_of_birth': BootstrapDateInput(),
        }

    # ✅ Field-level validation methods
    def clean_name(self):
        """Validate name field"""
        name = self.cleaned_data.get('name')

        # 1. Required check (even if field has blank=False)
        if not name or not name.strip():
            raise forms.ValidationError("Name is required.")

        # 2. Length check
        if len(name.strip()) < 2:
            raise forms.ValidationError("Name must be at least 2 characters.")

        # 3. Character validation
        if not all(c.isalpha() or c.isspace() or c in "'-." for c in name):
            raise forms.ValidationError("Name contains invalid characters.")

        return name.strip()

    def clean_ic_number(self):
        """Validate Malaysian IC number"""
        ic_number = self.cleaned_data.get('ic_number')

        # Use centralized validation utility
        if not validate_nric(ic_number):
            raise forms.ValidationError("Invalid Malaysian IC number format.")

        # Check uniqueness
        if Patient.objects.filter(ic_number=ic_number).exists():
            if not self.instance.pk or self.instance.ic_number != ic_number:
                raise forms.ValidationError("This IC number is already registered.")

        return ic_number

    def clean_phone(self):
        """Validate Malaysian phone number"""
        phone = self.cleaned_data.get('phone')

        # Use centralized validation utility
        if not validate_phone(phone):
            raise forms.ValidationError(
                "Invalid phone number. Must be Malaysian format (01X-XXXXXXX)."
            )

        return phone

    def clean_email(self):
        """Validate email"""
        email = self.cleaned_data.get('email')

        # Django EmailField already validates format
        # Add uniqueness check
        if User.objects.filter(email=email).exists():
            if not self.instance.pk or self.instance.user.email != email:
                raise forms.ValidationError("This email is already registered.")

        return email.lower()  # Normalize to lowercase

    def clean_date_of_birth(self):
        """Validate date of birth"""
        dob = self.cleaned_data.get('date_of_birth')

        from datetime import date
        from common.utils import calculate_age

        # 1. Must not be in future
        if dob > date.today():
            raise forms.ValidationError("Date of birth cannot be in the future.")

        # 2. Age validation
        age = calculate_age(dob)
        if age < 1:
            raise forms.ValidationError("Patient must be at least 1 year old.")
        if age > 150:
            raise forms.ValidationError("Invalid date of birth.")

        return dob
```

**❌ WRONG:**
```python
class PatientRegistrationForm(forms.ModelForm):
    """❌ NO validation - security vulnerability!"""

    class Meta:
        model = Patient
        fields = ['name', 'ic_number', 'phone', 'email']
        # ❌ Missing clean_* methods
        # ❌ No validation logic
        # ❌ Trusting client-side validation only - NEVER DO THIS!
```

---

#### Pattern 2: Form-Level Validation

**✅ CORRECT:**
```python
class XRayUploadForm(forms.ModelForm):
    """Validate across multiple fields"""

    class Meta:
        model = XRayImage
        fields = ['patient', 'original_image', 'notes']

    def clean_original_image(self):
        """Validate uploaded image"""
        image = self.cleaned_data.get('original_image')

        from common.utils import validate_image_file

        # 1. Use centralized validation
        if not validate_image_file(image, max_size_mb=10):
            raise forms.ValidationError(
                "Invalid image file. Must be JPEG/PNG and under 10MB."
            )

        # 2. Check MIME type (prevent extension spoofing)
        import magic
        mime = magic.from_buffer(image.read(1024), mime=True)
        image.seek(0)  # Reset file pointer

        allowed_mimes = ['image/jpeg', 'image/png']
        if mime not in allowed_mimes:
            raise forms.ValidationError(
                f"Invalid file format: {mime}. Only JPEG/PNG allowed."
            )

        return image

    def clean(self):
        """Form-level validation (multiple fields)"""
        cleaned_data = super().clean()
        patient = cleaned_data.get('patient')
        image = cleaned_data.get('original_image')

        # Validate relationship between fields
        if patient and image:
            # Check if patient already has X-ray today (business rule)
            from django.utils import timezone
            today = timezone.now().date()

            existing_today = XRayImage.objects.filter(
                patient=patient,
                created_at__date=today
            ).exists()

            if existing_today:
                raise forms.ValidationError(
                    "Patient already has an X-ray uploaded today. "
                    "Please use the existing X-ray or contact admin."
                )

        return cleaned_data
```

---

### Django Model Validation

**✅ CORRECT:**
```python
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from common.models import FullAuditModel

class Patient(FullAuditModel):
    """Model-level validation (last line of defense)"""

    name = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(2, "Name must be at least 2 characters.")]
    )

    ic_number = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{6}-\d{2}-\d{4}$',
                message="IC number must be in format: XXXXXX-XX-XXXX"
            )
        ]
    )

    phone = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^01[0-9]-\d{7,8}$',
                message="Phone must be Malaysian format: 01X-XXXXXXX"
            )
        ]
    )

    age = models.IntegerField(
        validators=[
            MinValueValidator(1, "Age must be at least 1."),
            MaxValueValidator(150, "Invalid age.")
        ]
    )

    def clean(self):
        """Model-level validation"""
        super().clean()

        # Cross-field validation
        from datetime import date
        if self.date_of_birth and self.date_of_birth > date.today():
            raise ValidationError("Date of birth cannot be in the future.")

    def save(self, *args, **kwargs):
        """Validate before saving"""
        self.full_clean()  # ✅ Always call full_clean() before save
        super().save(*args, **kwargs)
```

**Why:** Model validation provides the **final defense layer** if form validation is bypassed.

---

### DRF Serializer Validation

**✅ CORRECT:**
```python
from rest_framework import serializers
from detection.models import Patient
from common.utils import validate_phone, validate_nric

class PatientSerializer(serializers.ModelSerializer):
    """API input validation"""

    class Meta:
        model = Patient
        fields = ['id', 'name', 'ic_number', 'phone', 'email', 'date_of_birth', 'age']
        read_only_fields = ['id', 'age']

    # ✅ Field-level validation
    def validate_name(self, value):
        """Validate name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Name is required.")

        if len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters.")

        return value.strip()

    def validate_ic_number(self, value):
        """Validate IC number"""
        if not validate_nric(value):
            raise serializers.ValidationError("Invalid Malaysian IC number format.")

        # Check uniqueness (excluding current instance)
        queryset = Patient.objects.filter(ic_number=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError("IC number already registered.")

        return value

    def validate_phone(self, value):
        """Validate phone"""
        if not validate_phone(value):
            raise serializers.ValidationError("Invalid Malaysian phone number.")

        return value

    def validate_email(self, value):
        """Validate email"""
        # EmailField already validates format
        from django.contrib.auth.models import User

        queryset = User.objects.filter(email=value)
        if self.instance and self.instance.user:
            queryset = queryset.exclude(pk=self.instance.user.pk)

        if queryset.exists():
            raise serializers.ValidationError("Email already registered.")

        return value.lower()

    def validate_date_of_birth(self, value):
        """Validate date of birth"""
        from datetime import date

        if value > date.today():
            raise serializers.ValidationError("Date of birth cannot be in future.")

        from common.utils import calculate_age
        age = calculate_age(value)
        if age < 1 or age > 150:
            raise serializers.ValidationError("Invalid date of birth.")

        return value

    # ✅ Object-level validation
    def validate(self, data):
        """Cross-field validation"""
        # Example: Validate age matches date_of_birth
        if 'date_of_birth' in data:
            from common.utils import calculate_age
            calculated_age = calculate_age(data['date_of_birth'])

            if 'age' in data and data['age'] != calculated_age:
                raise serializers.ValidationError({
                    'age': f"Age must match date of birth (should be {calculated_age})."
                })

        return data
```

**Why:** API endpoints need validation just like web forms - **never trust client input**.

---

## Part 2: Client-Side Validation (HTML5 + JavaScript)

### HTML5 Native Validation

**✅ CORRECT:**
```django
<!-- templates/accounts/register.html -->
{% extends "base.html" %}
{% load common_tags %}

{% block content %}
<form method="post" novalidate>  {# novalidate lets you customize error messages #}
    {% csrf_token %}

    <!-- Name Field -->
    <div class="mb-3">
        <label for="{{ form.name.id_for_label }}" class="form-label">
            Full Name <span class="text-danger">*</span>
        </label>
        {{ form.name }}
        {# ✅ HTML5 validation attributes #}
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const nameInput = document.getElementById('{{ form.name.id_for_label }}');
                nameInput.required = true;
                nameInput.minLength = 2;
                nameInput.maxLength = 200;
                nameInput.pattern = "[A-Za-z '-.]+(?: [A-Za-z '-\\.]+)*";
                nameInput.title = "Name can only contain letters, spaces, hyphens, apostrophes, and periods";
            });
        </script>
        {% if form.name.errors %}
            <div class="invalid-feedback d-block">{{ form.name.errors.0 }}</div>
        {% endif %}
    </div>

    <!-- IC Number Field -->
    <div class="mb-3">
        <label for="{{ form.ic_number.id_for_label }}" class="form-label">
            IC Number <span class="text-danger">*</span>
        </label>
        {{ form.ic_number }}
        {# ✅ Pattern validation for Malaysian IC #}
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const icInput = document.getElementById('{{ form.ic_number.id_for_label }}');
                icInput.required = true;
                icInput.pattern = "\\d{6}-\\d{2}-\\d{4}";
                icInput.placeholder = "XXXXXX-XX-XXXX";
                icInput.title = "IC number must be in format: XXXXXX-XX-XXXX";
            });
        </script>
        <small class="form-text text-muted">Format: XXXXXX-XX-XXXX</small>
        {% if form.ic_number.errors %}
            <div class="invalid-feedback d-block">{{ form.ic_number.errors.0 }}</div>
        {% endif %}
    </div>

    <!-- Phone Field -->
    <div class="mb-3">
        <label for="{{ form.phone.id_for_label }}" class="form-label">
            Phone Number <span class="text-danger">*</span>
        </label>
        {{ form.phone }}
        {# ✅ Pattern validation for Malaysian phone #}
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const phoneInput = document.getElementById('{{ form.phone.id_for_label }}');
                phoneInput.required = true;
                phoneInput.type = 'tel';
                phoneInput.pattern = "01[0-9]-\\d{7,8}";
                phoneInput.placeholder = "01X-XXXXXXX";
                phoneInput.title = "Phone must be Malaysian format: 01X-XXXXXXX";
            });
        </script>
        <small class="form-text text-muted">Format: 01X-XXXXXXX</small>
        {% if form.phone.errors %}
            <div class="invalid-feedback d-block">{{ form.phone.errors.0 }}</div>
        {% endif %}
    </div>

    <!-- Email Field -->
    <div class="mb-3">
        <label for="{{ form.email.id_for_label }}" class="form-label">
            Email <span class="text-danger">*</span>
        </label>
        {{ form.email }}
        {# ✅ Email validation built-in #}
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const emailInput = document.getElementById('{{ form.email.id_for_label }}');
                emailInput.required = true;
                emailInput.type = 'email';
            });
        </script>
        {% if form.email.errors %}
            <div class="invalid-feedback d-block">{{ form.email.errors.0 }}</div>
        {% endif %}
    </div>

    <!-- Date of Birth Field -->
    <div class="mb-3">
        <label for="{{ form.date_of_birth.id_for_label }}" class="form-label">
            Date of Birth <span class="text-danger">*</span>
        </label>
        {{ form.date_of_birth }}
        {# ✅ Date validation #}
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const dobInput = document.getElementById('{{ form.date_of_birth.id_for_label }}');
                dobInput.required = true;
                dobInput.type = 'date';
                // Max date is today
                dobInput.max = new Date().toISOString().split('T')[0];
                // Min date is 150 years ago
                const minDate = new Date();
                minDate.setFullYear(minDate.getFullYear() - 150);
                dobInput.min = minDate.toISOString().split('T')[0];
            });
        </script>
        {% if form.date_of_birth.errors %}
            <div class="invalid-feedback d-block">{{ form.date_of_birth.errors.0 }}</div>
        {% endif %}
    </div>

    <button type="submit" class="btn btn-primary">Register</button>
</form>
{% endblock %}
```

**Why:** HTML5 validation provides **instant feedback** before form submission - excellent UX.

---

### JavaScript Real-Time Validation

**✅ CORRECT:**
```javascript
// static/js/validation.js

/**
 * Real-time validation for patient registration form
 */
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');

    // ✅ Real-time IC number validation
    const icInput = document.querySelector('#id_ic_number');
    if (icInput) {
        icInput.addEventListener('input', function() {
            validateICNumber(this);
        });
    }

    // ✅ Real-time phone validation
    const phoneInput = document.querySelector('#id_phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function() {
            validatePhone(this);
        });
    }

    // ✅ Real-time email validation
    const emailInput = document.querySelector('#id_email');
    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            validateEmailAsync(this);  // Check uniqueness via API
        });
    }

    // ✅ Form submission validation
    form.addEventListener('submit', function(e) {
        if (!validateForm()) {
            e.preventDefault();
            showAlert('Please fix the validation errors before submitting.', 'danger');
        }
    });
});

/**
 * Validate IC number format
 */
function validateICNumber(input) {
    const icPattern = /^\d{6}-\d{2}-\d{4}$/;
    const value = input.value.trim();

    if (!value) {
        setInvalid(input, 'IC number is required.');
        return false;
    }

    if (!icPattern.test(value)) {
        setInvalid(input, 'IC number must be in format: XXXXXX-XX-XXXX');
        return false;
    }

    setValid(input);
    return true;
}

/**
 * Validate phone number format
 */
function validatePhone(input) {
    const phonePattern = /^01[0-9]-\d{7,8}$/;
    const value = input.value.trim();

    if (!value) {
        setInvalid(input, 'Phone number is required.');
        return false;
    }

    if (!phonePattern.test(value)) {
        setInvalid(input, 'Phone must be Malaysian format: 01X-XXXXXXX');
        return false;
    }

    setValid(input);
    return true;
}

/**
 * Validate email uniqueness (async check)
 */
async function validateEmailAsync(input) {
    const value = input.value.trim();

    if (!value) {
        setInvalid(input, 'Email is required.');
        return false;
    }

    // Basic email format check
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(value)) {
        setInvalid(input, 'Invalid email format.');
        return false;
    }

    // ✅ Check uniqueness via API
    try {
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const response = await fetch('/api/check-email/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({ email: value })
        });

        const data = await response.json();

        if (data.exists) {
            setInvalid(input, 'This email is already registered.');
            return false;
        }

        setValid(input);
        return true;
    } catch (error) {
        console.error('Email validation error:', error);
        // Don't block form submission on network error
        return true;
    }
}

/**
 * Validate entire form
 */
function validateForm() {
    let isValid = true;

    // Validate all required fields
    const requiredInputs = document.querySelectorAll('input[required]');
    requiredInputs.forEach(input => {
        if (!input.value.trim()) {
            setInvalid(input, 'This field is required.');
            isValid = false;
        }
    });

    return isValid;
}

/**
 * Mark input as invalid
 */
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

/**
 * Mark input as valid
 */
function setValid(input) {
    input.classList.remove('is-invalid');
    input.classList.add('is-valid');

    // Hide error message
    const feedback = input.parentElement.querySelector('.invalid-feedback');
    if (feedback) {
        feedback.style.display = 'none';
    }
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}
```

**Why:** Real-time JavaScript validation provides the **best UX** - users see errors as they type.

---

### File Upload Validation (Client-Side)

**✅ CORRECT:**
```javascript
// static/js/file-upload-validation.js

/**
 * Validate X-ray image upload (client-side)
 */
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.querySelector('#id_original_image');
    const previewImg = document.querySelector('#image-preview');
    const uploadBtn = document.querySelector('#upload-btn');

    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];

            if (!file) {
                return;
            }

            // ✅ Validate file type (client-side check)
            const allowedTypes = ['image/jpeg', 'image/png'];
            if (!allowedTypes.includes(file.type)) {
                setInvalid(fileInput, 'Only JPEG and PNG images are allowed.');
                fileInput.value = '';  // Clear invalid file
                return;
            }

            // ✅ Validate file size (10MB limit)
            const maxSize = 10 * 1024 * 1024;  // 10MB
            if (file.size > maxSize) {
                setInvalid(fileInput, 'File size must be under 10MB.');
                fileInput.value = '';  // Clear invalid file
                return;
            }

            // ✅ Validate image dimensions (optional)
            const reader = new FileReader();
            reader.onload = function(e) {
                const img = new Image();
                img.onload = function() {
                    const minWidth = 224;
                    const minHeight = 224;

                    if (img.width < minWidth || img.height < minHeight) {
                        setInvalid(
                            fileInput,
                            `Image must be at least ${minWidth}x${minHeight} pixels.`
                        );
                        fileInput.value = '';
                        return;
                    }

                    // Show preview
                    if (previewImg) {
                        previewImg.src = e.target.result;
                        previewImg.style.display = 'block';
                    }

                    setValid(fileInput);
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);

            setValid(fileInput);
        });
    }
});
```

**Why:** Client-side file validation prevents unnecessary uploads and provides instant feedback.

---

## Part 3: Validation Utilities (`common/utils.py`)

**✅ Add to `common/utils.py`:**

```python
"""
Centralized validation utilities
"""
import re
from typing import Optional


def validate_nric(nric: str) -> bool:
    """
    Validate Malaysian IC number format.

    Args:
        nric: IC number string

    Returns:
        bool: True if valid format, False otherwise

    Format: XXXXXX-XX-XXXX (6 digits, 2 digits, 4 digits)
    """
    if not nric:
        return False

    pattern = r'^\d{6}-\d{2}-\d{4}$'
    return bool(re.match(pattern, nric.strip()))


def validate_phone(phone: str) -> bool:
    """
    Validate Malaysian phone number.

    Args:
        phone: Phone number string

    Returns:
        bool: True if valid format, False otherwise

    Formats accepted:
    - 01X-XXXXXXX (with dash)
    - 01XXXXXXXXX (without dash)
    """
    if not phone:
        return False

    phone = phone.strip()

    # Pattern with dash: 01X-XXXXXXX
    pattern_with_dash = r'^01[0-9]-\d{7,8}$'
    # Pattern without dash: 01XXXXXXXXX
    pattern_without_dash = r'^01[0-9]\d{7,8}$'

    return bool(re.match(pattern_with_dash, phone)) or \
           bool(re.match(pattern_without_dash, phone))


def validate_image_file(file, max_size_mb: int = 10) -> bool:
    """
    Validate uploaded image file.

    Args:
        file: Django UploadedFile object
        max_size_mb: Maximum file size in megabytes

    Returns:
        bool: True if valid, False otherwise
    """
    if not file:
        return False

    # 1. Check file size
    max_size_bytes = max_size_mb * 1024 * 1024
    if file.size > max_size_bytes:
        return False

    # 2. Check file extension
    from pathlib import Path
    allowed_extensions = ['.jpg', '.jpeg', '.png']
    ext = Path(file.name).suffix.lower()
    if ext not in allowed_extensions:
        return False

    return True


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength.

    Args:
        password: Password string

    Returns:
        tuple: (is_valid, error_message)
    """
    if not password:
        return False, "Password is required."

    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter."

    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter."

    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit."

    # Check for special characters
    special_chars = "!@#$%^&*()_+-=[]{}|;:',.<>?/"
    if not any(c in special_chars for c in password):
        return False, "Password must contain at least one special character."

    return True, None
```

**Why:** Centralized validation functions ensure consistency across forms, serializers, and APIs.

---

## Part 4: Validation Checklist

### Before Deploying ANY Feature:

**Server-Side Validation:**
- ✅ All form fields have `clean_<field>()` methods
- ✅ All forms have `clean()` method for cross-field validation
- ✅ All model fields have appropriate validators
- ✅ All API serializers have `validate_<field>()` methods
- ✅ All API serializers have `validate()` method for object-level validation
- ✅ File uploads validate type, size, and MIME type
- ✅ Uniqueness constraints are checked in validation
- ✅ Business rules are enforced in validation

**Client-Side Validation:**
- ✅ All input fields have HTML5 validation attributes (required, pattern, min, max, type)
- ✅ Custom JavaScript validation for complex rules
- ✅ Real-time validation feedback (on input/blur events)
- ✅ File uploads validate type and size before submission
- ✅ Form submission is blocked if validation fails
- ✅ Clear error messages are displayed for each field
- ✅ Visual feedback (is-valid/is-invalid classes)

**Both Layers:**
- ✅ Error messages are consistent between client and server
- ✅ Validation rules are consistent between client and server
- ✅ Server-side validation is NEVER bypassed
- ✅ Client-side validation enhances UX but doesn't replace security

---

## Common Validation Patterns

### Pattern 1: Required Field with Min/Max Length

**Server-Side:**
```python
def clean_name(self):
    name = self.cleaned_data.get('name')
    if not name or not name.strip():
        raise forms.ValidationError("Name is required.")
    if len(name) < 2 or len(name) > 200:
        raise forms.ValidationError("Name must be between 2 and 200 characters.")
    return name.strip()
```

**Client-Side:**
```html
<input type="text" id="id_name" required minlength="2" maxlength="200">
```

---

### Pattern 2: Email with Uniqueness Check

**Server-Side:**
```python
def clean_email(self):
    email = self.cleaned_data.get('email')
    if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
        raise forms.ValidationError("Email already registered.")
    return email.lower()
```

**Client-Side:**
```html
<input type="email" id="id_email" required>
<script>
    // Async uniqueness check via API
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
</script>
```

---

### Pattern 3: Date Range Validation

**Server-Side:**
```python
def clean_date_of_birth(self):
    dob = self.cleaned_data.get('date_of_birth')
    from datetime import date
    if dob > date.today():
        raise forms.ValidationError("Date cannot be in future.")
    return dob
```

**Client-Side:**
```html
<input type="date" id="id_date_of_birth" required>
<script>
    dobInput.max = new Date().toISOString().split('T')[0];
</script>
```

---

### Pattern 4: File Upload Validation

**Server-Side:**
```python
def clean_original_image(self):
    image = self.cleaned_data.get('original_image')
    from common.utils import validate_image_file
    if not validate_image_file(image, max_size_mb=10):
        raise forms.ValidationError("Invalid image or size exceeds 10MB.")
    return image
```

**Client-Side:**
```javascript
fileInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file.size > 10 * 1024 * 1024) {
        setInvalid(this, 'File must be under 10MB.');
        this.value = '';
    }
});
```

---

## Anti-Patterns (NEVER DO THIS)

### ❌ Anti-Pattern 1: Client-Side Only Validation

```python
# ❌ WRONG - No server-side validation
class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'email']
    # ❌ Missing clean_* methods - SECURITY VULNERABILITY!
```

```html
<!-- Relying only on HTML5/JavaScript validation -->
<input type="email" required>  <!-- ❌ Can be bypassed! -->
```

**Why Wrong:** Client-side validation can be bypassed by disabling JavaScript or using curl/Postman.

---

### ❌ Anti-Pattern 2: No Client-Side Validation

```python
# ✅ Server-side validation is present
def clean_name(self):
    # ... validation logic ...
    pass
```

```html
<!-- ❌ No client-side validation - poor UX -->
<input type="text" id="id_name">  <!-- No required, no pattern -->
```

**Why Wrong:** Poor user experience - users only see errors after form submission.

---

### ❌ Anti-Pattern 3: Inconsistent Error Messages

**Server-Side:**
```python
raise forms.ValidationError("Invalid IC number format.")
```

**Client-Side:**
```javascript
setInvalid(input, "IC number is wrong.");  // ❌ Different message
```

**Why Wrong:** Confuses users - error messages should be consistent.

---

## Integration with Existing Skills

### With `security-best-practices`:
- Server-side validation is the **security boundary**
- This skill enforces validation implementation
- Security skill enforces WHAT to validate (injection, XSS, etc.)

### With `foundation-components`:
- Use `common.widgets` for consistent form rendering
- Use `common.utils` for centralized validation logic
- Use Bootstrap classes for validation feedback (is-valid/is-invalid)

### With `full-stack-django-patterns`:
- Follow form patterns for validation structure
- Use service layer for complex cross-model validation
- Use model validation as final defense layer

---

## Auto-Apply This Skill When:
- Creating any Django form
- Creating any DRF serializer
- Adding new model fields
- Implementing file upload functionality
- Creating API endpoints
- Writing templates with user input
- Implementing search or filter functionality
- Adding user registration or profile forms

---

**Last Updated:** 2025-11-24
**Version:** 1.0.0
**Status:** Active - MANDATORY for all user inputs
**Principle:** Server-side = Security, Client-side = UX, Both = Excellence
