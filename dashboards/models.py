# dashboards/models.py
"""
Enhanced Dashboards Module - Database Models
Store user dashboard customization preferences and widget definitions
"""

from django.db import models
from django.conf import settings
from common.models import TimeStampedModel


class DashboardPreference(TimeStampedModel):
    """
    Store user dashboard customization preferences

    Inherits from TimeStampedModel:
    - Timestamps: created_at, updated_at
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dashboard_preferences'
    )

    # Layout preferences
    widget_layout = models.JSONField(
        default=dict,
        help_text="Widget positions and sizes"
    )
    theme = models.CharField(
        max_length=20,
        choices=[('light', 'Light'), ('dark', 'Dark')],
        default='light'
    )

    # Widget visibility
    visible_widgets = models.JSONField(
        default=list,
        help_text="List of visible widget IDs"
    )

    # Refresh settings
    auto_refresh = models.BooleanField(default=True)
    refresh_interval = models.IntegerField(
        default=60,
        help_text="Auto-refresh interval in seconds"
    )

    # updated_at inherited from TimeStampedModel

    class Meta:
        verbose_name = "Dashboard Preference"
        verbose_name_plural = "Dashboard Preferences"

    def __str__(self):
        return f"{self.user.username} - Dashboard Preferences"


class DashboardWidget(TimeStampedModel):
    """
    Define available dashboard widgets

    Inherits from TimeStampedModel:
    - Timestamps: created_at, updated_at
    """
    WIDGET_TYPES = (
        ('statistics', 'Statistics Card'),
        ('chart', 'Chart/Graph'),
        ('table', 'Data Table'),
        ('list', 'List View'),
        ('calendar', 'Calendar'),
        ('notifications', 'Notifications'),
        ('quick_actions', 'Quick Actions'),
        ('custom', 'Custom Widget'),
    )

    widget_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)

    # Access control
    available_for_roles = models.JSONField(
        default=list,
        help_text="List of roles that can see this widget"
    )

    # Default settings
    default_size = models.CharField(
        max_length=20,
        choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')],
        default='medium'
    )
    default_position = models.IntegerField(default=0)

    # Metadata
    is_active = models.BooleanField(default=True)
    # created_at inherited from TimeStampedModel

    class Meta:
        ordering = ['default_position']
        verbose_name = "Dashboard Widget"
        verbose_name_plural = "Dashboard Widgets"

    def __str__(self):
        return self.name
