# detection/urls.py
"""
URL Configuration for Detection App
"""

from django.urls import path
from . import views

app_name = "detection"

urlpatterns = [
    # Dashboards
    path("doctor/dashboard/", views.doctor_dashboard, name="doctor_dashboard"),
    path("patient/dashboard/", views.patient_dashboard, name="patient_dashboard"),
    # Upload & Prediction
    path("upload/", views.upload_xray, name="upload_xray"),
    path("results/<int:prediction_id>/", views.view_results, name="view_results"),
    path(
        "explain/<int:prediction_id>/",
        views.explain_prediction,
        name="explain_prediction",
    ),
    path("history/", views.prediction_history, name="prediction_history"),
    # Doctor actions
    path(
        "add-notes/<int:prediction_id>/",
        views.add_doctor_notes,
        name="add_doctor_notes",
    ),
    # Patient profile
    path("patient/profile/", views.patient_profile, name="patient_profile"),
    # API endpoints
    path("api/models/", views.api_model_info, name="api_model_info"),
]
