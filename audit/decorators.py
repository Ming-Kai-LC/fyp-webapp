from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def admin_required(view_func):
    """
    Decorator to ensure user is an admin
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            messages.error(request, "You don't have permission to access this page.")
            return redirect('home')

        if not request.user.profile.is_admin():
            messages.error(request, "Only administrators can access this page.")
            return redirect('home')

        return view_func(request, *args, **kwargs)

    return wrapper


def log_data_access(data_type):
    """
    Decorator to automatically log patient data access
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Execute the view
            response = view_func(request, *args, **kwargs)

            # Log the access (implement based on your needs)
            # This is a simplified example
            if request.user.is_authenticated and hasattr(request.user, 'profile'):
                from .models import DataAccessLog
                # Extract patient from kwargs if available
                patient_id = kwargs.get('patient_id') or request.GET.get('patient_id')
                if patient_id:
                    try:
                        from detection.models import Patient
                        patient = Patient.objects.get(id=patient_id)
                        DataAccessLog.objects.create(
                            accessor=request.user,
                            accessor_role=request.user.profile.role,
                            patient=patient,
                            data_type=data_type,
                            data_id=patient_id,
                            access_type='view',
                            ip_address=get_client_ip(request)
                        )
                    except Patient.DoesNotExist:
                        pass

            return response

        return wrapper
    return decorator


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
