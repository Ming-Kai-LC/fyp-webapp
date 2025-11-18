# dashboards/admin.py
"""
Enhanced Dashboards Module - Admin Configuration
"""

from django.contrib import admin
from .models import DashboardPreference, DashboardWidget


@admin.register(DashboardPreference)
class DashboardPreferenceAdmin(admin.ModelAdmin):
    """
    Admin interface for Dashboard Preferences
    """
    list_display = ['user', 'theme', 'auto_refresh', 'refresh_interval', 'updated_at']
    list_filter = ['theme', 'auto_refresh']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['updated_at']

    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Appearance Settings', {
            'fields': ('theme', 'widget_layout', 'visible_widgets')
        }),
        ('Refresh Settings', {
            'fields': ('auto_refresh', 'refresh_interval')
        }),
        ('Metadata', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    """
    Admin interface for Dashboard Widgets
    """
    list_display = ['name', 'widget_id', 'widget_type', 'default_size', 'default_position', 'is_active']
    list_filter = ['widget_type', 'is_active', 'default_size']
    search_fields = ['name', 'widget_id', 'description']
    list_editable = ['is_active', 'default_position']

    fieldsets = (
        ('Widget Information', {
            'fields': ('widget_id', 'name', 'description', 'widget_type')
        }),
        ('Access Control', {
            'fields': ('available_for_roles',)
        }),
        ('Display Settings', {
            'fields': ('default_size', 'default_position', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at']
