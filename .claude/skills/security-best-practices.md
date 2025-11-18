# Security Best Practices Skill

Ensures all code follows industry-standard security practices for healthcare/medical applications.

## Core Security Principles

1. **Defense in Depth**: Multiple layers of security
2. **Least Privilege**: Minimum necessary permissions
3. **Secure by Default**: Security is default, not optional
4. **Input Validation**: Never trust user input
5. **Data Protection**: Encrypt sensitive data
6. **Audit Logging**: Track all important operations

## OWASP Top 10 Protection

### 1. Injection Prevention

**SQL Injection**
```python
# ✅ GOOD: Use Django ORM (parameterized queries)
Prediction.objects.filter(final_diagnosis=user_input)

# ❌ BAD: Raw SQL with string formatting
cursor.execute(f"SELECT * FROM prediction WHERE diagnosis = '{user_input}'")

# ✅ ACCEPTABLE: Parameterized raw SQL if ORM not suitable
cursor.execute("SELECT * FROM prediction WHERE diagnosis = %s", [user_input])
```

**Command Injection**
```python
# ❌ BAD: Shell injection vulnerability
import os
os.system(f"convert {user_filename} output.jpg")

# ✅ GOOD: Use subprocess with list arguments
import subprocess
subprocess.run(['convert', user_filename, 'output.jpg'], check=True)
```

### 2. Broken Authentication

**Password Handling**
```python
# ✅ Django handles this, but enforce strong passwords
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8}
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Session Security
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Strict'  # CSRF protection
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # For healthcare
```

**Login Rate Limiting**
```python
# views.py
from django.core.cache import cache
from django.http import HttpResponseForbidden

class RateLimitMixin:
    """Prevent brute force attacks"""

    def dispatch(self, request, *args, **kwargs):
        # Track failed login attempts
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

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
```

### 3. Sensitive Data Exposure

**HTTPS Enforcement**
```python
# settings.py (Production)
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

**Sensitive Field Handling**
```python
# models.py
from django.db import models

class Patient(models.Model):
    # ✅ Don't store SSN/IC directly without encryption
    # Use django-encrypted-model-fields or similar
    ic_number_encrypted = models.BinaryField()  # Encrypted

    # ✅ Hash medical record numbers if used for lookup
    medical_record_hash = models.CharField(max_length=64, unique=True)

    def set_ic_number(self, ic_number: str):
        """Encrypt IC number before storing"""
        from cryptography.fernet import Fernet
        cipher = Fernet(settings.ENCRYPTION_KEY)
        self.ic_number_encrypted = cipher.encrypt(ic_number.encode())

    def get_ic_number(self) -> str:
        """Decrypt IC number for authorized access"""
        from cryptography.fernet import Fernet
        cipher = Fernet(settings.ENCRYPTION_KEY)
        return cipher.decrypt(self.ic_number_encrypted).decode()
```

**Logging Sensitive Data**
```python
import logging

logger = logging.getLogger(__name__)

# ❌ BAD: Log sensitive data
logger.info(f"Patient {patient.ic_number} logged in")

# ✅ GOOD: Log only non-sensitive identifiers
logger.info(f"Patient {patient.id} logged in")
```

### 4. Access Control (Already implemented!)

**Role-Based Access**
```python
# ✅ Using our mixins
class DoctorDashboardView(DoctorRequiredMixin, View):
    """Only doctors can access"""
    pass

# ✅ Object-level permissions
def view_results(request, prediction_id):
    prediction = get_object_or_404(Prediction, id=prediction_id)

    # Doctor can see all
    if request.user.profile.is_doctor():
        return render(request, 'results.html', {'prediction': prediction})

    # Patient can only see own
    if request.user.profile.is_patient():
        if prediction.xray.patient.user != request.user:
            raise PermissionDenied("You can only view your own results")
        return render(request, 'results.html', {'prediction': prediction})

    raise PermissionDenied()
```

### 5. Security Misconfiguration

**Django Settings Security**
```python
# settings.py

# ❌ NEVER commit secrets to Git
# ✅ Use environment variables
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DATABASE_PASSWORD = config('DB_PASSWORD')

# Debug mode
DEBUG = config('DEBUG', default=False, cast=bool)

# Allowed hosts
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])

# Security headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# CSRF protection
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
```

### 6. Cross-Site Scripting (XSS)

**Template Auto-Escaping**
```django
<!-- ✅ GOOD: Django auto-escapes by default -->
<p>{{ user_input }}</p>

<!-- ❌ BAD: Disable auto-escape only if you're SURE it's safe HTML -->
<p>{{ user_input|safe }}</p>

<!-- ✅ GOOD: Explicit escaping -->
<p>{{ user_input|escape }}</p>

<!-- ✅ GOOD: For JavaScript context, use json_script -->
{{ data|json_script:"prediction-data" }}
<script>
    const data = JSON.parse(document.getElementById('prediction-data').textContent);
</script>
```

**Content Security Policy**
```python
# settings.py
# Use django-csp package
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net")
CSP_IMG_SRC = ("'self'", "data:", "https:")
```

### 7. File Upload Security

**Safe File Handling**
```python
# forms.py
import magic
from pathlib import Path

def clean_original_image(self):
    image = self.cleaned_data.get('original_image')

    # 1. Check file size
    if image.size > 10 * 1024 * 1024:  # 10MB
        raise ValidationError("File too large")

    # 2. Check extension
    allowed_extensions = ['.jpg', '.jpeg', '.png']
    ext = Path(image.name).suffix.lower()
    if ext not in allowed_extensions:
        raise ValidationError("Invalid file type")

    # 3. Verify MIME type (prevent extension spoofing)
    mime = magic.from_buffer(image.read(1024), mime=True)
    image.seek(0)  # Reset file pointer
    allowed_mimes = ['image/jpeg', 'image/png']
    if mime not in allowed_mimes:
        raise ValidationError("Invalid file format")

    # 4. Scan for malware if available
    # Use ClamAV or similar

    return image
```

**Safe File Storage**
```python
# models.py
import uuid
from pathlib import Path

def safe_upload_path(instance, filename):
    """Generate safe upload path"""
    # Use UUID to prevent path traversal
    ext = Path(filename).suffix.lower()
    new_filename = f"{uuid.uuid4()}{ext}"
    return f'xrays/original/{instance.patient.id}/{new_filename}'

class XRayImage(models.Model):
    original_image = models.ImageField(upload_to=safe_upload_path)
```

### 8. CSRF Protection

**All Forms Must Include**
```django
<!-- ✅ Always include CSRF token -->
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Submit</button>
</form>
```

**AJAX Requests**
```javascript
// ✅ Include CSRF token in AJAX
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

fetch('/api/endpoint/', {
    method: 'POST',
    headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(data)
});
```

## Healthcare-Specific Security

### HIPAA-Like Considerations (If Applicable)

**Audit Logging**
```python
# models.py
class AuditLog(models.Model):
    """Track all access to patient data"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict)

    class Meta:
        ordering = ['-timestamp']

# Middleware or signal to log access
from django.db.models.signals import post_save

@receiver(post_save, sender=Prediction)
def log_prediction_creation(sender, instance, created, **kwargs):
    if created:
        AuditLog.objects.create(
            user=instance.xray.uploaded_by,
            action='PREDICTION_CREATED',
            patient=instance.xray.patient,
            ip_address=get_current_ip(),
            details={'prediction_id': instance.id}
        )
```

**Data Retention**
```python
# management/commands/cleanup_old_data.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Delete predictions older than 7 years (example retention policy)'

    def handle(self, *args, **options):
        cutoff_date = timezone.now() - timedelta(days=365 * 7)
        old_predictions = Prediction.objects.filter(created_at__lt=cutoff_date)
        count = old_predictions.count()
        old_predictions.delete()
        self.stdout.write(f'Deleted {count} old predictions')
```

### Data Anonymization

```python
# services.py
class AnonymizationService:
    """Anonymize patient data for research"""

    @staticmethod
    def anonymize_patient(patient: Patient) -> dict:
        """Remove PII, keep medical data"""
        return {
            'age': patient.age,
            'gender': patient.gender,
            'medical_history': patient.medical_history,
            # DON'T include: name, IC, address, contact, etc.
        }

    @staticmethod
    def anonymize_prediction(prediction: Prediction) -> dict:
        """Anonymize prediction for research dataset"""
        return {
            'diagnosis': prediction.final_diagnosis,
            'confidence': prediction.consensus_confidence,
            'age': prediction.xray.patient.age,
            'gender': prediction.xray.patient.gender,
            # Image can be included (no PII in X-ray)
            'image_id': prediction.xray.id,
        }
```

## Security Checklist

Before deploying ANY feature:

- ✅ All user inputs are validated
- ✅ CSRF tokens on all forms
- ✅ SQL injection prevented (using ORM)
- ✅ XSS prevented (template auto-escaping)
- ✅ Authentication required for sensitive operations
- ✅ Authorization checks (role-based + object-level)
- ✅ Sensitive data encrypted
- ✅ HTTPS enforced (production)
- ✅ Security headers configured
- ✅ File uploads validated (type, size, content)
- ✅ Rate limiting on authentication
- ✅ Audit logging for important operations
- ✅ No secrets in code (use environment variables)
- ✅ Debug mode OFF in production
- ✅ Dependencies updated (no known vulnerabilities)

## Security Testing

```python
# tests/test_security.py
from django.test import TestCase, Client
from django.contrib.auth.models import User

class SecurityTests(TestCase):
    def test_unauthenticated_access_denied(self):
        """Ensure protected pages require login"""
        response = self.client.get('/detection/upload/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_patient_cannot_access_doctor_pages(self):
        """Ensure role-based access control"""
        patient = User.objects.create_user('patient', 'p@test.com', 'pass')
        patient.profile.role = 'patient'
        patient.profile.save()

        self.client.login(username='patient', password='pass')
        response = self.client.get('/detection/upload/')
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_csrf_protection(self):
        """Ensure CSRF protection on forms"""
        self.client.login(username='doctor', password='pass')
        # POST without CSRF token should fail
        response = self.client.post('/detection/upload/', {})
        self.assertEqual(response.status_code, 403)

    def test_sql_injection_prevented(self):
        """Ensure ORM prevents SQL injection"""
        # This should NOT execute as SQL
        malicious_input = "'; DROP TABLE predictions; --"
        results = Prediction.objects.filter(final_diagnosis=malicious_input)
        # Should return 0 results, not drop table
        self.assertEqual(results.count(), 0)
```

## Auto-Apply This Skill When:
- Creating new views or forms
- Handling user input
- Implementing authentication/authorization
- Working with sensitive data (patient info, X-rays)
- Adding file upload functionality
- Creating APIs
- Modifying database models
- Deploying to production
