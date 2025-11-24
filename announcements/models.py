"""
Announcements Models
Demonstrates usage of foundation components (TimeStampedModel)
"""

from django.db import models
from django.contrib.auth.models import User

# ✅ FOUNDATION: Import abstract base model
from common.models import TimeStampedModel


class Announcement(TimeStampedModel):
    """
    Announcement model for system-wide announcements.

    ✅ Inherits from TimeStampedModel - automatically gets:
    - created_at (auto timestamp on creation)
    - updated_at (auto timestamp on modification)
    - Meta.ordering = ['-created_at']

    This eliminates 5-10 lines of boilerplate code!
    """

    # Priority levels
    PRIORITY_INFO = 'info'
    PRIORITY_WARNING = 'warning'
    PRIORITY_URGENT = 'urgent'

    PRIORITY_CHOICES = [
        (PRIORITY_INFO, 'Information'),
        (PRIORITY_WARNING, 'Warning'),
        (PRIORITY_URGENT, 'Urgent'),
    ]

    title = models.CharField(
        max_length=200,
        help_text="Announcement title (max 200 characters)"
    )

    message = models.TextField(
        help_text="Announcement message content"
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_INFO,
        help_text="Priority level of the announcement"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Whether this announcement is currently active"
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='announcements',
        help_text="User who created this announcement"
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this announcement expires (optional)"
    )

    class Meta:
        verbose_name = 'Announcement'
        verbose_name_plural = 'Announcements'
        # ✅ TimeStampedModel already provides ordering = ['-created_at']
        # No need to duplicate it!
        indexes = [
            models.Index(fields=['is_active', '-created_at']),
            models.Index(fields=['priority', '-created_at']),
        ]

    def __str__(self) -> str:
        """String representation of announcement."""
        return f"{self.get_priority_display()}: {self.title}"

    def is_expired(self) -> bool:
        """Check if announcement has expired."""
        from django.utils import timezone
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    @property
    def priority_badge_class(self) -> str:
        """Get Bootstrap badge class for priority."""
        priority_classes = {
            self.PRIORITY_INFO: 'info',
            self.PRIORITY_WARNING: 'warning',
            self.PRIORITY_URGENT: 'danger',
        }
        return priority_classes.get(self.priority, 'secondary')
