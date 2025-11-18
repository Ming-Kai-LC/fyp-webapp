# Notification System Module - Detailed Specification

## Module Information
- **Module Name:** notifications
- **Priority:** HIGH (Phase 1)
- **Estimated Effort:** 1-2 days
- **Dependencies:** detection app, Celery (for async tasks)

## Purpose
Real-time notification system for critical COVID-19 results, appointment reminders, and system alerts via email, SMS, and in-app notifications.

## Features

### Core Features
1. Email notifications (results ready, critical findings)
2. SMS alerts for positive COVID-19 cases
3. In-app notifications with real-time updates
4. Notification preferences management
5. Notification templates
6. Delivery status tracking
7. Emergency contact notifications

### Advanced Features
8. Push notifications (if mobile app exists)
9. Scheduled notifications (appointment reminders)
10. Notification batching (daily digest)
11. Priority-based routing
12. Multi-language support

---

## Database Models

### File: `notifications/models.py`

```python
from django.db import models
from django.conf import settings
from detection.models import Patient, Prediction
import uuid


class NotificationTemplate(models.Model):
    """
    Email/SMS templates for different notification types
    """
    TEMPLATE_TYPES = (
        ('prediction_ready', 'Prediction Ready'),
        ('critical_result', 'Critical Result - COVID Positive'),
        ('appointment_reminder', 'Appointment Reminder'),
        ('appointment_confirmed', 'Appointment Confirmed'),
        ('report_ready', 'Report Ready'),
        ('account_created', 'Account Created'),
        ('password_reset', 'Password Reset'),
        ('test_result_updated', 'Test Result Updated'),
        ('doctor_notes_added', 'Doctor Notes Added'),
    )

    CHANNEL_TYPES = (
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('in_app', 'In-App'),
    )

    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPES, unique=True)
    channel = models.CharField(max_length=20, choices=CHANNEL_TYPES)
    subject = models.CharField(max_length=200, help_text="For email only")
    body_template = models.TextField(help_text="Use {variable} for placeholders")
    is_active = models.BooleanField(default=True)

    # Priority
    is_critical = models.BooleanField(
        default=False,
        help_text="Critical notifications bypass user preferences"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_template_type_display()} - {self.get_channel_display()}"


class Notification(models.Model):
    """
    Individual notification instances
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('read', 'Read'),
    )

    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )

    notification_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Content
    title = models.CharField(max_length=200)
    message = models.TextField()
    channel = models.CharField(
        max_length=20,
        choices=NotificationTemplate.CHANNEL_TYPES,
        default='in_app'
    )

    # Delivery
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    # Delivery details
    recipient_email = models.EmailField(blank=True)
    recipient_phone = models.CharField(max_length=20, blank=True)
    error_message = models.TextField(blank=True)

    # Related objects
    related_prediction = models.ForeignKey(
        Prediction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )
    action_url = models.URLField(blank=True, help_text="Link to related resource")

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['status', 'priority']),
        ]

    def __str__(self):
        return f"{self.recipient.username} - {self.title} ({self.status})"

    def mark_as_read(self):
        from django.utils import timezone
        self.status = 'read'
        self.read_at = timezone.now()
        self.save(update_fields=['status', 'read_at'])


class NotificationPreference(models.Model):
    """
    User notification preferences
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )

    # Channel preferences
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    in_app_enabled = models.BooleanField(default=True)

    # Notification type preferences
    prediction_results = models.BooleanField(default=True)
    appointment_reminders = models.BooleanField(default=True)
    report_ready = models.BooleanField(default=True)
    doctor_notes = models.BooleanField(default=True)
    system_updates = models.BooleanField(default=False)

    # Delivery preferences
    email_address = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    quiet_hours_start = models.TimeField(
        null=True,
        blank=True,
        help_text="Don't send non-critical notifications during quiet hours"
    )
    quiet_hours_end = models.TimeField(null=True, blank=True)

    # Digest preferences
    daily_digest = models.BooleanField(
        default=False,
        help_text="Receive daily summary instead of individual notifications"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Notification Preferences"


class NotificationLog(models.Model):
    """
    Log all notification attempts for debugging
    """
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='delivery_logs'
    )
    attempted_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField()
    channel = models.CharField(max_length=20)
    error_details = models.TextField(blank=True)

    # Provider details (for SMS/email services)
    provider = models.CharField(max_length=50, blank=True)
    provider_response = models.TextField(blank=True)

    class Meta:
        ordering = ['-attempted_at']

    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{self.notification.title} - {status} via {self.channel}"
```

---

## Services

### File: `notifications/services.py`

```python
from django.core.mail import send_mail
from django.conf import settings
from django.template import Template, Context
from django.utils import timezone
from .models import Notification, NotificationTemplate, NotificationLog, NotificationPreference


class NotificationService:
    """
    Core service for sending notifications via multiple channels
    """
    @staticmethod
    def send_notification(user, template_type, context_data, priority='normal', related_prediction=None):
        """
        Send notification using appropriate template and channel
        """
        # Get template
        try:
            template = NotificationTemplate.objects.get(
                template_type=template_type,
                is_active=True
            )
        except NotificationTemplate.DoesNotExist:
            return None

        # Get user preferences
        try:
            prefs = NotificationPreference.objects.get(user=user)
        except NotificationPreference.DoesNotExist:
            # Create default preferences
            prefs = NotificationPreference.objects.create(user=user)

        # Render message
        subject = Template(template.subject).render(Context(context_data)) if template.subject else ''
        message = Template(template.body_template).render(Context(context_data))

        # Create notification record
        notification = Notification.objects.create(
            recipient=user,
            template=template,
            title=subject or template.get_template_type_display(),
            message=message,
            channel=template.channel,
            priority=priority,
            related_prediction=related_prediction,
            recipient_email=prefs.email_address or user.email,
            recipient_phone=prefs.phone_number,
            action_url=context_data.get('action_url', '')
        )

        # Send based on channel and preferences
        if template.is_critical or NotificationService._should_send_now(prefs, template):
            if template.channel == 'email' and prefs.email_enabled:
                NotificationService._send_email(notification)
            elif template.channel == 'sms' and prefs.sms_enabled:
                NotificationService._send_sms(notification)
            elif template.channel == 'in_app':
                notification.status = 'sent'
                notification.sent_at = timezone.now()
                notification.save()

        return notification

    @staticmethod
    def _should_send_now(prefs, template):
        """
        Check if notification should be sent now based on preferences and quiet hours
        """
        # Critical notifications always send
        if template.is_critical:
            return True

        # Check quiet hours for non-critical
        now = timezone.now().time()
        if prefs.quiet_hours_start and prefs.quiet_hours_end:
            if prefs.quiet_hours_start <= now <= prefs.quiet_hours_end:
                return False

        return True

    @staticmethod
    def _send_email(notification):
        """
        Send email notification
        """
        try:
            send_mail(
                subject=notification.title,
                message=notification.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.recipient_email],
                fail_silently=False,
            )

            notification.status = 'sent'
            notification.sent_at = timezone.now()
            notification.save()

            NotificationLog.objects.create(
                notification=notification,
                success=True,
                channel='email'
            )

        except Exception as e:
            notification.status = 'failed'
            notification.error_message = str(e)
            notification.save()

            NotificationLog.objects.create(
                notification=notification,
                success=False,
                channel='email',
                error_details=str(e)
            )

    @staticmethod
    def _send_sms(notification):
        """
        Send SMS notification using Twilio or similar service
        """
        try:
            # Implement SMS sending logic using Twilio, AWS SNS, or similar
            # from twilio.rest import Client
            # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            # message = client.messages.create(
            #     body=notification.message,
            #     from_=settings.TWILIO_PHONE_NUMBER,
            #     to=notification.recipient_phone
            # )

            # For now, mark as sent (implement actual SMS later)
            notification.status = 'sent'
            notification.sent_at = timezone.now()
            notification.save()

            NotificationLog.objects.create(
                notification=notification,
                success=True,
                channel='sms',
                provider='twilio'
            )

        except Exception as e:
            notification.status = 'failed'
            notification.error_message = str(e)
            notification.save()

            NotificationLog.objects.create(
                notification=notification,
                success=False,
                channel='sms',
                error_details=str(e)
            )

    @staticmethod
    def send_prediction_notification(prediction):
        """
        Send notification when prediction is ready
        """
        patient_user = prediction.xray.patient.user
        context = {
            'patient_name': patient_user.get_full_name(),
            'diagnosis': prediction.final_diagnosis,
            'confidence': prediction.consensus_confidence,
            'action_url': f'/detection/results/{prediction.id}/',
        }

        # Determine priority based on diagnosis
        priority = 'critical' if prediction.final_diagnosis == 'COVID' else 'normal'

        return NotificationService.send_notification(
            user=patient_user,
            template_type='prediction_ready' if priority == 'normal' else 'critical_result',
            context_data=context,
            priority=priority,
            related_prediction=prediction
        )


class NotificationScheduler:
    """
    Schedule and batch notifications
    """
    @staticmethod
    def send_daily_digest(user):
        """
        Send daily digest of unread notifications
        """
        unread = Notification.objects.filter(
            recipient=user,
            status='sent',
            read_at__isnull=True,
            created_at__gte=timezone.now() - timezone.timedelta(days=1)
        )

        if unread.count() > 0:
            # Send digest email
            # Implementation here
            pass
```

---

## URL Configuration

### File: `notifications/urls.py`

```python
from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Notification list
    path('', views.notification_list, name='notification_list'),
    path('<uuid:notification_id>/read/', views.mark_as_read, name='mark_as_read'),
    path('mark-all-read/', views.mark_all_as_read, name='mark_all_as_read'),

    # Preferences
    path('preferences/', views.notification_preferences, name='preferences'),

    # API for AJAX
    path('api/unread-count/', views.unread_count_api, name='unread_count_api'),
    path('api/latest/', views.latest_notifications_api, name='latest_notifications_api'),
]
```

---

## Integration Points

### 1. Update `config/settings.py`

```python
INSTALLED_APPS = [
    # ... existing apps ...
    'notifications',
]

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-password'
DEFAULT_FROM_EMAIL = 'COVID-19 Detection System <noreply@example.com>'

# SMS settings (Twilio)
# TWILIO_ACCOUNT_SID = 'your-account-sid'
# TWILIO_AUTH_TOKEN = 'your-auth-token'
# TWILIO_PHONE_NUMBER = '+1234567890'
```

### 2. Trigger notifications from detection views

```python
# In detection/views.py after prediction creation
from notifications.services import NotificationService
NotificationService.send_prediction_notification(prediction)
```

---

## Dependencies

```
# Add to requirements.txt
twilio==8.10.0  # For SMS (optional)
celery==5.3.4   # For async task processing
redis==5.0.1    # For Celery broker
```

---

## Success Criteria

- ✅ Email notifications sent for critical results
- ✅ In-app notifications display in real-time
- ✅ Users can manage notification preferences
- ✅ SMS alerts for COVID-positive cases
- ✅ Notification history is tracked
- ✅ Delivery failures are logged and retried
