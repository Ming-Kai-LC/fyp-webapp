from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Main dashboard
    path('dashboard/', views.analytics_dashboard, name='dashboard'),

    # Specific analytics
    path('trends/', views.trend_analysis, name='trends'),
    path('models/', views.model_comparison, name='model_comparison'),
    path('demographics/', views.demographic_analysis, name='demographics'),
    path('predictions/', views.prediction_analytics, name='predictions'),

    # Custom reports
    path('reports/', views.custom_reports, name='custom_reports'),
    path('reports/create/', views.create_custom_report, name='create_custom_report'),
    path('reports/<int:report_id>/', views.view_custom_report, name='view_custom_report'),

    # Data export
    path('export/', views.export_data, name='export_data'),

    # API endpoints
    path('api/snapshot/<str:date>/', views.snapshot_api, name='snapshot_api'),
    path('api/trends/<int:days>/', views.trends_api, name='trends_api'),
]
