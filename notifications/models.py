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
