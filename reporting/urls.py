from django.urls import path
from . import views

app_name = 'reporting'

urlpatterns = [
    # Report generation
    path('generate/<int:prediction_id>/', views.generate_report, name='generate_report'),
    path('view/<uuid:report_id>/', views.view_report, name='view_report'),
    path('download/<uuid:report_id>/', views.download_report, name='download_report'),

    # Report management
    path('list/', views.report_list, name='report_list'),
    path('templates/', views.manage_templates, name='manage_templates'),

    # Batch operations
    path('batch/generate/', views.batch_generate_reports, name='batch_generate'),
    path('batch/status/<uuid:job_id>/', views.batch_job_status, name='batch_job_status'),
    path('batch/download/<uuid:job_id>/', views.download_batch_reports, name='download_batch_reports'),

    # Export
    path('export/excel/', views.export_to_excel, name='export_to_excel'),

    # API
    path('api/batch/<uuid:job_id>/progress/', views.batch_job_progress_api, name='batch_job_progress_api'),
]
