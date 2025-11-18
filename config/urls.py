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
    path("admin/", admin.site.urls),
    # Home page
    path("", detection_views.home, name="home"),
    # Authentication
    path(
        "accounts/", include("django.contrib.auth.urls")
    ),  # Login, logout, password reset
    path("register/", detection_views.register, name="register"),
    # Detection app URLs
    path("detection/", include("detection.urls")),
    # Reporting app URLs
    path("reporting/", include("reporting.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
