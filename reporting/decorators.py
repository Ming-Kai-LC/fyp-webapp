from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def doctor_required(view_func):
    """
    Decorator to ensure user is a doctor or admin
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            messages.error(request, "You don't have permission to access this page.")
            return redirect('detection:home')

        if not (request.user.profile.is_doctor() or request.user.profile.is_admin()):
            messages.error(request, "Only doctors can access this page.")
            return redirect('detection:patient_dashboard')

        return view_func(request, *args, **kwargs)

    return wrapper
