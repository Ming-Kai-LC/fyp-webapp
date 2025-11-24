# config/urls.py
"""
Main URL Configuration for COVID-19 Detection System
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from detection import views as detection_views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger documentation schema
schema_view = get_schema_view(
    openapi.Info(
        title="COVID-19 Detection API",
        default_version='v1',
        description="RESTful API for COVID-19 Detection System using CrossViT and Multi-Model Ensemble",
        terms_of_service="https://www.example.com/policies/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin panel
    path("admin/", admin.site.urls),
    # Home page
    path("", detection_views.home, name="home"),
    # Authentication
    path("accounts/login/", detection_views.CustomLoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("accounts/password_change/", auth_views.PasswordChangeView.as_view(), name="password_change"),
    path("accounts/password_change/done/", auth_views.PasswordChangeDoneView.as_view(), name="password_change_done"),
    path("accounts/password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("accounts/password_reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("accounts/reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("accounts/reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path("register/", detection_views.register, name="register"),
    # Detection app URLs
    path("detection/", include("detection.urls")),
    # Medical records URLs
    path("medical-records/", include("medical_records.urls")),
    # Reporting URLs
    path("reporting/", include("reporting.urls")),
    # Audit & Compliance URLs
    path("audit/", include("audit.urls")),
    # Notifications URLs
    path("notifications/", include("notifications.urls")),
    # Appointments URLs
    path("appointments/", include("appointments.urls")),
    # Analytics URLs
    path("analytics/", include("analytics.urls")),
    # Enhanced Dashboards URLs
    path("dashboards/", include("dashboards.urls")),
    # Announcements URLs (Test module demonstrating foundation components)
    path("announcements/", include("announcements.urls")),

    # ===== REST API =====
    path("api/v1/", include("api.urls")),

    # ===== API Documentation (Swagger/OpenAPI) =====
    path("api/docs/", schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path("api/redoc/", schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path("api/schema/", schema_view.without_ui(cache_timeout=0), name='schema-json'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
