from django.contrib import admin
from .models import NotificationTemplate, Notification, NotificationPreference, NotificationLog


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    """
    Admin interface for NotificationTemplate
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
    Inline admin for NotificationLog
    """
    model = NotificationLog
    extra = 0
    readonly_fields = ['attempted_at', 'success', 'channel', 'error_details', 'provider', 'provider_response']
    can_delete = False


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin interface for Notification
    """
    list_display = ['title', 'recipient', 'channel', 'status', 'priority', 'created_at', 'sent_at']
    list_filter = ['status', 'priority', 'channel', 'created_at']
    search_fields = ['title', 'message', 'recipient__username', 'recipient__email']
    readonly_fields = ['notification_id', 'created_at', 'sent_at', 'read_at']
    date_hierarchy = 'created_at'
    inlines = [NotificationLogInline]

    fieldsets = (
        ('Recipient Information', {
            'fields': ('recipient', 'notification_id')
        }),
        ('Content', {
            'fields': ('template', 'title', 'message', 'channel')
        }),
        ('Delivery Status', {
            'fields': ('status', 'priority', 'created_at', 'sent_at', 'read_at')
        }),
        ('Delivery Details', {
            'fields': ('recipient_email', 'recipient_phone', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Related Objects', {
            'fields': ('related_prediction', 'action_url'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_sent', 'mark_as_read', 'resend_notification']

    def mark_as_sent(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='sent', sent_at=timezone.now())
        self.message_user(request, f'{updated} notifications marked as sent')
    mark_as_sent.short_description = "Mark selected notifications as sent"

    def mark_as_read(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='read', read_at=timezone.now())
        self.message_user(request, f'{updated} notifications marked as read')
    mark_as_read.short_description = "Mark selected notifications as read"

    def resend_notification(self, request, queryset):
        from .services import NotificationService
        count = 0
        for notification in queryset:
            if notification.channel == 'email':
                NotificationService._send_email(notification)
                count += 1
            elif notification.channel == 'sms':
                NotificationService._send_sms(notification)
                count += 1
        self.message_user(request, f'{count} notifications resent')
    resend_notification.short_description = "Resend selected notifications"


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """
    Admin interface for NotificationPreference
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
        ('Notification Type Preferences', {
            'fields': ('prediction_results', 'appointment_reminders', 'report_ready', 'doctor_notes', 'system_updates')
        }),
        ('Delivery Preferences', {
            'fields': ('email_address', 'phone_number', 'quiet_hours_start', 'quiet_hours_end')
        }),
        ('Digest Preferences', {
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
    Admin interface for NotificationLog
    """
    list_display = ['notification', 'channel', 'success', 'attempted_at', 'provider']
    list_filter = ['success', 'channel', 'provider', 'attempted_at']
    search_fields = ['notification__title', 'error_details', 'provider_response']
    readonly_fields = ['notification', 'attempted_at', 'success', 'channel', 'error_details', 'provider', 'provider_response']
    date_hierarchy = 'attempted_at'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
