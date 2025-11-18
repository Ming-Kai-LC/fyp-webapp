from django.contrib import admin
from .models import (
    AuditLog, DataAccessLog, LoginAttempt, DataChange,
    ComplianceReport, DataRetentionPolicy, SecurityAlert
)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'username', 'action_type', 'action_description', 'severity', 'success']
    list_filter = ['action_type', 'severity', 'success', 'timestamp']
    search_fields = ['username', 'action_description', 'ip_address']
    readonly_fields = ['timestamp', 'user', 'username']
    date_hierarchy = 'timestamp'


@admin.register(DataAccessLog)
class DataAccessLogAdmin(admin.ModelAdmin):
    list_display = ['accessed_at', 'accessor', 'patient', 'data_type', 'access_type', 'flagged_for_review']
    list_filter = ['access_type', 'flagged_for_review', 'accessed_at']
    search_fields = ['accessor__username', 'patient__user__username']
    readonly_fields = ['accessed_at']
    date_hierarchy = 'accessed_at'


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'username', 'success', 'ip_address', 'is_suspicious']
    list_filter = ['success', 'is_suspicious', 'timestamp']
    search_fields = ['username', 'ip_address']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'


@admin.register(SecurityAlert)
class SecurityAlertAdmin(admin.ModelAdmin):
    list_display = ['triggered_at', 'alert_type', 'severity', 'acknowledged', 'user']
    list_filter = ['alert_type', 'severity', 'acknowledged', 'triggered_at']
    readonly_fields = ['triggered_at']
    date_hierarchy = 'triggered_at'


@admin.register(ComplianceReport)
class ComplianceReportAdmin(admin.ModelAdmin):
    list_display = ['generated_at', 'report_type', 'generated_by', 'start_date', 'end_date']
    list_filter = ['report_type', 'generated_at']
    readonly_fields = ['generated_at']


@admin.register(DataRetentionPolicy)
class DataRetentionPolicyAdmin(admin.ModelAdmin):
    list_display = ['data_type', 'retention_days', 'is_active', 'auto_delete']
    list_filter = ['is_active', 'auto_delete']


@admin.register(DataChange)
class DataChangeAdmin(admin.ModelAdmin):
    list_display = ['changed_at', 'content_type', 'object_id', 'field_name', 'changed_by']
    list_filter = ['content_type', 'changed_at']
    readonly_fields = ['changed_at']
    date_hierarchy = 'changed_at'
