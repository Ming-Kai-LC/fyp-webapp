from django.contrib import admin
from .models import (
    AnalyticsSnapshot,
    ModelPerformanceMetric,
    CustomReport,
    DataExport
)


@admin.register(AnalyticsSnapshot)
class AnalyticsSnapshotAdmin(admin.ModelAdmin):
    list_display = [
        'snapshot_date',
        'period_type',
        'total_predictions',
        'covid_positive',
        'normal_cases',
        'avg_confidence',
    ]
    list_filter = ['period_type', 'snapshot_date']
    search_fields = ['snapshot_date']
    ordering = ['-snapshot_date']
    readonly_fields = ['created_at']


@admin.register(ModelPerformanceMetric)
class ModelPerformanceMetricAdmin(admin.ModelAdmin):
    list_display = [
        'model_name',
        'date',
        'total_predictions',
        'avg_confidence',
        'avg_inference_time',
        'agreement_rate',
    ]
    list_filter = ['model_name', 'date']
    search_fields = ['model_name']
    ordering = ['-date', 'model_name']
    readonly_fields = ['created_at']


@admin.register(CustomReport)
class CustomReportAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'report_type',
        'chart_type',
        'created_by',
        'created_at',
        'is_public',
    ]
    list_filter = ['report_type', 'chart_type', 'is_public', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['-created_at']
    readonly_fields = ['created_at']


@admin.register(DataExport)
class DataExportAdmin(admin.ModelAdmin):
    list_display = [
        'export_type',
        'exported_by',
        'exported_at',
        'file_format',
        'record_count',
        'anonymized',
    ]
    list_filter = ['export_type', 'file_format', 'anonymized', 'exported_at']
    search_fields = ['exported_by__username']
    ordering = ['-exported_at']
    readonly_fields = ['exported_at']
