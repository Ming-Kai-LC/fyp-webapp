from django.apps import AppConfig


class CommonConfig(AppConfig):
    """
    Configuration for the common app.

    This app provides foundation components used across all modules:
    - Abstract base models (TimeStampedModel, FullAuditModel, etc.)
    - Bootstrap form widgets
    - Common utilities and validators
    - Template tags and filters
    - System checks to enforce foundation-components skill compliance
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'common'

    def ready(self):
        """
        Import checks module to register custom Django system checks.

        These checks automatically run during:
        - python manage.py check
        - python manage.py runserver
        - python manage.py migrate

        They enforce that all models inherit from foundation base classes.
        """
        # Import checks to register them with Django's check framework
        from common import checks  # noqa: F401
