# config/urls.py
"""
Main URL Configuration for COVID-19 Detection System
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from detection import views as detection_views

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # Home page
    path('', detection_views.home, name='home'),
    
    # Authentication
    path('accounts/', include('django.contrib.auth.urls')),  # Login, logout, password reset
    path('register/', detection_views.register, name='register'),
    
    # Detection app URLs
    path('detection/', include('detection.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# ================================================================
# detection/urls.py
"""
URL Configuration for Detection App
"""

from django.urls import path
from . import views

app_name = 'detection'

urlpatterns = [
    # Dashboards
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    
    # Upload & Prediction
    path('upload/', views.upload_xray, name='upload_xray'),
    path('results/<int:prediction_id>/', views.view_results, name='view_results'),
    path('explain/<int:prediction_id>/', views.explain_prediction, name='explain_prediction'),
    path('history/', views.prediction_history, name='prediction_history'),
    
    # Doctor actions
    path('add-notes/<int:prediction_id>/', views.add_doctor_notes, name='add_doctor_notes'),
    
    # Patient profile
    path('patient/profile/', views.patient_profile, name='patient_profile'),
    
    # API endpoints
    path('api/models/', views.api_model_info, name='api_model_info'),
]
