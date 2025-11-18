# analytics/admin.py
"""
Django admin configuration for Analytics models
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    AnalyticsSnapshot,
    ModelPerformanceMetric,
    CustomReport,
    DataExport
)


@admin.register(AnalyticsSnapshot)
class AnalyticsSnapshotAdmin(admin.ModelAdmin):
    """
    Admin interface for Analytics Snapshots
    """
    list_display = [
        'snapshot_date',
        'period_type',
        'total_predictions',
        'covid_positive',
        'normal_cases',
        'avg_confidence_display',
        'created_at',
    ]
    list_filter = [
        'period_type',
        'snapshot_date',
    ]
    search_fields = [
        'snapshot_date',
    ]
    ordering = ['-snapshot_date']
    readonly_fields = [
        'created_at',
    ]

    fieldsets = (
        ('Snapshot Info', {
            'fields': ('period_type', 'snapshot_date')
        }),
        ('Prediction Statistics', {
            'fields': (
                'total_predictions',
                'covid_positive',
                'normal_cases',
                'viral_pneumonia',
                'lung_opacity',
            )
        }),
        ('User Statistics', {
            'fields': (
                'total_patients',
                'new_patients',
                'active_doctors',
            )
        }),
        ('Performance Metrics', {
            'fields': (
                'avg_inference_time',
                'avg_confidence',
                'model_accuracy',
            )
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )

    def avg_confidence_display(self, obj):
        """Display average confidence as percentage"""
        if obj.avg_confidence:
            return f"{obj.avg_confidence:.2f}%"
        return "N/A"
    avg_confidence_display.short_description = 'Avg Confidence'


@admin.register(ModelPerformanceMetric)
class ModelPerformanceMetricAdmin(admin.ModelAdmin):
    """
    Admin interface for Model Performance Metrics
    """
    list_display = [
        'model_name',
        'date',
        'total_predictions',
        'avg_confidence_display',
        'avg_inference_time_display',
        'accuracy_display',
    ]
    list_filter = [
        'model_name',
        'date',
    ]
    search_fields = [
        'model_name',
    ]
    ordering = ['-date', 'model_name']
    readonly_fields = [
        'created_at',
    ]

    fieldsets = (
        ('Model Info', {
            'fields': ('model_name', 'date')
        }),
        ('Performance Metrics', {
            'fields': (
                'total_predictions',
                'avg_confidence',
                'avg_inference_time',
            )
        }),
        ('Accuracy Metrics', {
            'fields': (
                'accuracy',
                'precision',
                'recall',
                'f1_score',
                'agreement_rate',
            )
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )

    def avg_confidence_display(self, obj):
        """Display average confidence"""
        return f"{obj.avg_confidence:.2f}%"
    avg_confidence_display.short_description = 'Avg Confidence'

    def avg_inference_time_display(self, obj):
        """Display average inference time"""
        return f"{obj.avg_inference_time:.3f}s"
    avg_inference_time_display.short_description = 'Avg Time'

    def accuracy_display(self, obj):
        """Display accuracy if available"""
        if obj.accuracy:
            return f"{obj.accuracy:.2f}%"
        return "N/A"
    accuracy_display.short_description = 'Accuracy'


@admin.register(CustomReport)
class CustomReportAdmin(admin.ModelAdmin):
    """
    Admin interface for Custom Reports
    """
    list_display = [
        'name',
        'report_type',
        'chart_type',
        'created_by',
        'is_public_icon',
        'created_at',
    ]
    list_filter = [
        'report_type',
        'chart_type',
        'is_public',
        'created_at',
    ]
    search_fields = [
        'name',
        'description',
        'created_by__username',
    ]
    ordering = ['-created_at']
    readonly_fields = [
        'created_at',
        'created_by',
    ]

    fieldsets = (
        ('Report Info', {
            'fields': ('name', 'report_type', 'description')
        }),
        ('Configuration', {
            'fields': ('filters', 'chart_type')
        }),
        ('Ownership', {
            'fields': ('created_by', 'created_at', 'is_public')
        }),
    )

    def is_public_icon(self, obj):
        """Display public status as icon"""
        if obj.is_public:
            return format_html('<span style="color: green;">✓ Public</span>')
        return format_html('<span style="color: gray;">Private</span>')
    is_public_icon.short_description = 'Visibility'

    def save_model(self, request, obj, form, change):
        """Auto-set created_by to current user"""
        if not change:  # Only set on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(DataExport)
class DataExportAdmin(admin.ModelAdmin):
    """
    Admin interface for Data Exports
    """
    list_display = [
        'export_type',
        'exported_by',
        'exported_at',
        'record_count',
        'file_format',
        'anonymized_icon',
    ]
    list_filter = [
        'export_type',
        'file_format',
        'anonymized',
        'exported_at',
    ]
    search_fields = [
        'exported_by__username',
        'export_type',
    ]
    ordering = ['-exported_at']
    readonly_fields = [
        'exported_at',
        'exported_by',
    ]

    fieldsets = (
        ('Export Info', {
            'fields': ('export_type', 'file_format', 'record_count')
        }),
        ('Filters Applied', {
            'fields': (
                'filters_applied',
                'date_range_start',
                'date_range_end',
            )
        }),
        ('File', {
            'fields': ('file_path',)
        }),
        ('Metadata', {
            'fields': ('exported_by', 'exported_at', 'anonymized')
        }),
    )

    def anonymized_icon(self, obj):
        """Display anonymization status as icon"""
        if obj.anonymized:
            return format_html('<span style="color: green;">✓ Anonymized</span>')
        return format_html('<span style="color: orange;">Not Anonymized</span>')
    anonymized_icon.short_description = 'Anonymization'

    def save_model(self, request, obj, form, change):
        """Auto-set exported_by to current user"""
        if not change:  # Only set on creation
            obj.exported_by = request.user
        super().save_model(request, obj, form, change)


# Customize admin site header
admin.site.site_header = "COVID-19 Detection System - Analytics Administration"
admin.site.site_title = "Analytics Admin"
admin.site.index_title = "Analytics Management"
