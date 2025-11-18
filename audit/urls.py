from django.urls import path
from . import views

app_name = 'audit'

urlpatterns = [
    # Audit logs
    path('logs/', views.audit_log_list, name='audit_log_list'),
    path('data-access/', views.data_access_log_list, name='data_access_log_list'),
    path('login-attempts/', views.login_attempts_list, name='login_attempts_list'),

    # Security alerts
    path('security/alerts/', views.security_alerts_dashboard, name='security_alerts_dashboard'),
    path('security/alert/<int:alert_id>/acknowledge/', views.acknowledge_alert, name='acknowledge_alert'),

    # Compliance reports
    path('compliance/generate/', views.generate_compliance_report, name='generate_compliance_report'),
    path('compliance/view/<int:report_id>/', views.view_compliance_report, name='view_compliance_report'),

    # Export
    path('export/csv/', views.export_audit_logs, name='export_audit_logs'),

    # User access
    path('my-history/', views.my_access_history, name='my_access_history'),
    path('changes/<int:content_type_id>/<int:object_id>/', views.data_change_history, name='data_change_history'),
]
