from django.db.models.signals import post_save, post_delete, pre_save
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import AuditLog, LoginAttempt, DataChange
from detection.models import Prediction, Patient, XRayImage


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    Log successful user login
    """
    AuditLog.log(
        user=user,
        action_type='login',
        description=f"User logged in successfully",
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        severity='info'
    )

    LoginAttempt.objects.create(
        username=user.username,
        success=True,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """
    Log user logout
    """
    if user:
        AuditLog.log(
            user=user,
            action_type='logout',
            description=f"User logged out",
            ip_address=get_client_ip(request),
            severity='info'
        )


@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    """
    Log failed login attempt
    """
    username = credentials.get('username', 'Unknown')
    ip_address = get_client_ip(request)

    AuditLog.log(
        user=None,
        action_type='login_failed',
        description=f"Failed login attempt for username: {username}",
        ip_address=ip_address,
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        severity='warning'
    )

    LoginAttempt.objects.create(
        username=username,
        success=False,
        ip_address=ip_address,
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        failure_reason='Invalid credentials'
    )

    # Check for suspicious activity
    from .services import SecurityMonitor
    SecurityMonitor.check_failed_login_attempts(username, ip_address)


@receiver(pre_save)
def track_model_changes(sender, instance, **kwargs):
    """
    Track changes to critical models
    """
    # Only track specific models
    tracked_models = [Prediction, Patient]

    if sender not in tracked_models:
        return

    # Only for updates (not creates)
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            content_type = ContentType.objects.get_for_model(sender)

            # Compare fields
            for field in instance._meta.fields:
                field_name = field.name
                old_value = getattr(old_instance, field_name, None)
                new_value = getattr(instance, field_name, None)

                if old_value != new_value:
                    DataChange.objects.create(
                        content_type=content_type,
                        object_id=instance.pk,
                        changed_by=getattr(instance, '_changed_by', None),
                        field_name=field_name,
                        old_value=str(old_value),
                        new_value=str(new_value)
                    )

        except sender.DoesNotExist:
            pass


def get_client_ip(request):
    """
    Get client IP address from request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    # Default to localhost if IP not available (e.g., in tests)
    return ip if ip else '127.0.0.1'
