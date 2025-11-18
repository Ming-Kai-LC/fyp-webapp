from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    """
    Configuration for the Notifications app
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'
    verbose_name = 'Notification System'

    def ready(self):
        """
        Import signals when app is ready
        """
        # Import signals here if needed in the future
        # import notifications.signals
        pass
