"""
Django app configuration for API module
"""
from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Configuration for API app"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = 'REST API'
