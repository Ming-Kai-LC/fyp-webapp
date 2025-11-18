from django.apps import AppConfig


class AuditConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'audit'
    verbose_name = 'Audit & Compliance'

    def ready(self):
        """
        Import signals when the app is ready
        """
        import audit.signals
