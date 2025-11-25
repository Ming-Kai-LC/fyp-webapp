from django.contrib import admin
from .models import (
    AuditLog, DataAccessLog, LoginAttempt, DataChange,
    ComplianceReport, DataRetentionPolicy, SecurityAlert
)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'username', 'action_type', 'action_description', 'severity', 'success']
    list_filter = ['action_type', 'severity', 'success', 'created_at']
    search_fields = ['username', 'action_description', 'ip_address']
    readonly_fields = ['created_at', 'user', 'username']
    date_hierarchy = 'created_at'


@admin.register(DataAccessLog)
class DataAccessLogAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'accessor', 'patient', 'data_type', 'access_type', 'flagged_for_review']
    list_filter = ['access_type', 'flagged_for_review', 'created_at']
    search_fields = ['accessor__username', 'patient__user__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'username', 'success', 'ip_address', 'is_suspicious']
    list_filter = ['success', 'is_suspicious', 'created_at']
    search_fields = ['username', 'ip_address']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(SecurityAlert)
class SecurityAlertAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'alert_type', 'severity', 'acknowledged', 'user']
    list_filter = ['alert_type', 'severity', 'acknowledged', 'created_at']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(ComplianceReport)
class ComplianceReportAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'report_type', 'generated_by', 'start_date', 'end_date']
    list_filter = ['report_type', 'created_at']
    readonly_fields = ['created_at']


@admin.register(DataRetentionPolicy)
class DataRetentionPolicyAdmin(admin.ModelAdmin):
    list_display = ['data_type', 'retention_days', 'is_active', 'auto_delete']
    list_filter = ['is_active', 'auto_delete']


@admin.register(DataChange)
class DataChangeAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'content_type', 'object_id', 'field_name', 'changed_by']
    list_filter = ['content_type', 'created_at']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
