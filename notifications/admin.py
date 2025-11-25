from django.contrib import admin
from .models import NotificationTemplate, Notification, NotificationPreference, NotificationLog


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    """
    Admin interface for notification templates
    """
    list_display = ['template_type', 'channel', 'is_active', 'is_critical', 'created_at']
    list_filter = ['channel', 'is_active', 'is_critical', 'template_type']
    search_fields = ['template_type', 'subject', 'body_template']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Template Information', {
            'fields': ('template_type', 'channel', 'is_active', 'is_critical')
        }),
        ('Content', {
            'fields': ('subject', 'body_template')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class NotificationLogInline(admin.TabularInline):
    """
    Inline display of notification logs
    """
    model = NotificationLog
    extra = 0
    readonly_fields = ['created_at', 'success', 'channel', 'error_details', 'provider', 'provider_response']
    can_delete = False


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin interface for notifications
    """
    list_display = ['title', 'recipient', 'channel', 'status', 'priority', 'created_at', 'sent_at']
    list_filter = ['status', 'priority', 'channel', 'created_at']
    search_fields = ['title', 'message', 'recipient__username', 'recipient__email']
    readonly_fields = ['notification_id', 'created_at', 'sent_at', 'read_at']
    date_hierarchy = 'created_at'
    inlines = [NotificationLogInline]

    fieldsets = (
        ('Notification Details', {
            'fields': ('notification_id', 'recipient', 'template', 'title', 'message')
        }),
        ('Delivery Information', {
            'fields': ('channel', 'status', 'priority', 'recipient_email', 'recipient_phone')
        }),
        ('Related Objects', {
            'fields': ('related_prediction', 'action_url')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'sent_at', 'read_at'),
            'classes': ('collapse',)
        }),
        ('Error Information', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('recipient', 'template', 'related_prediction')


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """
    Admin interface for notification preferences
    """
    list_display = ['user', 'email_enabled', 'sms_enabled', 'in_app_enabled', 'daily_digest']
    list_filter = ['email_enabled', 'sms_enabled', 'in_app_enabled', 'daily_digest']
    search_fields = ['user__username', 'user__email', 'email_address', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Channel Preferences', {
            'fields': ('email_enabled', 'sms_enabled', 'in_app_enabled')
        }),
        ('Notification Types', {
            'fields': ('prediction_results', 'appointment_reminders', 'report_ready',
                      'doctor_notes', 'system_updates')
        }),
        ('Contact Information', {
            'fields': ('email_address', 'phone_number')
        }),
        ('Quiet Hours', {
            'fields': ('quiet_hours_start', 'quiet_hours_end'),
            'classes': ('collapse',)
        }),
        ('Digest Options', {
            'fields': ('daily_digest',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    """
    Admin interface for notification logs
    """
    list_display = ['notification', 'channel', 'success', 'created_at', 'provider']
    list_filter = ['success', 'channel', 'provider', 'created_at']
    search_fields = ['notification__title', 'error_details', 'provider_response']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Log Information', {
            'fields': ('notification', 'created_at', 'success', 'channel')
        }),
        ('Provider Details', {
            'fields': ('provider', 'provider_response'),
            'classes': ('collapse',)
        }),
        ('Error Details', {
            'fields': ('error_details',),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('notification', 'notification__recipient')
