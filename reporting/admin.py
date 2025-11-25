from django.contrib import admin
from .models import ReportTemplate, Report, BatchReportJob


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'is_active', 'created_at']
    list_filter = ['template_type', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['report_id', 'patient_name', 'diagnosis', 'created_at', 'status', 'download_count']
    list_filter = ['status', 'created_at', 'include_signature']
    search_fields = ['report_id', 'patient__user__first_name', 'patient__user__last_name']
    readonly_fields = ['report_id', 'created_at', 'file_size', 'downloaded_count', 'last_downloaded_at']

    def patient_name(self, obj):
        return obj.patient.user.get_full_name()
    patient_name.short_description = 'Patient'

    def diagnosis(self, obj):
        return obj.prediction.final_diagnosis
    diagnosis.short_description = 'Diagnosis'

    def download_count(self, obj):
        return obj.downloaded_count
    download_count.short_description = 'Downloads'


@admin.register(BatchReportJob)
class BatchReportJobAdmin(admin.ModelAdmin):
    list_display = ['job_id', 'created_by', 'status', 'progress_display', 'created_at', 'completed_at']
    list_filter = ['status', 'created_at']
    readonly_fields = ['job_id', 'created_at', 'completed_at', 'total_reports', 'completed_reports', 'failed_reports']

    def progress_display(self, obj):
        return f"{obj.get_progress_percentage()}%"
    progress_display.short_description = 'Progress'
