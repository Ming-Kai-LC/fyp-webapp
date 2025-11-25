"""
Custom decorators for detection app
Includes profile completion checks, role-based access control, etc.
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

from detection.constants import ProfileFieldDisplayNames


def get_profile_completion_status(user):
    """
    Check if user profile is complete based on their role.
    Returns: (is_complete: bool, missing_fields: list, completion_percentage: int)

    Note: missing_fields returns human-readable field names for display in UI.
          Uses ProfileFieldDisplayNames from detection.constants for consistency.
    """
    profile = user.profile
    missing_fields = []
    total_fields = 0
    completed_fields = 0

    # Required fields for all users
    required_for_all = {
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
    }

    total_fields += len(required_for_all)
    for field_name, field_value in required_for_all.items():
        if field_value:
            completed_fields += 1
        else:
            # Use centralized human-readable display name
            missing_fields.append(ProfileFieldDisplayNames.get_display(field_name))

    # Role-specific required fields
    if profile.is_patient():
        # Additional required fields for patients
        try:
            patient = user.patient_info
            patient_required = {
                'date_of_birth': patient.date_of_birth,
                'emergency_contact': patient.emergency_contact,
                'gender': patient.gender if patient.gender != 'O' else None,  # 'O' is default, not filled
            }
            total_fields += len(patient_required)
            for field_name, field_value in patient_required.items():
                if field_value:
                    completed_fields += 1
                else:
                    # Use centralized human-readable display name
                    missing_fields.append(ProfileFieldDisplayNames.get_display(field_name))
        except Exception:
            # If patient record doesn't exist or has issues
            missing_fields.extend([
                ProfileFieldDisplayNames.get_display('date_of_birth'),
                ProfileFieldDisplayNames.get_display('emergency_contact'),
                ProfileFieldDisplayNames.get_display('gender'),
            ])
            total_fields += 3

    elif profile.is_staff() or profile.is_admin():
        # Additional recommended field for staff/admin (not strictly required)
        # We'll just check the basics are filled
        pass

    # Calculate completion percentage
    completion_percentage = int((completed_fields / total_fields) * 100) if total_fields > 0 else 0
    is_complete = len(missing_fields) == 0

    return is_complete, missing_fields, completion_percentage


def profile_completion_required(allow_partial=False):
    """
    Decorator to ensure user has completed their profile before accessing certain views.

    Args:
        allow_partial (bool): If True, allows access with 70%+ completion.
                              If False, requires 100% completion.

    Usage:
        @profile_completion_required()
        def my_view(request):
            ...

        @profile_completion_required(allow_partial=True)
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            # Get profile completion status
            is_complete, missing_fields, completion_percentage = get_profile_completion_status(request.user)

            # Check if completion requirement is met
            if allow_partial:
                # Allow access if 70% or more complete
                if completion_percentage < 70:
                    messages.warning(
                        request,
                        f"Your profile is only {completion_percentage}% complete. "
                        f"Please complete your profile to access all features."
                    )
                    return redirect('detection:user_profile')
            else:
                # Require 100% completion
                if not is_complete:
                    missing_str = ', '.join(missing_fields)
                    messages.warning(
                        request,
                        f"Please complete your profile before accessing this feature. "
                        f"Missing fields: {missing_str}"
                    )
                    return redirect('detection:user_profile')

            # Profile is complete or meets threshold, allow access
            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator


def profile_completion_context(request):
    """
    Context processor to add profile completion status to all templates.

    Add to settings.py:
        'context_processors': [
            ...
            'detection.decorators.profile_completion_context',
        ]
    """
    if request.user.is_authenticated:
        is_complete, missing_fields, completion_percentage = get_profile_completion_status(request.user)
        return {
            'profile_is_complete': is_complete,
            'profile_missing_fields': missing_fields,
            'profile_completion_percentage': completion_percentage,
        }
    return {
        'profile_is_complete': True,  # Don't show warnings for anonymous users
        'profile_missing_fields': [],
        'profile_completion_percentage': 100,
    }
