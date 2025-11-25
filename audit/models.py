from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from common.models import TimeStampedModel
import json


class AuditLog(TimeStampedModel):
    """
    Comprehensive audit trail for all system activities

    Inherits from TimeStampedModel:
    - Timestamps: created_at (log time), updated_at
    """
    ACTION_TYPES = (
        ('create', 'Create'),
        ('read', 'Read/View'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('login_failed', 'Failed Login'),
        ('export', 'Data Export'),
        ('report', 'Report Generation'),
        ('upload', 'File Upload'),
        ('download', 'File Download'),
        ('permission_change', 'Permission Change'),
        ('password_change', 'Password Change'),
        ('other', 'Other'),
    )

    SEVERITY_LEVELS = (
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    )

    # Who
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    username = models.CharField(max_length=150, blank=True)  # Store username even if user deleted

    # What
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    action_description = models.CharField(max_length=500)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='info')

    # When - Note: timestamp is now created_at (inherited from TimeStampedModel)

    # Where (network info)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_key = models.CharField(max_length=40, blank=True)

    # Context (what was affected)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Details
    old_value = models.JSONField(null=True, blank=True, help_text="Previous state before change")
    new_value = models.JSONField(null=True, blank=True, help_text="New state after change")
    additional_data = models.JSONField(null=True, blank=True, help_text="Extra context data")

    # Status
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action_type', '-created_at']),
            models.Index(fields=['created_at']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f"{self.username or 'Anonymous'} - {self.action_type} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

    @classmethod
    def log(cls, user, action_type, description, **kwargs):
        """
        Convenience method to create audit log entries
        """
        return cls.objects.create(
            user=user,
            username=user.username if user and user.is_authenticated else 'Anonymous',
            action_type=action_type,
            action_description=description,
            **kwargs
        )


class DataAccessLog(TimeStampedModel):
    """
    Specific tracking for patient data access (HIPAA compliance)

    Inherits from TimeStampedModel:
    - Timestamps: created_at (access time), updated_at
    """
    ACCESS_TYPES = (
        ('view', 'View'),
        ('download', 'Download'),
        ('export', 'Export'),
        ('print', 'Print'),
        ('share', 'Share'),
    )

    # Who accessed
    accessor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='data_accesses'
    )
    accessor_role = models.CharField(max_length=20)  # doctor, admin, patient

    # What was accessed
    patient = models.ForeignKey(
        'detection.Patient',
        on_delete=models.CASCADE,
        related_name='access_logs'
    )
    data_type = models.CharField(max_length=50)  # 'prediction', 'xray', 'medical_history', etc.
    data_id = models.PositiveIntegerField()

    # How
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPES)
    access_reason = models.TextField(blank=True, help_text="Purpose of access")

    # When - Note: accessed_at is now created_at (inherited from TimeStampedModel)

    # Where
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    # Context
    is_legitimate = models.BooleanField(
        default=True,
        help_text="Whether access was for legitimate medical purpose"
    )
    flagged_for_review = models.BooleanField(default=False)
    review_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', '-created_at']),
            models.Index(fields=['accessor', '-created_at']),
            models.Index(fields=['flagged_for_review']),
        ]

    def __str__(self):
        return f"{self.accessor.username if self.accessor else 'Unknown'} accessed {self.patient.user.get_full_name()}'s {self.data_type}"


class LoginAttempt(TimeStampedModel):
    """
    Track all login attempts for security monitoring

    Inherits from TimeStampedModel:
    - Timestamps: created_at (attempt time), updated_at
    """
    username = models.CharField(max_length=150, db_index=True)
    success = models.BooleanField()
    # Note: timestamp is now created_at (inherited from TimeStampedModel)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    failure_reason = models.CharField(max_length=200, blank=True)

    # Security flags
    is_suspicious = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['username', '-created_at']),
            models.Index(fields=['ip_address', '-created_at']),
            models.Index(fields=['is_suspicious']),
        ]

    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{self.username} - {status} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"


class DataChange(TimeStampedModel):
    """
    Track changes to critical medical data with full history

    Inherits from TimeStampedModel:
    - Timestamps: created_at (change time), updated_at
    """
    # What was changed
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Who changed it
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='data_changes'
    )

    # When - Note: changed_at is now created_at (inherited from TimeStampedModel)

    # Details
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)

    # Context
    change_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id', '-created_at']),
        ]

    def __str__(self):
        return f"{self.field_name} changed by {self.changed_by.username if self.changed_by else 'System'}"


class ComplianceReport(TimeStampedModel):
    """
    Generated compliance reports for regulatory review

    Inherits from TimeStampedModel:
    - Timestamps: created_at (generated time), updated_at
    """
    REPORT_TYPES = (
        ('hipaa_audit', 'HIPAA Audit Report'),
        ('gdpr_compliance', 'GDPR Compliance Report'),
        ('access_review', 'Data Access Review'),
        ('security_audit', 'Security Audit'),
        ('user_activity', 'User Activity Report'),
    )

    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    # Note: generated_at is now created_at (inherited from TimeStampedModel)

    # Date range for report
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    # Report data
    summary = models.JSONField(help_text="Summary statistics")
    details = models.JSONField(help_text="Detailed findings")

    # Files
    pdf_file = models.FileField(upload_to='compliance_reports/%Y/%m/', null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.created_at.strftime('%Y-%m-%d')}"


class DataRetentionPolicy(TimeStampedModel):
    """
    Define and enforce data retention policies

    Inherits from TimeStampedModel:
    - Timestamps: created_at, updated_at
    """
    data_type = models.CharField(max_length=100, unique=True)
    retention_days = models.IntegerField(help_text="Number of days to retain data")
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    # created_at, updated_at inherited from TimeStampedModel

    # Enforcement
    auto_delete = models.BooleanField(
        default=False,
        help_text="Automatically delete data after retention period"
    )
    notify_before_days = models.IntegerField(
        default=30,
        help_text="Notify admins N days before deletion"
    )

    class Meta:
        verbose_name_plural = "Data Retention Policies"

    def __str__(self):
        return f"{self.data_type} - {self.retention_days} days"


class SecurityAlert(TimeStampedModel):
    """
    Real-time security alerts for suspicious activities

    Inherits from TimeStampedModel:
    - Timestamps: created_at (triggered time), updated_at
    """
    ALERT_TYPES = (
        ('failed_login', 'Multiple Failed Logins'),
        ('unusual_access', 'Unusual Data Access Pattern'),
        ('bulk_export', 'Bulk Data Export'),
        ('privilege_escalation', 'Privilege Escalation Attempt'),
        ('after_hours', 'After Hours Access'),
        ('other', 'Other'),
    )

    ALERT_SEVERITY = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )

    alert_type = models.CharField(max_length=50, choices=ALERT_TYPES)
    severity = models.CharField(max_length=10, choices=ALERT_SEVERITY)
    description = models.TextField()
    # Note: triggered_at is now created_at (inherited from TimeStampedModel)

    # Related user
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='security_alerts'
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    # Resolution
    acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_alerts'
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)

    # Actions taken
    auto_blocked = models.BooleanField(default=False)
    admin_notified = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['acknowledged', '-created_at']),
            models.Index(fields=['severity', '-created_at']),
        ]

    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.severity} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
