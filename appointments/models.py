"""
Appointment & Scheduling Module - Models

This module defines the database models for appointment scheduling and management.

Models:
    - DoctorSchedule: Doctor's working hours and availability
    - Appointment: Individual appointment instances
    - AppointmentReminder: Automated appointment reminders
    - Waitlist: Patient waitlist for fully booked slots
    - DoctorLeave: Doctor leave/holiday tracking
"""

from django.db import models
from django.conf import settings
from detection.models import Patient
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from datetime import datetime, timedelta


class DoctorSchedule(models.Model):
    """
    Define doctor's working hours and availability.

    This model stores recurring weekly schedules for doctors,
    including working hours, slot duration, and capacity.

    Attributes:
        doctor: The doctor this schedule belongs to
        day_of_week: Day of the week (0=Monday, 6=Sunday)
        start_time: Schedule start time
        end_time: Schedule end time
        is_active: Whether this schedule is currently active
        slot_duration: Duration of each appointment slot in minutes
        max_appointments_per_slot: Maximum concurrent appointments per slot
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
        verbose_name = "Doctor Schedule"
        verbose_name_plural = "Doctor Schedules"

    def __str__(self) -> str:
        return f"{self.doctor.get_full_name()} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class Appointment(models.Model):
    """
    Individual appointment instances.

    This model represents a specific appointment between a patient and doctor
    at a specific date and time.

    Attributes:
        appointment_id: Unique UUID identifier
        patient: The patient for this appointment
        doctor: The doctor for this appointment
        appointment_date: Date of the appointment
        appointment_time: Time of the appointment
        duration: Duration in minutes
        end_time: Calculated end time
        appointment_type: Type of appointment (consultation, follow-up, etc.)
        reason: Reason for appointment
        notes: Patient notes
        status: Current status of the appointment
        booked_by: User who booked the appointment
        booked_at: Timestamp when booked
        confirmed_at: Timestamp when confirmed
        confirmation_sent: Whether confirmation was sent
        reminder_sent: Whether reminder was sent
        reminder_sent_at: Timestamp when reminder was sent
        completed_at: Timestamp when completed
        doctor_notes: Doctor's notes after appointment
        cancelled_at: Timestamp when cancelled
        cancellation_reason: Reason for cancellation
        is_virtual: Whether this is a virtual consultation
        video_link: Link for virtual consultation
        is_follow_up: Whether this is a follow-up appointment
        parent_appointment: Link to parent appointment if follow-up
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
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"
        indexes = [
            models.Index(fields=['doctor', 'appointment_date']),
            models.Index(fields=['patient', 'appointment_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self) -> str:
        return f"{self.patient.user.get_full_name()} - {self.doctor.get_full_name()} - {self.appointment_date} {self.appointment_time}"

    def save(self, *args, **kwargs):
        """
        Override save to calculate end_time based on duration.
        """
        if self.appointment_time and self.duration:
            dt = datetime.combine(self.appointment_date, self.appointment_time)
            end_dt = dt + timedelta(minutes=self.duration)
            self.end_time = end_dt.time()
        super().save(*args, **kwargs)


class AppointmentReminder(models.Model):
    """
    Track appointment reminders.

    This model stores scheduled reminders for appointments
    to reduce no-shows.

    Attributes:
        appointment: The appointment this reminder is for
        reminder_type: Type of reminder (24h, 2h, custom)
        scheduled_for: When this reminder should be sent
        sent: Whether the reminder has been sent
        sent_at: Timestamp when sent
        channel: Delivery channel (email, SMS, both)
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
        verbose_name = "Appointment Reminder"
        verbose_name_plural = "Appointment Reminders"

    def __str__(self) -> str:
        return f"Reminder for {self.appointment.appointment_id} - {self.reminder_type}"


class Waitlist(models.Model):
    """
    Manage waitlist for fully booked slots.

    When all appointment slots are full, patients can join
    a waitlist and be notified when slots become available.

    Attributes:
        patient: The patient on the waitlist
        doctor: The doctor they want to see
        preferred_date: Preferred appointment date
        preferred_time_start: Preferred start time
        preferred_time_end: Preferred end time
        appointment_type: Type of appointment requested
        reason: Reason for appointment
        is_active: Whether this waitlist entry is active
        added_at: Timestamp when added to waitlist
        notified: Whether patient has been notified of availability
        notified_at: Timestamp when notified
        converted_to_appointment: Link to appointment if converted
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
        verbose_name = "Waitlist Entry"
        verbose_name_plural = "Waitlist Entries"

    def __str__(self) -> str:
        return f"{self.patient.user.get_full_name()} - Waitlist for {self.doctor.get_full_name()}"


class DoctorLeave(models.Model):
    """
    Track doctor leaves/holidays to block appointments.

    This model prevents appointments from being booked
    when doctors are on leave.

    Attributes:
        doctor: The doctor taking leave
        start_date: Leave start date
        end_date: Leave end date
        reason: Reason for leave
        is_approved: Whether the leave is approved
        created_at: Timestamp when leave was created
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
        verbose_name = "Doctor Leave"
        verbose_name_plural = "Doctor Leaves"

    def __str__(self) -> str:
        return f"{self.doctor.get_full_name()} - Leave from {self.start_date} to {self.end_date}"
