# detection/urls.py
"""
URL Configuration for Detection App
"""

from django.urls import path
from . import views

app_name = "detection"

urlpatterns = [
    # Dashboards
    path("staff/dashboard/", views.staff_dashboard, name="staff_dashboard"),
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
    # Staff actions
    path(
        "add-notes/<int:prediction_id>/",
        views.add_doctor_notes,
        name="add_doctor_notes",
    ),
    # User profile (all roles)
    path("profile/", views.user_profile, name="user_profile"),
    # API endpoints
    path("api/models/", views.api_model_info, name="api_model_info"),
]
