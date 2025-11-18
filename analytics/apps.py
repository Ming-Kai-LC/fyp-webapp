# analytics/apps.py
from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    """
    Analytics module configuration
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analytics'
    verbose_name = 'Advanced Analytics'

    def ready(self):
        """
        Import signal handlers when app is ready
        """
        # Import signals here if needed
        pass
