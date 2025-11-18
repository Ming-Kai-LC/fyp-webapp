from django.apps import AppConfig


class AppointmentsConfig(AppConfig):
    """
    Configuration for the Appointments & Scheduling module.

    This module handles:
    - Calendar-based appointment booking
    - Doctor availability management
    - Patient appointment history
    - Automated reminders (email/SMS)
    - Waitlist management
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appointments'
    verbose_name = 'Appointment & Scheduling'
