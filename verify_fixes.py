"""
Verification script for user data fixes
Run with: python manage.py runscript verify_fixes
Or: python verify_fixes.py (after setup)
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from detection.models import UserProfile, Patient

print("=" * 60)
print("VERIFICATION REPORT - User Data Integrity")
print("=" * 60)
print()

# Check 1: Patient Records
print("1. Patient Records Check:")
patient_users = UserProfile.objects.filter(role='patient')
all_ok = True
for p in patient_users:
    has_patient = Patient.objects.filter(user=p.user).exists()
    status = "OK" if has_patient else "MISSING"
    if not has_patient:
        all_ok = False
    print(f"   - {p.user.username}: {status}")
print()

# Check 2: Staff Permissions
print("2. Staff Permission Check:")
staff_users = UserProfile.objects.filter(role='staff')
for s in staff_users:
    status = "OK" if s.user.is_staff else "MISMATCH"
    if not s.user.is_staff:
        all_ok = False
    print(f"   - {s.user.username}: is_staff={s.user.is_staff} ({status})")
print()

# Check 3: User Counts
print("3. User Count by Role:")
for role in ['admin', 'staff', 'patient']:
    count = UserProfile.objects.filter(role=role).count()
    print(f"   - {role}: {count} users")
print()

# Check 4: Profile Completion
print("4. Profile Completion Status:")
from detection.decorators import get_profile_completion_status
for profile in UserProfile.objects.all():
    is_complete, missing, percentage = get_profile_completion_status(profile.user)
    status = "Complete" if is_complete else f"{percentage}% (missing: {', '.join(missing)})"
    print(f"   - {profile.user.username} ({profile.role}): {status}")
print()

print("=" * 60)
if all_ok:
    print("STATUS: All checks passed!")
else:
    print("STATUS: Some issues found - see details above")
print("=" * 60)
