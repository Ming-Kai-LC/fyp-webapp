# Appointment & Scheduling Module - Detailed Specification

## Module Information
- **Module Name:** appointments
- **Priority:** MEDIUM-HIGH (Phase 2)
- **Estimated Effort:** 2-3 days
- **Dependencies:** detection app, notifications module

## Purpose
Streamline doctor-patient consultations with calendar-based appointment booking, reminders, and schedule management.

## Features

### Core Features
1. Calendar-based appointment booking
2. Doctor availability management
3. Patient appointment history
4. Automated reminders (email/SMS)
5. Appointment status tracking (scheduled, completed, cancelled, no-show)
6. Multiple appointment types (consultation, follow-up, X-ray, virtual)
7. Waitlist management

### Advanced Features
8. Recurring appointments
9. Video consultation integration
10. Calendar sync (Google Calendar, iCal)
11. No-show tracking and penalties
12. Appointment analytics
13. Multi-doctor scheduling

---

## Database Models

### File: `appointments/models.py`

```python
from django.db import models
from django.conf import settings
from detection.models import Patient
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from datetime import timedelta


class DoctorSchedule(models.Model):
    """
    Define doctor's working hours and availability
    """
    DAY_CHOICES = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )

    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'profile__role': 'doctor'},
        related_name='schedules'
    )
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    # Appointment duration
    slot_duration = models.IntegerField(
        default=30,
        help_text="Duration of each appointment slot in minutes"
    )

    # Capacity
    max_appointments_per_slot = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )

    class Meta:
        ordering = ['day_of_week', 'start_time']
        unique_together = ['doctor', 'day_of_week', 'start_time']

    def __str__(self):
        return f"{self.doctor.get_full_name()} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class Appointment(models.Model):
    """
    Individual appointment instances
    """
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled_patient', 'Cancelled by Patient'),
        ('cancelled_doctor', 'Cancelled by Doctor'),
        ('no_show', 'No Show'),
        ('rescheduled', 'Rescheduled'),
    )

    APPOINTMENT_TYPES = (
        ('consultation', 'General Consultation'),
        ('follow_up', 'Follow-up'),
        ('xray_review', 'X-ray Review'),
        ('results_discussion', 'Results Discussion'),
        ('virtual', 'Virtual Consultation'),
        ('emergency', 'Emergency'),
    )

    appointment_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # Who
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'profile__role': 'doctor'},
        related_name='doctor_appointments'
    )

    # When
    appointment_date = models.DateField(db_index=True)
    appointment_time = models.TimeField()
    duration = models.IntegerField(default=30, help_text="Duration in minutes")
    end_time = models.TimeField(blank=True)

    # What
    appointment_type = models.CharField(max_length=30, choices=APPOINTMENT_TYPES, default='consultation')
    reason = models.TextField()
    notes = models.TextField(blank=True, help_text="Patient notes")

    # Status
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='scheduled')

    # Booking details
    booked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='booked_appointments'
    )
    booked_at = models.DateTimeField(auto_now_add=True)

    # Confirmation
    confirmed_at = models.DateTimeField(null=True, blank=True)
    confirmation_sent = models.BooleanField(default=False)

    # Reminders
    reminder_sent = models.BooleanField(default=False)
    reminder_sent_at = models.DateTimeField(null=True, blank=True)

    # Completion
    completed_at = models.DateTimeField(null=True, blank=True)
    doctor_notes = models.TextField(blank=True, help_text="Doctor notes after appointment")

    # Cancellation
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)

    # Virtual consultation
    is_virtual = models.BooleanField(default=False)
    video_link = models.URLField(blank=True)

    # Follow-up
    is_follow_up = models.BooleanField(default=False)
    parent_appointment = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='follow_ups'
    )

    class Meta:
        ordering = ['appointment_date', 'appointment_time']
        indexes = [
            models.Index(fields=['doctor', 'appointment_date']),
            models.Index(fields=['patient', 'appointment_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.patient.user.get_full_name()} - {self.doctor.get_full_name()} - {self.appointment_date} {self.appointment_time}"

    def save(self, *args, **kwargs):
        # Calculate end time
        from datetime import datetime, timedelta
        if self.appointment_time and self.duration:
            dt = datetime.combine(self.appointment_date, self.appointment_time)
            end_dt = dt + timedelta(minutes=self.duration)
            self.end_time = end_dt.time()
        super().save(*args, **kwargs)


class AppointmentReminder(models.Model):
    """
    Track appointment reminders
    """
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='reminders')
    reminder_type = models.CharField(
        max_length=20,
        choices=[('24h', '24 Hours Before'), ('2h', '2 Hours Before'), ('custom', 'Custom')]
    )
    scheduled_for = models.DateTimeField()
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    channel = models.CharField(
        max_length=20,
        choices=[('email', 'Email'), ('sms', 'SMS'), ('both', 'Both')]
    )

    class Meta:
        ordering = ['scheduled_for']

    def __str__(self):
        return f"Reminder for {self.appointment.appointment_id} - {self.reminder_type}"


class Waitlist(models.Model):
    """
    Manage waitlist for fully booked slots
    """
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='waitlist_entries')
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='waitlist'
    )
    preferred_date = models.DateField()
    preferred_time_start = models.TimeField()
    preferred_time_end = models.TimeField()
    appointment_type = models.CharField(max_length=30, choices=Appointment.APPOINTMENT_TYPES)
    reason = models.TextField()

    # Status
    is_active = models.BooleanField(default=True)
    added_at = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)
    notified_at = models.DateTimeField(null=True, blank=True)

    # Conversion
    converted_to_appointment = models.ForeignKey(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='from_waitlist'
    )

    class Meta:
        ordering = ['added_at']

    def __str__(self):
        return f"{self.patient.user.get_full_name()} - Waitlist for {self.doctor.get_full_name()}"


class DoctorLeave(models.Model):
    """
    Track doctor leaves/holidays to block appointments
    """
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leaves'
    )
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=200, blank=True)
    is_approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.doctor.get_full_name()} - Leave from {self.start_date} to {self.end_date}"
```

---

## Services

### File: `appointments/services.py`

```python
from datetime import datetime, timedelta, time
from django.utils import timezone
from .models import DoctorSchedule, Appointment, AppointmentReminder, Waitlist


class AppointmentScheduler:
    """
    Service for finding available appointment slots
    """
    @staticmethod
    def get_available_slots(doctor, date):
        """
        Get available time slots for a doctor on a specific date
        """
        day_of_week = date.weekday()

        # Get doctor's schedule for this day
        schedules = DoctorSchedule.objects.filter(
            doctor=doctor,
            day_of_week=day_of_week,
            is_active=True
        )

        if not schedules.exists():
            return []

        available_slots = []

        for schedule in schedules:
            # Generate time slots
            current_time = datetime.combine(date, schedule.start_time)
            end_datetime = datetime.combine(date, schedule.end_time)

            while current_time < end_datetime:
                slot_time = current_time.time()

                # Check if slot is available
                existing_appointments = Appointment.objects.filter(
                    doctor=doctor,
                    appointment_date=date,
                    appointment_time=slot_time,
                    status__in=['scheduled', 'confirmed', 'in_progress']
                ).count()

                if existing_appointments < schedule.max_appointments_per_slot:
                    available_slots.append({
                        'time': slot_time,
                        'duration': schedule.slot_duration,
                        'available_spots': schedule.max_appointments_per_slot - existing_appointments
                    })

                current_time += timedelta(minutes=schedule.slot_duration)

        return available_slots

    @staticmethod
    def book_appointment(patient, doctor, appointment_date, appointment_time, **kwargs):
        """
        Book an appointment
        """
        # Create appointment
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            **kwargs
        )

        # Schedule reminders
        AppointmentScheduler.schedule_reminders(appointment)

        # Send confirmation
        from notifications.services import NotificationService
        NotificationService.send_notification(
            user=patient.user,
            template_type='appointment_confirmed',
            context_data={
                'patient_name': patient.user.get_full_name(),
                'doctor_name': doctor.get_full_name(),
                'date': appointment_date,
                'time': appointment_time,
                'appointment_type': appointment.get_appointment_type_display(),
            },
            priority='normal'
        )

        return appointment

    @staticmethod
    def schedule_reminders(appointment):
        """
        Schedule appointment reminders
        """
        appointment_datetime = datetime.combine(
            appointment.appointment_date,
            appointment.appointment_time
        )

        # 24 hours before
        reminder_24h = appointment_datetime - timedelta(hours=24)
        if reminder_24h > timezone.now():
            AppointmentReminder.objects.create(
                appointment=appointment,
                reminder_type='24h',
                scheduled_for=reminder_24h,
                channel='email'
            )

        # 2 hours before
        reminder_2h = appointment_datetime - timedelta(hours=2)
        if reminder_2h > timezone.now():
            AppointmentReminder.objects.create(
                appointment=appointment,
                reminder_type='2h',
                scheduled_for=reminder_2h,
                channel='sms'
            )

    @staticmethod
    def send_due_reminders():
        """
        Send all due reminders (run via Celery periodic task)
        """
        due_reminders = AppointmentReminder.objects.filter(
            sent=False,
            scheduled_for__lte=timezone.now()
        )

        for reminder in due_reminders:
            from notifications.services import NotificationService
            NotificationService.send_notification(
                user=reminder.appointment.patient.user,
                template_type='appointment_reminder',
                context_data={
                    'patient_name': reminder.appointment.patient.user.get_full_name(),
                    'doctor_name': reminder.appointment.doctor.get_full_name(),
                    'date': reminder.appointment.appointment_date,
                    'time': reminder.appointment.appointment_time,
                },
                priority='high'
            )

            reminder.sent = True
            reminder.sent_at = timezone.now()
            reminder.save()
```

---

## URL Configuration

### File: `appointments/urls.py`

```python
from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    # Booking
    path('book/', views.book_appointment, name='book_appointment'),
    path('available-slots/', views.get_available_slots_api, name='available_slots_api'),

    # Management
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('<uuid:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('<uuid:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('<uuid:appointment_id>/reschedule/', views.reschedule_appointment, name='reschedule_appointment'),
    path('<uuid:appointment_id>/complete/', views.complete_appointment, name='complete_appointment'),

    # Doctor schedule
    path('doctor/schedule/', views.manage_schedule, name='manage_schedule'),
    path('doctor/appointments/', views.doctor_appointments, name='doctor_appointments'),

    # Waitlist
    path('waitlist/join/', views.join_waitlist, name='join_waitlist'),
]
```

---

## Integration Points

- Link to notifications module for reminders
- Add appointment booking from patient dashboard
- Doctor calendar view in doctor dashboard
- Integration with video consultation platform (Zoom, Google Meet)

---

## Success Criteria

- ✅ Patients can book appointments online
- ✅ Doctors can manage their schedules
- ✅ Automated reminders reduce no-shows
- ✅ Waitlist system handles fully booked slots
- ✅ Calendar view shows doctor availability
- ✅ Appointment history is tracked
