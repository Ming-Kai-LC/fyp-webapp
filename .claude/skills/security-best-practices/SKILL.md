---
name: Security Best Practices
description: Enforces OWASP Top 10 security standards and healthcare-grade security for medical applications. Auto-applies input validation, authentication, and data protection patterns.
---

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

---

## Healthcare-Grade Security Requirements

### PHI (Protected Health Information) Handling

**What is PHI in this application:**
- Patient names, IC numbers, contact information
- Medical history and diagnoses
- X-ray images
- Prediction results
- Appointment records
- Any data that can identify a patient

**PHI Protection Rules:**

```python
# models.py - Always use FullAuditModel for PHI
from common.models import FullAuditModel

class Patient(FullAuditModel):  # ✅ Audit trail for all PHI access
    """
    Contains PHI - requires full audit logging
    Auto gets: created_at, updated_at, created_by, updated_by,
               is_deleted, deleted_at, deleted_by
    """
    name = models.CharField(max_length=200)
    ic_number = models.CharField(max_length=20)  # Consider encryption
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    date_of_birth = models.DateField()
    medical_history = models.TextField()

    class Meta:
        permissions = [
            ("view_all_patients", "Can view all patients"),
            ("export_patient_data", "Can export patient data"),
            ("anonymize_patient_data", "Can anonymize patient data"),
        ]
```

### Encryption at Rest (Production)

**For sensitive fields (IC numbers, medical record numbers):**

```python
# Install: pip install django-encrypted-model-fields
from encrypted_model_fields.fields import EncryptedCharField

class Patient(FullAuditModel):
    # Encrypted fields
    ic_number = EncryptedCharField(max_length=20)  # ✅ Encrypted in database

    # Non-sensitive fields (plain text OK)
    age = models.IntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

# settings.py
# Store encryption key in environment variable, NOT in code
FIELD_ENCRYPTION_KEY = config('FIELD_ENCRYPTION_KEY')  # 32-byte Fernet key
```

**Generating encryption key:**
```python
# Run once to generate key, store in .env
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())  # Add to .env as FIELD_ENCRYPTION_KEY
```

### Access Audit Logging (CRITICAL)

**Comprehensive audit trail for all PHI access:**

```python
# audit/models.py
from common.models import TimeStampedModel

class AccessLog(TimeStampedModel):
    """Log every access to patient data - HIPAA requirement"""

    ACTION_CHOICES = [
        ('VIEW', 'Viewed patient record'),
        ('CREATE', 'Created patient record'),
        ('UPDATE', 'Updated patient record'),
        ('DELETE', 'Deleted patient record'),
        ('EXPORT', 'Exported patient data'),
        ('PRINT', 'Printed patient data'),
        ('UPLOAD_XRAY', 'Uploaded X-ray'),
        ('VIEW_XRAY', 'Viewed X-ray'),
        ('CREATE_PREDICTION', 'Created prediction'),
        ('VIEW_PREDICTION', 'Viewed prediction'),
        ('VALIDATE_PREDICTION', 'Validated prediction'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    patient = models.ForeignKey('detection.Patient', on_delete=models.CASCADE, null=True)
    resource_type = models.CharField(max_length=50)  # 'Patient', 'XRay', 'Prediction'
    resource_id = models.IntegerField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    details = models.JSONField(default=dict)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
        ]

# audit/middleware.py
class AuditMiddleware:
    """Automatically log PHI access"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Log if accessing PHI views
        if self._is_phi_access(request):
            self._log_access(request, response)

        return response

    def _is_phi_access(self, request):
        """Check if URL accesses PHI"""
        phi_patterns = [
            '/detection/patient/',
            '/detection/xray/',
            '/detection/prediction/',
            '/api/patients/',
            '/api/predictions/',
        ]
        return any(pattern in request.path for pattern in phi_patterns)

    def _log_access(self, request, response):
        """Log the access"""
        if request.user.is_authenticated and response.status_code == 200:
            AccessLog.objects.create(
                user=request.user,
                action='VIEW',
                resource_type=self._get_resource_type(request.path),
                resource_id=self._extract_resource_id(request.path),
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                details={'path': request.path, 'method': request.method}
            )
```

### Data Retention & Destruction Policies

```python
# management/commands/apply_retention_policy.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from audit.models import AccessLog

class Command(BaseCommand):
    help = 'Apply data retention policies'

    def handle(self, *args, **options):
        # Retention periods (adjust based on regulations)
        policies = {
            'access_logs': timedelta(days=365 * 7),  # 7 years
            'predictions': timedelta(days=365 * 10),  # 10 years
            'xrays': timedelta(days=365 * 10),  # 10 years
            'patients_inactive': timedelta(days=365 * 5),  # 5 years since last visit
        }

        # Delete old access logs
        cutoff = timezone.now() - policies['access_logs']
        deleted_logs = AccessLog.objects.filter(created_at__lt=cutoff).delete()
        self.stdout.write(f'Deleted {deleted_logs[0]} old access logs')

        # Archive old predictions (soft delete)
        cutoff = timezone.now() - policies['predictions']
        old_predictions = Prediction.objects.filter(
            created_at__lt=cutoff,
            is_deleted=False
        )
        count = old_predictions.update(
            is_deleted=True,
            deleted_at=timezone.now(),
            deleted_by=None  # Automated deletion
        )
        self.stdout.write(f'Archived {count} old predictions')
```

### Secure Data Export & Anonymization

```python
# reporting/services.py
import hashlib
from typing import List, Dict, Any

class SecureExportService:
    """Handle secure export of patient data"""

    @staticmethod
    def export_for_research(prediction_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Export anonymized data for research.
        Removes all PII, keeps medical data.
        """
        predictions = Prediction.objects.filter(
            id__in=prediction_ids
        ).select_related('xray__patient')

        anonymized_data = []
        for pred in predictions:
            # Create anonymous patient ID (consistent hash)
            patient_hash = hashlib.sha256(
                f"patient_{pred.xray.patient.id}".encode()
            ).hexdigest()[:16]

            anonymized_data.append({
                'anonymous_patient_id': patient_hash,
                'age': pred.xray.patient.age,
                'gender': pred.xray.patient.gender,
                'diagnosis': pred.final_diagnosis,
                'confidence': pred.consensus_confidence,
                'model_results': {
                    'crossvit': pred.crossvit_confidence,
                    'resnet50': pred.resnet50_confidence,
                    'densenet121': pred.densenet121_confidence,
                },
                'created_at': pred.created_at.isoformat(),
                # NO: name, IC, contact, address, etc.
            })

        # Log export for audit
        AccessLog.objects.create(
            user=get_current_user(),
            action='EXPORT',
            resource_type='Prediction',
            resource_id=0,  # Bulk export
            ip_address=get_current_ip(),
            details={
                'count': len(anonymized_data),
                'anonymized': True,
            }
        )

        return anonymized_data

    @staticmethod
    def export_for_compliance(patient_id: int, requesting_user: User) -> Dict[str, Any]:
        """
        Export complete patient data for compliance/legal request.
        Requires admin permission and is fully audited.
        """
        # Verify permission
        if not requesting_user.has_perm('detection.export_patient_data'):
            raise PermissionDenied("Not authorized to export patient data")

        patient = Patient.objects.get(id=patient_id)

        # Full data export (includes PII)
        data = {
            'patient': {
                'id': patient.id,
                'name': patient.name,
                'ic_number': patient.get_ic_number() if hasattr(patient, 'get_ic_number') else patient.ic_number,
                'phone': patient.phone,
                'email': patient.email,
                'date_of_birth': patient.date_of_birth.isoformat(),
                'medical_history': patient.medical_history,
            },
            'xrays': [
                {
                    'id': xray.id,
                    'uploaded_at': xray.created_at.isoformat(),
                    'image_path': xray.original_image.url,
                }
                for xray in patient.xrays.all()
            ],
            'predictions': [
                {
                    'id': pred.id,
                    'diagnosis': pred.final_diagnosis,
                    'confidence': pred.consensus_confidence,
                    'created_at': pred.created_at.isoformat(),
                }
                for xray in patient.xrays.all()
                for pred in xray.predictions.all()
            ],
            'export_metadata': {
                'exported_by': requesting_user.username,
                'exported_at': timezone.now().isoformat(),
                'export_reason': 'Compliance request',
            }
        }

        # Log export (CRITICAL for compliance)
        AccessLog.objects.create(
            user=requesting_user,
            action='EXPORT',
            patient=patient,
            resource_type='Patient',
            resource_id=patient.id,
            ip_address=get_current_ip(),
            details={
                'full_export': True,
                'includes_phi': True,
            }
        )

        return data
```

### Secure Session Management (Healthcare)

```python
# settings.py - Healthcare-specific session settings

# Session expires after 15 minutes of inactivity
SESSION_COOKIE_AGE = 900  # 15 minutes

# Session expires when browser closes
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Prevent session fixation
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Strict'

# Regenerate session ID after login
def login_view(request):
    # ... authentication logic ...
    if user.is_authenticated:
        # Regenerate session ID to prevent session fixation
        request.session.cycle_key()
        login(request, user)

        # Log login for audit
        AccessLog.objects.create(
            user=user,
            action='LOGIN',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        )
```

### Incident Response Procedures

**Security incident handling:**

```python
# security/incident_response.py
from django.core.mail import send_mail
from django.conf import settings
import logging

security_logger = logging.getLogger('security')

class IncidentResponse:
    """Handle security incidents"""

    @staticmethod
    def report_suspicious_access(user: User, patient: Patient, reason: str):
        """Report suspicious access pattern"""

        # Log incident
        security_logger.warning(
            f"Suspicious access: User {user.username} accessed "
            f"Patient {patient.id} - Reason: {reason}"
        )

        # Create audit record
        AccessLog.objects.create(
            user=user,
            action='SUSPICIOUS_ACCESS',
            patient=patient,
            resource_type='Patient',
            resource_id=patient.id,
            ip_address=get_current_ip(),
            details={
                'reason': reason,
                'flagged': True,
                'requires_review': True,
            }
        )

        # Notify security admin
        if settings.SECURITY_ADMIN_EMAIL:
            send_mail(
                subject=f'[SECURITY ALERT] Suspicious Access Detected',
                message=f'User {user.username} accessed Patient {patient.id}\nReason: {reason}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.SECURITY_ADMIN_EMAIL],
                fail_silently=False,
            )

    @staticmethod
    def report_data_breach(affected_patients: List[Patient], description: str):
        """Report potential data breach"""

        # Critical security log
        security_logger.critical(
            f"POTENTIAL DATA BREACH: {len(affected_patients)} patients affected - {description}"
        )

        # Create incident record
        Incident.objects.create(
            incident_type='DATA_BREACH',
            severity='CRITICAL',
            description=description,
            affected_patient_count=len(affected_patients),
            reported_at=timezone.now(),
            status='UNDER_INVESTIGATION',
        )

        # Immediate notification to admins
        if settings.SECURITY_ADMIN_EMAIL:
            send_mail(
                subject=f'[CRITICAL] Potential Data Breach Detected',
                message=f'Affected patients: {len(affected_patients)}\n{description}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.SECURITY_ADMIN_EMAIL],
                fail_silently=False,
            )

# Example usage in views
def patient_detail(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    # Check if user should have access
    if request.user.profile.is_patient():
        if patient.user != request.user:
            # Patient trying to access another patient's record
            IncidentResponse.report_suspicious_access(
                user=request.user,
                patient=patient,
                reason="Patient attempted to access another patient's record"
            )
            raise PermissionDenied("Access denied")

    # Normal access - still log it
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

### Security Testing for Healthcare Apps

```python
# tests/test_healthcare_security.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from detection.models import Patient, XRayImage, Prediction
from audit.models import AccessLog

class HealthcareSecurityTests(TestCase):
    """Comprehensive security tests for healthcare data"""

    def setUp(self):
        # Create test users
        self.admin = User.objects.create_user('admin', password='admin123')
        self.admin.profile.role = 'admin'
        self.admin.profile.save()

        self.staff = User.objects.create_user('staff', password='staff123')
        self.staff.profile.role = 'staff'
        self.staff.profile.save()

        self.patient1 = User.objects.create_user('patient1', password='pass123')
        self.patient1.profile.role = 'patient'
        self.patient1.profile.save()

        self.patient2 = User.objects.create_user('patient2', password='pass123')
        self.patient2.profile.role = 'patient'
        self.patient2.profile.save()

        # Create test patient records
        self.patient_record1 = Patient.objects.create(
            user=self.patient1,
            name="Test Patient 1",
            age=30,
            gender='M'
        )

        self.patient_record2 = Patient.objects.create(
            user=self.patient2,
            name="Test Patient 2",
            age=25,
            gender='F'
        )

    def test_patient_cannot_view_other_patient_data(self):
        """CRITICAL: Patient isolation"""
        self.client.login(username='patient1', password='pass123')

        # Try to access another patient's data
        response = self.client.get(f'/detection/patient/{self.patient_record2.id}/')

        self.assertEqual(response.status_code, 403)  # Forbidden

        # Verify suspicious access was logged
        suspicious_logs = AccessLog.objects.filter(
            action='SUSPICIOUS_ACCESS',
            user=self.patient1
        )
        self.assertTrue(suspicious_logs.exists())

    def test_staff_access_is_logged(self):
        """CRITICAL: All staff access must be audited"""
        self.client.login(username='staff', password='staff123')

        # Access patient data
        response = self.client.get(f'/detection/patient/{self.patient_record1.id}/')

        # Verify access was logged
        access_logs = AccessLog.objects.filter(
            user=self.staff,
            patient=self.patient_record1,
            action='VIEW'
        )
        self.assertTrue(access_logs.exists())
        self.assertGreater(access_logs.count(), 0)

    def test_phi_encryption_at_rest(self):
        """Test sensitive data encryption"""
        # If using encrypted fields
        if hasattr(self.patient_record1, 'ic_number'):
            # IC should be encrypted in database
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT ic_number FROM detection_patient WHERE id = %s",
                    [self.patient_record1.id]
                )
                raw_data = cursor.fetchone()[0]

                # Should NOT be plain text
                self.assertNotEqual(raw_data, self.patient_record1.ic_number)

    def test_data_export_requires_permission(self):
        """Test data export is restricted"""
        self.client.login(username='staff', password='staff123')

        # Try to export patient data without permission
        response = self.client.post('/api/export-patient/', {
            'patient_id': self.patient_record1.id
        })

        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_session_expires_after_inactivity(self):
        """Test session timeout for security"""
        self.client.login(username='staff', password='staff123')

        # Simulate session expiry
        from django.conf import settings
        session = self.client.session
        session.set_expiry(-1)  # Expired
        session.save()

        # Try to access protected resource
        response = self.client.get('/detection/dashboard/')

        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_anonymized_export_removes_phi(self):
        """Test anonymization removes all PII"""
        from reporting.services import SecureExportService

        # Create prediction
        xray = XRayImage.objects.create(patient=self.patient_record1)
        prediction = Prediction.objects.create(xray=xray, final_diagnosis='COVID')

        # Export anonymized data
        anonymized = SecureExportService.export_for_research([prediction.id])

        # Verify NO PII present
        self.assertEqual(len(anonymized), 1)
        data = anonymized[0]

        self.assertNotIn('name', data)
        self.assertNotIn('ic_number', data)
        self.assertNotIn('phone', data)
        self.assertNotIn('email', data)
        self.assertIn('age', data)  # OK - not identifiable
        self.assertIn('gender', data)  # OK - not identifiable
        self.assertIn('diagnosis', data)  # OK - medical data
```

### Healthcare Security Checklist

**Before deploying to production:**

**PHI Protection:**
- ✅ All PHI models use `FullAuditModel` (audit trail)
- ✅ Sensitive fields encrypted at rest (IC numbers, medical record numbers)
- ✅ All PHI access is logged in `AccessLog`
- ✅ Patient isolation enforced (patients cannot see other patients)
- ✅ Object-level permissions implemented

**Audit & Compliance:**
- ✅ Comprehensive access logging for all PHI access
- ✅ Audit logs retained for minimum 7 years
- ✅ User actions logged (VIEW, CREATE, UPDATE, DELETE, EXPORT)
- ✅ IP address and user agent logged
- ✅ Failed access attempts logged

**Data Security:**
- ✅ HTTPS enforced in production
- ✅ Session timeout configured (15 minutes)
- ✅ Session expires on browser close
- ✅ Encryption keys stored in environment variables (not code)
- ✅ Database backups encrypted
- ✅ File uploads scanned for malware

**Access Control:**
- ✅ Role-based access control enforced
- ✅ Admin-only functions restricted
- ✅ Staff can only perform job-related tasks
- ✅ Patients can only access own data
- ✅ Suspicious access patterns detected and logged

**Data Retention & Destruction:**
- ✅ Retention policies documented
- ✅ Automated retention policy enforcement
- ✅ Secure deletion (soft delete with audit)
- ✅ Data anonymization for research exports

**Incident Response:**
- ✅ Security incident logging implemented
- ✅ Automated alerts for suspicious activity
- ✅ Security admin notification configured
- ✅ Breach notification procedures documented

**Testing:**
- ✅ Security tests for patient isolation
- ✅ Security tests for access logging
- ✅ Security tests for data export restrictions
- ✅ Security tests for anonymization
- ✅ Penetration testing completed

---

## Security Monitoring & Alerts

**Real-time security monitoring:**

```python
# security/monitoring.py
from django.core.cache import cache
from django.conf import settings
from datetime import timedelta

class SecurityMonitor:
    """Monitor for suspicious security patterns"""

    @staticmethod
    def check_unusual_access_pattern(user: User, patient: Patient) -> bool:
        """Detect unusual access patterns"""

        # Check if user is accessing many different patients rapidly
        cache_key = f'patient_access_{user.id}'
        accessed_patients = cache.get(cache_key, set())
        accessed_patients.add(patient.id)
        cache.set(cache_key, accessed_patients, 300)  # 5 minutes

        # Alert if accessing > 10 different patients in 5 minutes
        if len(accessed_patients) > 10:
            IncidentResponse.report_suspicious_access(
                user=user,
                patient=patient,
                reason=f"User accessed {len(accessed_patients)} different patients in 5 minutes"
            )
            return True

        return False

    @staticmethod
    def check_off_hours_access(user: User) -> bool:
        """Detect access outside business hours"""
        from datetime import datetime

        current_hour = datetime.now().hour

        # Business hours: 8 AM - 6 PM
        if current_hour < 8 or current_hour > 18:
            security_logger.warning(
                f"Off-hours access: User {user.username} at {datetime.now()}"
            )
            return True

        return False
```

---

## Auto-Apply This Skill When:
- Creating new views or forms
- Handling user input
- Implementing authentication/authorization
- Working with sensitive data (patient info, X-rays)
- Adding file upload functionality
- Creating APIs
- Modifying database models
- Deploying to production
- Implementing data export features
- Creating audit logs
- Handling PHI (Protected Health Information)
- Implementing session management

---

**Last Updated:** 2025-11-24
**Version:** 2.0.0 (Enhanced with Healthcare-Grade Security)
**Status:** Active
**Compliance:** OWASP Top 10 + Healthcare-Grade (HIPAA-like) Security
