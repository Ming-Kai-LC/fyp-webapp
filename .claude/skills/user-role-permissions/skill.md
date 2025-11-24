---
name: user-role-permissions
description: Enforces role-based access control (RBAC) with three user roles - admin (full privileges), staff (read/update, create medical records, limited delete), patient (self-registration and profile updates only). Auto-applies when implementing authentication, authorization, or user management features.
---

# User Role Permissions and Access Control

## Core Principles

This skill defines the **fundamental access control rules** for the COVID-19 Detection Web Application. Every feature, view, API endpoint, and database operation MUST respect these role-based permissions.

### Three User Roles

1. **Admin** - Full system privileges
2. **Staff** - Medical staff with limited administrative rights
3. **Patient** - End users with self-service capabilities

### Primary Rules

1. **Only admin can create staff users** - Staff accounts are created through admin panel only
2. **Public can only register as patients** - Public registration is restricted to patient role
3. **Admin has full privileges** - Complete CRUD access to all resources
4. **Staff have read/update rights** - Can view all records, update medical data, create medical records, limited delete
5. **Patients have self-service only** - Can register, view, and update their own profile and medical records only

---

## Role Definitions and Permissions

### Admin Role

**Database value:** `role = "admin"`

**Capabilities:**
- ✅ Create/Read/Update/Delete ALL users (including staff)
- ✅ Access Django admin panel
- ✅ Create/Read/Update/Delete ALL medical records
- ✅ Create/Read/Update/Delete ALL X-rays and predictions
- ✅ Create/Read/Update/Delete ALL appointments
- ✅ Access audit logs and compliance reports
- ✅ Manage system settings and configurations
- ✅ Export all data and reports
- ✅ Perform bulk operations
- ✅ Access analytics and system insights

**Helper method:** `request.user.profile.is_admin()`

**Auto-created:** First superuser automatically gets admin role via signal

---

### Staff Role

**Database value:** `role = "staff"`

**Capabilities:**

**CREATE:**
- ✅ X-ray uploads and COVID predictions
- ✅ Medical reports and clinical notes
- ✅ Appointments for patients
- ✅ Validation notes for predictions
- ❌ User accounts (staff or patient)
- ❌ Audit log entries (auto-created only)

**READ:**
- ✅ All patient records
- ✅ All X-rays and predictions
- ✅ All appointments
- ✅ All medical reports
- ✅ Analytics dashboards
- ❌ Audit logs (admin only)
- ❌ System settings (admin only)

**UPDATE:**
- ✅ Patient medical information
- ✅ Prediction validation status
- ✅ Appointment details
- ✅ Medical reports and notes
- ✅ Own profile information
- ❌ User roles (admin only)
- ❌ System configurations (admin only)

**DELETE:**
- ✅ Own clinical notes (if not validated)
- ✅ Pending/draft reports
- ✅ Uploaded X-rays (if no prediction yet)
- ❌ Validated predictions
- ❌ Patient accounts
- ❌ Historical medical records
- ❌ Audit logs

**Helper method:** `request.user.profile.is_staff()`

**Created by:** Admin only (via Django admin panel or admin-only views)

---

### Patient Role

**Database value:** `role = "patient"`

**Capabilities:**

**CREATE:**
- ✅ Own account via public registration
- ✅ Own medical history updates
- ✅ Appointment requests
- ❌ X-ray uploads (staff only)
- ❌ Medical reports (staff only)
- ❌ Other user accounts

**READ:**
- ✅ Own profile information
- ✅ Own medical records
- ✅ Own X-rays and predictions
- ✅ Own appointments
- ✅ Own medical reports
- ❌ Other patients' data
- ❌ System-wide analytics
- ❌ Audit logs

**UPDATE:**
- ✅ Own profile information
- ✅ Own contact details
- ✅ Own medical history
- ✅ Own emergency contact
- ❌ Own prediction results (read-only)
- ❌ Own appointments (request only)
- ❌ Other patients' data

**DELETE:**
- ❌ Own account (admin only)
- ❌ Own medical records (admin only)
- ❌ Own X-rays (admin only)
- ❌ Any system data

**Helper method:** `request.user.profile.is_patient()`

**Created by:** Self-registration or admin

**Default role:** All new registrations default to patient role

---

## Implementation Patterns

### 1. Model-Level Access Control

**UserProfile Model** (`detection/models.py`)

```python
class UserProfile(models.Model):
    """Extended user information with role-based access control"""

    ROLE_CHOICES = [
        ("admin", "Administrator"),
        ("staff", "Staff"),
        ("patient", "Patient"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="patient")

    def is_admin(self) -> bool:
        """Check if user has admin role"""
        return self.role == "admin"

    def is_staff(self) -> bool:
        """Check if user has staff role"""
        return self.role == "staff"

    def is_patient(self) -> bool:
        """Check if user has patient role"""
        return self.role == "patient"

    def can_create_users(self) -> bool:
        """Only admin can create users"""
        return self.is_admin()

    def can_delete_record(self, obj) -> bool:
        """Check if user can delete a specific object"""
        if self.is_admin():
            return True
        if self.is_staff():
            # Staff can delete own notes or pending items
            if hasattr(obj, 'created_by') and obj.created_by == self.user:
                if hasattr(obj, 'status') and obj.status == 'pending':
                    return True
            return False
        return False
```

**Auto-create profile for new users:**

```python
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create UserProfile when a new User is created"""
    if created:
        # Default role is patient
        UserProfile.objects.create(user=instance, role="patient")

        # If superuser, promote to admin
        if instance.is_superuser:
            instance.profile.role = "admin"
            instance.profile.save()
```

---

### 2. Function-Based View Decorators

**Basic Login Requirement:**

```python
from django.contrib.auth.decorators import login_required

@login_required
def my_view(request):
    """Requires authentication, any role"""
    pass
```

**Role-Specific Decorators:**

```python
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    """Decorator to require admin role"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.profile.is_admin():
            messages.error(request, "Access denied. Admin privileges required.")
            return redirect("home")
        return view_func(request, *args, **kwargs)
    return wrapper

def staff_required(view_func):
    """Decorator to require staff role"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.profile.is_staff():
            messages.error(request, "Access denied. Staff privileges required.")
            return redirect("home")
        return view_func(request, *args, **kwargs)
    return wrapper

def staff_or_admin_required(view_func):
    """Decorator to require staff or admin role"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not (request.user.profile.is_staff() or request.user.profile.is_admin()):
            messages.error(request, "Access denied. Staff or Admin privileges required.")
            return redirect("home")
        return view_func(request, *args, **kwargs)
    return wrapper
```

**Usage in views:**

```python
@staff_required
def upload_xray(request):
    """Staff can upload X-rays"""
    # Implementation
    pass

@admin_required
def create_staff_user(request):
    """Only admin can create staff users"""
    # Implementation
    pass

@login_required
def view_own_results(request):
    """Patients can view their own results"""
    if request.user.profile.is_patient():
        # Show only user's results
        predictions = Prediction.objects.filter(patient__user=request.user)
    else:
        # Staff/admin see all
        predictions = Prediction.objects.all()
    return render(request, "results.html", {"predictions": predictions})
```

---

### 3. Class-Based View Mixins

**Role Requirement Mixins:**

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

class AdminRequiredMixin(LoginRequiredMixin):
    """Mixin to require admin role for CBVs"""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.profile.is_admin():
            raise PermissionDenied("Admin privileges required")
        return super().dispatch(request, *args, **kwargs)

class StaffRequiredMixin(LoginRequiredMixin):
    """Mixin to require staff role for CBVs"""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.profile.is_staff():
            raise PermissionDenied("Staff privileges required")
        return super().dispatch(request, *args, **kwargs)

class StaffOrAdminRequiredMixin(LoginRequiredMixin):
    """Mixin to require staff or admin role for CBVs"""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not (request.user.profile.is_staff() or request.user.profile.is_admin()):
            raise PermissionDenied("Staff or Admin privileges required")
        return super().dispatch(request, *args, **kwargs)
```

**Object-Level Permission Mixin:**

```python
class ObjectOwnerMixin:
    """Mixin to restrict access to object owner or staff/admin"""

    def get_queryset(self):
        """Filter queryset based on role"""
        qs = super().get_queryset()
        user = self.request.user

        if user.profile.is_patient():
            # Patients see only their own objects
            return qs.filter(patient__user=user)
        # Staff and admin see all
        return qs

    def get_object(self, queryset=None):
        """Ensure user has access to specific object"""
        obj = super().get_object(queryset)
        user = self.request.user

        if user.profile.is_patient():
            # Verify patient owns this object
            if hasattr(obj, 'patient') and obj.patient.user != user:
                raise PermissionDenied("You can only access your own records")
            elif hasattr(obj, 'user') and obj.user != user:
                raise PermissionDenied("You can only access your own records")

        return obj
```

**Usage in CBVs:**

```python
from django.views.generic import ListView, DetailView, CreateView

class XRayUploadView(StaffRequiredMixin, CreateView):
    """Staff can upload X-rays"""
    model = XRayImage
    template_name = "detection/upload.html"
    # ...

class PatientListView(StaffOrAdminRequiredMixin, ListView):
    """Staff and admin can view all patients"""
    model = Patient
    template_name = "detection/patients.html"
    # ...

class PredictionDetailView(LoginRequiredMixin, ObjectOwnerMixin, DetailView):
    """View prediction - patients see own, staff see all"""
    model = Prediction
    template_name = "detection/prediction_detail.html"
    # ...
```

---

### 4. REST API Permissions

**Custom Permission Classes** (`api/permissions.py`)

```python
from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """Allow access only to admin users"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.profile.is_admin()

class IsStaffOrAdmin(permissions.BasePermission):
    """Allow access to staff or admin users"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.profile.is_staff() or request.user.profile.is_admin()
        )

class IsPatientOwner(permissions.BasePermission):
    """
    Object-level permission - patients can only access own data
    Staff and admin can access all data
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Admin and staff have full access
        if user.profile.is_admin() or user.profile.is_staff():
            return True

        # Patient can only access own records
        if user.profile.is_patient():
            if hasattr(obj, 'patient'):
                return obj.patient.user == user
            elif hasattr(obj, 'user'):
                return obj.user == user

        return False

class ReadOnlyOrStaff(permissions.BasePermission):
    """
    Read access: all authenticated users
    Write access: staff or admin only
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.profile.is_staff() or request.user.profile.is_admin()

class StaffCreateOnly(permissions.BasePermission):
    """
    Allow create operations only for staff/admin
    Patients can read their own data
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method == 'POST':
            # Only staff/admin can create
            return request.user.profile.is_staff() or request.user.profile.is_admin()

        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Staff and admin have full access
        if user.profile.is_staff() or user.profile.is_admin():
            return True

        # Patients can read their own data
        if request.method in permissions.SAFE_METHODS:
            if hasattr(obj, 'patient'):
                return obj.patient.user == user
            elif hasattr(obj, 'user'):
                return obj.user == user

        return False
```

**Usage in ViewSets:**

```python
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

class PredictionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for COVID predictions
    - Staff/Admin: Full CRUD
    - Patient: Read own predictions only
    """
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer
    permission_classes = [StaffCreateOnly, IsPatientOwner]

    def get_queryset(self):
        """Filter based on user role"""
        user = self.request.user
        if user.profile.is_patient():
            return Prediction.objects.filter(patient__user=user)
        return Prediction.objects.all()

    @action(detail=True, methods=['post'], permission_classes=[IsStaffOrAdmin])
    def validate_prediction(self, request, pk=None):
        """Staff can validate predictions"""
        prediction = self.get_object()
        # Validation logic
        return Response({'status': 'validated'})

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user management
    - Admin: Full CRUD
    - Staff: Read only
    - Patient: Own profile only
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """Different permissions for different actions"""
        if self.action == 'create':
            # Only admin can create users (especially staff)
            permission_classes = [IsAdminUser]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Filter based on user role"""
        user = self.request.user
        if user.profile.is_admin():
            return User.objects.all()
        elif user.profile.is_staff():
            return User.objects.all()  # Read-only via permissions
        else:
            return User.objects.filter(id=user.id)  # Own profile only
```

---

### 5. Registration Flow

**Patient Self-Registration** (`detection/views.py`)

```python
from django.contrib.auth import login
from django.contrib.auth.models import User

def register(request):
    """Public registration - creates patient accounts only"""
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Create user
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Profile is auto-created via signal with role='patient'
            # Explicitly ensure it's patient (defense in depth)
            user.profile.role = "patient"
            user.profile.save()

            # Log user in
            login(request, user)
            messages.success(request, "Registration successful! Welcome to COVID-19 Detection.")
            return redirect("patient_dashboard")
    else:
        form = UserRegistrationForm()

    return render(request, "registration/register.html", {"form": form})
```

**Admin Creating Staff** (`detection/admin.py` or admin views)

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

    def get_fields(self, request, obj=None):
        """Show role field only to admins"""
        if request.user.profile.is_admin():
            return ['role', 'phone']
        return ['phone']

class CustomUserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]

    def save_formset(self, request, form, formset, change):
        """Ensure only admin can set staff role"""
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, UserProfile):
                if instance.role in ['staff', 'admin'] and not request.user.profile.is_admin():
                    raise PermissionDenied("Only admin can create staff or admin users")
            instance.save()
        formset.save_m2m()

# Register custom admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
```

**Alternative: Admin-Only Staff Creation View**

```python
@admin_required
def create_staff_user(request):
    """Admin-only view to create staff users"""
    if request.method == "POST":
        form = StaffCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Set role to staff
            user.profile.role = "staff"
            user.profile.save()

            messages.success(request, f"Staff user '{user.username}' created successfully.")
            return redirect("admin_dashboard")
    else:
        form = StaffCreationForm()

    return render(request, "admin/create_staff.html", {"form": form})
```

---

### 6. Inline Permission Checks

**In views where decorators aren't sufficient:**

```python
@login_required
def delete_record(request, record_id):
    """Delete a record - admin always, staff for pending/own items only"""
    record = get_object_or_404(MedicalRecord, id=record_id)
    user = request.user

    # Check if user can delete this record
    if not user.profile.can_delete_record(record):
        messages.error(request, "You don't have permission to delete this record.")
        return redirect("record_list")

    # Proceed with deletion
    record.delete()
    messages.success(request, "Record deleted successfully.")
    return redirect("record_list")

@login_required
def dashboard_redirect(request):
    """Redirect to appropriate dashboard based on role"""
    user = request.user

    if user.profile.is_admin():
        return redirect("admin_dashboard")
    elif user.profile.is_staff():
        return redirect("staff_dashboard")
    else:
        return redirect("patient_dashboard")
```

---

### 7. Template-Level Access Control

**In templates, check user role:**

```django
{% if user.profile.is_admin %}
    <a href="{% url 'create_staff' %}" class="btn btn-primary">Create Staff User</a>
    <a href="{% url 'audit_logs' %}" class="btn btn-secondary">View Audit Logs</a>
{% endif %}

{% if user.profile.is_staff or user.profile.is_admin %}
    <a href="{% url 'upload_xray' %}" class="btn btn-success">Upload X-Ray</a>
    <a href="{% url 'patient_list' %}" class="btn btn-info">View All Patients</a>
{% endif %}

{% if user.profile.is_patient %}
    <a href="{% url 'my_results' %}" class="btn btn-primary">My Results</a>
    <a href="{% url 'update_profile' %}" class="btn btn-secondary">Update Profile</a>
{% endif %}
```

**Show different content based on role:**

```django
<h1>
    {% if user.profile.is_admin %}
        Admin Dashboard
    {% elif user.profile.is_staff %}
        Staff Dashboard
    {% else %}
        My Health Portal
    {% endif %}
</h1>

<div class="predictions-list">
    {% for prediction in predictions %}
        <div class="prediction-card">
            <h3>{{ prediction.created_at }}</h3>
            <p>Result: {{ prediction.result }}</p>

            {% if user.profile.is_staff or user.profile.is_admin %}
                <a href="{% url 'validate_prediction' prediction.id %}">Validate</a>
                {% if not prediction.validated %}
                    <a href="{% url 'delete_prediction' prediction.id %}">Delete</a>
                {% endif %}
            {% endif %}
        </div>
    {% endfor %}
</div>
```

---

### 8. Healthcare-Specific Permission Scenarios

Healthcare applications require sophisticated permission models beyond basic RBAC to comply with regulations like HIPAA and handle real-world clinical workflows. This section covers critical permission scenarios for medical applications.

---

#### 8.1 Emergency Access (Break-the-Glass)

**Scenario:** A staff member needs to access a patient's records in an emergency when they don't have explicit permission (e.g., patient is unconscious, regular doctor unavailable).

**Implementation Pattern:**

```python
# detection/models.py
from django.db import models
from common.models import TimeStampedModel

class EmergencyAccess(TimeStampedModel):
    """Track break-the-glass emergency access events"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emergency_accesses')
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    reason = models.TextField(help_text="Emergency justification (required)")
    accessed_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_emergency_accesses'
    )

    class Meta:
        verbose_name = "Emergency Access"
        verbose_name_plural = "Emergency Accesses"
        indexes = [
            models.Index(fields=['patient', 'accessed_at']),
            models.Index(fields=['reviewed', 'accessed_at']),
        ]

# detection/services/emergency_service.py
from typing import Optional
from django.contrib.auth.models import User
from detection.models import Patient, EmergencyAccess
from audit.services import AuditService

class EmergencyAccessService:
    """Service for handling emergency break-the-glass access"""

    @staticmethod
    def request_emergency_access(
        user: User,
        patient: Patient,
        reason: str
    ) -> EmergencyAccess:
        """
        Grant temporary emergency access to patient records

        Args:
            user: Staff requesting emergency access
            patient: Patient whose records need to be accessed
            reason: Justification for emergency access (required)

        Returns:
            EmergencyAccess record for audit trail
        """
        if not user.profile.is_staff() and not user.profile.is_admin():
            raise PermissionDenied("Only staff can request emergency access")

        if not reason or len(reason) < 20:
            raise ValidationError("Detailed reason required (minimum 20 characters)")

        # Create emergency access record
        access = EmergencyAccess.objects.create(
            user=user,
            patient=patient,
            reason=reason
        )

        # Log to audit system
        AuditService.log_emergency_access(
            user=user,
            patient=patient,
            reason=reason,
            access_id=access.id
        )

        return access

    @staticmethod
    def can_access_patient(user: User, patient: Patient) -> bool:
        """
        Check if user has emergency access to patient
        Returns True if active emergency access exists
        """
        # Admin and assigned staff always have access
        if user.profile.is_admin():
            return True

        if hasattr(patient, 'assigned_staff') and patient.assigned_staff == user:
            return True

        # Check for active emergency access (within last 24 hours)
        from django.utils import timezone
        from datetime import timedelta

        cutoff = timezone.now() - timedelta(hours=24)
        has_emergency_access = EmergencyAccess.objects.filter(
            user=user,
            patient=patient,
            accessed_at__gte=cutoff
        ).exists()

        return has_emergency_access
```

**View Implementation:**

```python
# detection/views.py
from django.contrib import messages
from django.shortcuts import redirect, render
from detection.services.emergency_service import EmergencyAccessService

@staff_required
def request_emergency_access(request, patient_id):
    """Staff can request emergency access to patient records"""
    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == "POST":
        reason = request.POST.get('reason', '').strip()

        try:
            access = EmergencyAccessService.request_emergency_access(
                user=request.user,
                patient=patient,
                reason=reason
            )
            messages.warning(
                request,
                f"Emergency access granted. Access ID: {access.id}. "
                f"This action has been logged and will be reviewed."
            )
            return redirect("patient_detail", patient_id=patient.id)

        except (PermissionDenied, ValidationError) as e:
            messages.error(request, str(e))

    return render(request, "detection/emergency_access.html", {
        "patient": patient
    })

@login_required
def patient_detail(request, patient_id):
    """View patient details with emergency access check"""
    patient = get_object_or_404(Patient, id=patient_id)
    user = request.user

    # Check regular permissions first
    has_access = False
    emergency_access = False

    if user.profile.is_admin():
        has_access = True
    elif user.profile.is_staff():
        # Check if assigned staff or has emergency access
        if hasattr(patient, 'assigned_staff') and patient.assigned_staff == user:
            has_access = True
        elif EmergencyAccessService.can_access_patient(user, patient):
            has_access = True
            emergency_access = True
    elif user.profile.is_patient() and patient.user == user:
        has_access = True

    if not has_access:
        messages.error(request, "You don't have permission to view this patient's records.")
        return redirect("home")

    context = {
        "patient": patient,
        "emergency_access": emergency_access,  # Show warning banner
    }
    return render(request, "detection/patient_detail.html", context)
```

**Template with Emergency Warning:**

```django
{# detection/templates/detection/patient_detail.html #}
{% if emergency_access %}
<div class="alert alert-warning alert-dismissible fade show" role="alert">
    <i class="bi bi-exclamation-triangle-fill"></i>
    <strong>Emergency Access Active:</strong> You are viewing this patient's records via break-the-glass emergency access.
    This action has been logged and will be reviewed by administrators.
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>
{% endif %}
```

---

#### 8.2 Temporary Access Delegation

**Scenario:** A doctor delegates their patients to another doctor temporarily (e.g., vacation, medical leave).

**Implementation:**

```python
# detection/models.py
class TemporaryDelegation(TimeStampedModel):
    """Temporary access delegation between staff members"""

    delegator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='delegations_given'
    )
    delegate = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='delegations_received'
    )
    patient = models.ForeignKey(
        'Patient',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Specific patient or None for all patients"
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    reason = models.TextField()
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Temporary Delegation"
        indexes = [
            models.Index(fields=['delegate', 'active', 'end_date']),
            models.Index(fields=['patient', 'active']),
        ]

    def is_currently_active(self) -> bool:
        """Check if delegation is currently in effect"""
        from django.utils import timezone
        now = timezone.now()
        return (
            self.active and
            self.start_date <= now <= self.end_date
        )

# detection/services/delegation_service.py
class DelegationService:
    """Service for managing temporary access delegations"""

    @staticmethod
    def create_delegation(
        delegator: User,
        delegate: User,
        start_date: datetime,
        end_date: datetime,
        reason: str,
        patient: Optional[Patient] = None
    ) -> TemporaryDelegation:
        """Create temporary delegation"""

        # Validation
        if not delegator.profile.is_staff():
            raise PermissionDenied("Only staff can delegate access")

        if not delegate.profile.is_staff():
            raise ValidationError("Can only delegate to staff members")

        if end_date <= start_date:
            raise ValidationError("End date must be after start date")

        if (end_date - start_date).days > 90:
            raise ValidationError("Delegation cannot exceed 90 days")

        delegation = TemporaryDelegation.objects.create(
            delegator=delegator,
            delegate=delegate,
            patient=patient,
            start_date=start_date,
            end_date=end_date,
            reason=reason
        )

        # Audit log
        AuditService.log_delegation(delegation)

        return delegation

    @staticmethod
    def has_delegated_access(user: User, patient: Patient) -> bool:
        """Check if user has delegated access to patient"""
        from django.utils import timezone
        now = timezone.now()

        return TemporaryDelegation.objects.filter(
            delegate=user,
            active=True,
            start_date__lte=now,
            end_date__gte=now
        ).filter(
            models.Q(patient=patient) | models.Q(patient__isnull=True)
        ).exists()
```

---

#### 8.3 Time-Based Permissions

**Scenario:** Temporary consultants or locum doctors need access that automatically expires.

**Implementation:**

```python
# detection/models.py
class TimeBoundAccess(TimeStampedModel):
    """Time-limited access for temporary staff"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='time_bound_access')
    access_start = models.DateTimeField()
    access_end = models.DateTimeField()
    access_scope = models.JSONField(
        default=dict,
        help_text="Scoped permissions: {'can_view': True, 'can_create': False, ...}"
    )

    class Meta:
        verbose_name = "Time-Bound Access"

    def is_active(self) -> bool:
        """Check if access is currently active"""
        from django.utils import timezone
        now = timezone.now()
        return self.access_start <= now <= self.access_end

# Custom permission class
class TimeBoundPermission(permissions.BasePermission):
    """DRF permission that checks time-bound access"""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Check if user has time-bound access
        try:
            access = request.user.time_bound_access
            if not access.is_active():
                return False

            # Check scoped permissions
            if request.method in permissions.SAFE_METHODS:
                return access.access_scope.get('can_view', False)
            elif request.method == 'POST':
                return access.access_scope.get('can_create', False)
            elif request.method in ['PUT', 'PATCH']:
                return access.access_scope.get('can_update', False)
            elif request.method == 'DELETE':
                return access.access_scope.get('can_delete', False)

        except TimeBoundAccess.DoesNotExist:
            pass

        # Fall back to regular permissions
        return True
```

---

#### 8.4 Location-Based Access

**Scenario:** Staff can only access patient data when connected from hospital network or specific locations.

**Implementation:**

```python
# detection/middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
import ipaddress

class LocationBasedAccessMiddleware(MiddlewareMixin):
    """Enforce location-based access control"""

    HOSPITAL_IP_RANGES = [
        ipaddress.ip_network('192.168.1.0/24'),  # Example hospital network
        ipaddress.ip_network('10.0.0.0/16'),     # Example VPN network
    ]

    RESTRICTED_PATHS = [
        '/detection/patient/',
        '/api/predictions/',
        '/medical-records/',
    ]

    def process_request(self, request):
        """Check if request is from allowed location for sensitive paths"""

        # Skip for admin users
        if request.user.is_authenticated and request.user.profile.is_admin():
            return None

        # Check if path requires location check
        requires_check = any(
            request.path.startswith(path)
            for path in self.RESTRICTED_PATHS
        )

        if not requires_check:
            return None

        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        try:
            client_ip = ipaddress.ip_address(ip)

            # Check if IP is in allowed ranges
            is_allowed = any(
                client_ip in network
                for network in self.HOSPITAL_IP_RANGES
            )

            if not is_allowed:
                # Log unauthorized location access attempt
                AuditService.log_location_violation(
                    user=request.user,
                    ip=ip,
                    path=request.path
                )

                return HttpResponseForbidden(
                    "Access denied: This resource can only be accessed from hospital network."
                )

        except ValueError:
            return HttpResponseForbidden("Invalid IP address")

        return None

# config/settings.py
MIDDLEWARE = [
    # ... other middleware
    'detection.middleware.LocationBasedAccessMiddleware',
]
```

---

#### 8.5 Audit Override Permissions

**Scenario:** Compliance officers need read-only access to audit logs and override records without modifying patient data.

**Implementation:**

```python
# detection/models.py
class AuditRole(models.Model):
    """Extended role for audit/compliance officers"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='audit_role')
    can_view_all_audits = models.BooleanField(default=False)
    can_review_emergency_access = models.BooleanField(default=False)
    can_export_compliance_reports = models.BooleanField(default=False)
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    assigned_at = models.DateTimeField(auto_now_add=True)

# Custom decorator for audit permissions
def audit_officer_required(view_func):
    """Decorator for views requiring audit officer role"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            audit_role = request.user.audit_role
            if not audit_role.can_view_all_audits:
                raise PermissionDenied
        except AuditRole.DoesNotExist:
            raise PermissionDenied("Audit officer role required")

        return view_func(request, *args, **kwargs)
    return wrapper

@audit_officer_required
def view_emergency_access_log(request):
    """Compliance view for reviewing emergency access events"""
    emergency_accesses = EmergencyAccess.objects.filter(
        reviewed=False
    ).select_related('user', 'patient').order_by('-accessed_at')

    return render(request, "audit/emergency_access_log.html", {
        "accesses": emergency_accesses
    })
```

---

### 9. Advanced Permission Patterns

Beyond basic RBAC, healthcare applications require advanced permission strategies for data security and compliance.

---

#### 9.1 Row-Level Security (RLS)

**Concept:** Database-level permissions that filter data based on user context automatically.

**Implementation with Django:**

```python
# detection/managers.py
from django.db import models
from django.contrib.auth.models import User

class PatientQuerySet(models.QuerySet):
    """Custom queryset with row-level security"""

    def for_user(self, user: User):
        """Filter patients based on user permissions"""
        if user.profile.is_admin():
            # Admin sees all patients
            return self

        elif user.profile.is_staff():
            # Staff sees assigned patients + delegated patients
            from django.db.models import Q
            from django.utils import timezone
            now = timezone.now()

            return self.filter(
                Q(assigned_staff=user) |  # Direct assignment
                Q(temporarydelegation__delegate=user,  # Delegated access
                  temporarydelegation__active=True,
                  temporarydelegation__start_date__lte=now,
                  temporarydelegation__end_date__gte=now) |
                Q(emergencyaccess__user=user,  # Emergency access
                  emergencyaccess__accessed_at__gte=now - timezone.timedelta(hours=24))
            ).distinct()

        elif user.profile.is_patient():
            # Patients see only themselves
            return self.filter(user=user)

        # No access by default
        return self.none()

class PatientManager(models.Manager):
    """Manager with row-level security"""

    def get_queryset(self):
        return PatientQuerySet(self.model, using=self._db)

    def for_user(self, user: User):
        return self.get_queryset().for_user(user)

# detection/models.py
class Patient(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_info')
    assigned_staff = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_patients'
    )
    # ... other fields

    objects = PatientManager()  # Use custom manager

# Usage in views
@staff_required
def patient_list(request):
    """List patients - automatically filtered by permissions"""
    patients = Patient.objects.for_user(request.user)
    return render(request, "detection/patients.html", {"patients": patients})
```

---

#### 9.2 Multi-Factor Authentication for Sensitive Operations

**Scenario:** Require additional authentication for high-risk operations (deleting records, exporting PHI).

**Implementation:**

```python
# detection/decorators.py
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

def require_mfa_verification(view_func):
    """Require MFA verification before sensitive operation"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        # Check if MFA verified in last 15 minutes
        last_mfa = request.session.get('last_mfa_verification')

        if last_mfa:
            last_mfa_time = timezone.datetime.fromisoformat(last_mfa)
            if timezone.now() - last_mfa_time < timedelta(minutes=15):
                return view_func(request, *args, **kwargs)

        # Redirect to MFA verification
        messages.warning(request, "Please verify your identity to continue.")
        request.session['mfa_redirect'] = request.path
        return redirect('mfa_verification')

    return wrapper

# detection/views.py
@admin_required
@require_mfa_verification
def delete_patient_data(request, patient_id):
    """Delete patient - requires MFA"""
    patient = get_object_or_404(Patient, id=patient_id)

    if request.method == "POST":
        patient.delete()
        messages.success(request, "Patient data deleted.")
        return redirect("patient_list")

    return render(request, "detection/confirm_delete.html", {"patient": patient})

def mfa_verification(request):
    """MFA verification view"""
    if request.method == "POST":
        code = request.POST.get('code')

        # Verify OTP/TOTP code
        if verify_mfa_code(request.user, code):
            request.session['last_mfa_verification'] = timezone.now().isoformat()

            # Redirect to original destination
            redirect_url = request.session.pop('mfa_redirect', 'home')
            return redirect(redirect_url)
        else:
            messages.error(request, "Invalid verification code.")

    return render(request, "detection/mfa_verification.html")
```

---

#### 9.3 Session Management for Healthcare Compliance

**Scenario:** Enforce automatic logout after inactivity, session limits for security.

**Implementation:**

```python
# config/settings.py
# Session security settings
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_SAVE_EVERY_REQUEST = True  # Reset timer on every request
SESSION_COOKIE_SECURE = True  # HTTPS only (production)
SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Strict'  # CSRF protection

# detection/middleware.py
class SessionTimeoutMiddleware(MiddlewareMixin):
    """Enforce session timeout with warning"""

    def process_request(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')

            if last_activity:
                from django.utils import timezone
                last_time = timezone.datetime.fromisoformat(last_activity)
                idle_time = (timezone.now() - last_time).seconds

                # Warn at 50 minutes, logout at 60 minutes
                if idle_time > 3600:  # 60 minutes
                    from django.contrib.auth import logout
                    logout(request)
                    messages.warning(request, "Session expired due to inactivity.")
                    return redirect('login')

                elif idle_time > 3000:  # 50 minutes - add warning
                    request.session['session_expiring_soon'] = True

            # Update last activity
            request.session['last_activity'] = timezone.now().isoformat()
```

---

### 10. Permission Auditing & Compliance Monitoring

Healthcare applications must maintain comprehensive audit trails and monitor for permission violations.

---

#### 10.1 Real-Time Permission Violation Alerts

**Implementation:**

```python
# audit/services.py
class AuditService:
    """Centralized audit logging service"""

    @staticmethod
    def log_permission_violation(
        user: User,
        action: str,
        resource: str,
        reason: str
    ):
        """Log permission violation and send alert"""
        from audit.models import PermissionViolation

        violation = PermissionViolation.objects.create(
            user=user,
            action=action,
            resource=resource,
            reason=reason,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        # Send real-time alert to compliance team
        if violation.is_critical():
            send_security_alert(violation)

        return violation

    @staticmethod
    def log_data_access(user: User, patient: Patient, action: str):
        """Log all patient data access"""
        from audit.models import DataAccessLog

        DataAccessLog.objects.create(
            user=user,
            patient=patient,
            action=action,
            timestamp=timezone.now()
        )

# audit/models.py
class PermissionViolation(TimeStampedModel):
    """Track permission violations"""

    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    resource = models.CharField(max_length=255)
    reason = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    reviewed = models.BooleanField(default=False)

    def is_critical(self) -> bool:
        """Determine if violation requires immediate alert"""
        critical_actions = ['delete_patient', 'export_phi', 'modify_audit_log']
        return self.action in critical_actions or self.severity == 'critical'
```

---

#### 10.2 Compliance Reporting

**Generate HIPAA-compliant audit reports:**

```python
# audit/services.py
class ComplianceReportService:
    """Generate compliance reports"""

    @staticmethod
    def generate_access_report(start_date: datetime, end_date: datetime) -> dict:
        """Generate patient data access report"""
        from audit.models import DataAccessLog, EmergencyAccess

        report = {
            'period': f"{start_date.date()} to {end_date.date()}",
            'total_accesses': DataAccessLog.objects.filter(
                timestamp__range=(start_date, end_date)
            ).count(),
            'emergency_accesses': EmergencyAccess.objects.filter(
                accessed_at__range=(start_date, end_date)
            ).count(),
            'unreviewed_emergency': EmergencyAccess.objects.filter(
                accessed_at__range=(start_date, end_date),
                reviewed=False
            ).count(),
            'violations': PermissionViolation.objects.filter(
                created_at__range=(start_date, end_date)
            ).count(),
        }

        return report
```

---

## Security Checklist

Before deploying any feature with access control:

- [ ] **Public registration only creates patient accounts** (default role='patient')
- [ ] **Admin-only staff creation** (via admin panel or dedicated admin view)
- [ ] **Role checked at view level** (decorator or mixin)
- [ ] **Role checked at API level** (permission classes)
- [ ] **Object-level permissions** (patients can't access others' data)
- [ ] **QuerySet filtering** (patients see only own records)
- [ ] **Template conditionals** (hide UI elements based on role)
- [ ] **Delete operations restricted** (admin full, staff limited, patient none)
- [ ] **Audit logging enabled** (for sensitive operations)
- [ ] **Tests written** (for each role and permission scenario)
- [ ] **No role escalation possible** (patient can't become staff)
- [ ] **No horizontal privilege escalation** (patient can't access other patients' data)

---

## Testing Patterns

**Test user creation with different roles:**

```python
from django.test import TestCase
from django.contrib.auth.models import User
from detection.models import UserProfile

class UserRoleTests(TestCase):

    def setUp(self):
        """Create test users with different roles"""
        self.admin = User.objects.create_user(username="admin", password="admin123")
        self.admin.profile.role = "admin"
        self.admin.profile.save()

        self.staff = User.objects.create_user(username="staff", password="staff123")
        self.staff.profile.role = "staff"
        self.staff.profile.save()

        self.patient = User.objects.create_user(username="patient", password="patient123")
        # Patient is default role

    def test_patient_default_role(self):
        """New users should default to patient role"""
        user = User.objects.create_user(username="newuser", password="pass123")
        self.assertEqual(user.profile.role, "patient")
        self.assertTrue(user.profile.is_patient())

    def test_admin_has_full_permissions(self):
        """Admin should have all permissions"""
        self.assertTrue(self.admin.profile.is_admin())
        self.assertTrue(self.admin.profile.can_create_users())

    def test_staff_cannot_create_users(self):
        """Staff should not be able to create users"""
        self.assertTrue(self.staff.profile.is_staff())
        self.assertFalse(self.staff.profile.can_create_users())

    def test_patient_cannot_create_users(self):
        """Patient should not be able to create users"""
        self.assertTrue(self.patient.profile.is_patient())
        self.assertFalse(self.patient.profile.can_create_users())
```

**Test view access control:**

```python
class ViewAccessControlTests(TestCase):

    def setUp(self):
        self.admin = User.objects.create_user(username="admin", password="admin123")
        self.admin.profile.role = "admin"
        self.admin.profile.save()

        self.staff = User.objects.create_user(username="staff", password="staff123")
        self.staff.profile.role = "staff"
        self.staff.profile.save()

        self.patient = User.objects.create_user(username="patient", password="patient123")

    def test_staff_can_access_upload(self):
        """Staff should be able to access X-ray upload"""
        self.client.login(username="staff", password="staff123")
        response = self.client.get(reverse("upload_xray"))
        self.assertEqual(response.status_code, 200)

    def test_patient_cannot_access_upload(self):
        """Patient should be denied access to X-ray upload"""
        self.client.login(username="patient", password="patient123")
        response = self.client.get(reverse("upload_xray"))
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_only_admin_can_create_staff(self):
        """Only admin should access staff creation view"""
        # Patient attempt
        self.client.login(username="patient", password="patient123")
        response = self.client.get(reverse("create_staff"))
        self.assertEqual(response.status_code, 302)

        # Staff attempt
        self.client.login(username="staff", password="staff123")
        response = self.client.get(reverse("create_staff"))
        self.assertEqual(response.status_code, 302)

        # Admin success
        self.client.login(username="admin", password="admin123")
        response = self.client.get(reverse("create_staff"))
        self.assertEqual(response.status_code, 200)
```

**Test API permissions:**

```python
from rest_framework.test import APITestCase
from rest_framework import status

class APIPredictionPermissionTests(APITestCase):

    def setUp(self):
        self.staff = User.objects.create_user(username="staff", password="staff123")
        self.staff.profile.role = "staff"
        self.staff.profile.save()

        self.patient1 = User.objects.create_user(username="patient1", password="pass123")
        self.patient2 = User.objects.create_user(username="patient2", password="pass123")

        # Create predictions for both patients
        self.pred1 = Prediction.objects.create(patient=self.patient1.patient_info, result="negative")
        self.pred2 = Prediction.objects.create(patient=self.patient2.patient_info, result="positive")

    def test_staff_can_view_all_predictions(self):
        """Staff should see all predictions"""
        self.client.force_authenticate(user=self.staff)
        response = self.client.get('/api/predictions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_patient_can_only_view_own_predictions(self):
        """Patient should only see their own predictions"""
        self.client.force_authenticate(user=self.patient1)
        response = self.client.get('/api/predictions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.pred1.id)

    def test_patient_cannot_create_prediction(self):
        """Patients cannot create predictions (staff only)"""
        self.client.force_authenticate(user=self.patient1)
        data = {'patient': self.patient1.patient_info.id, 'result': 'negative'}
        response = self.client.post('/api/predictions/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create_prediction(self):
        """Staff can create predictions"""
        self.client.force_authenticate(user=self.staff)
        data = {'patient': self.patient1.patient_info.id, 'result': 'negative'}
        response = self.client.post('/api/predictions/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
```

---

## Common Pitfalls to Avoid

1. **Don't rely on frontend-only restrictions** - Always enforce permissions on backend
2. **Don't forget object-level permissions** - Check ownership, not just role
3. **Don't use is_staff from Django User model** - Use `user.profile.is_staff()` for our custom role
4. **Don't allow role changes in forms** - Exclude role field from patient-accessible forms
5. **Don't forget to filter QuerySets** - Patients should never see other patients' data in queries
6. **Don't skip audit logging** - Log all admin and staff actions on patient data
7. **Don't hardcode role strings** - Use UserProfile.ROLE_CHOICES constants
8. **Don't mix authentication and authorization** - `@login_required` checks auth, role checks are separate
9. **Don't forget API permissions** - Views and APIs both need permission checks
10. **Don't allow patient self-promotion** - Registration always creates patient role

---

## Auto-Apply This Skill When:

- Implementing any user authentication or login/logout functionality
- Creating new views, API endpoints, or models that handle user data
- Implementing user registration or account creation
- Adding features that differ by user role (dashboards, uploads, reports)
- Creating any CRUD operations on sensitive data (patients, predictions, medical records)
- Implementing access control for templates or UI elements
- Writing tests for user-related functionality
- Implementing Django admin customizations
- Creating or modifying Django REST Framework ViewSets
- Implementing object-level permissions or ownership checks
- Adding audit logging or compliance features
- Refactoring existing authentication/authorization code
