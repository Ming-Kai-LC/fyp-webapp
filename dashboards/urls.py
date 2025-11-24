# dashboards/urls.py
"""
Enhanced Dashboards Module - URL Configuration
"""

from django.urls import path
from . import views

app_name = 'dashboards'

urlpatterns = [
    # Enhanced dashboards
    path('staff/', views.enhanced_staff_dashboard, name='staff'),
    path('patient/', views.enhanced_patient_dashboard, name='patient'),
    path('admin/', views.enhanced_admin_dashboard, name='admin'),

    # Widget management
    path('preferences/', views.dashboard_preferences, name='preferences'),
    path('widgets/toggle/', views.toggle_widget, name='toggle_widget'),
]
