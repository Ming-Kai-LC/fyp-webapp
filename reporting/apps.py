from django.apps import AppConfig


class ReportingConfig(AppConfig):
    """
    Configuration for the Reporting application
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reporting'
    verbose_name = 'COVID-19 Report Generation'

    def ready(self):
        """
        Import signals and perform startup tasks
        """
        pass
