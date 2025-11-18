"""
Appointment & Scheduling Module - Services

This module contains the business logic for appointment scheduling,
including slot availability, booking, and reminder management.

Classes:
    - AppointmentScheduler: Core scheduling and booking service
"""

from datetime import datetime, timedelta, time
from django.utils import timezone
from typing import List, Dict, Optional
import logging

from .models import DoctorSchedule, Appointment, AppointmentReminder, Waitlist, DoctorLeave

logger = logging.getLogger(__name__)


class AppointmentScheduler:
    """
    Service for finding available appointment slots and managing bookings.

    This service handles:
    - Finding available time slots for doctors
    - Booking new appointments
    - Scheduling automated reminders
    - Sending due reminders
    """

    @staticmethod
    def get_available_slots(doctor, date) -> List[Dict]:
        """
        Get available time slots for a doctor on a specific date.

        This method generates all possible time slots based on the doctor's
        schedule and checks availability against existing appointments.

        Args:
            doctor: The doctor User object
            date: The date to check for available slots

        Returns:
            List of available slots with structure:
            [
                {
                    'time': time object,
                    'duration': int (minutes),
                    'available_spots': int
                },
                ...
            ]

        Example:
            >>> from datetime import date
            >>> from django.contrib.auth.models import User
            >>> doctor = User.objects.get(profile__role='doctor', pk=1)
            >>> slots = AppointmentScheduler.get_available_slots(doctor, date(2025, 11, 20))
            >>> print(slots)
            [{'time': time(9, 0), 'duration': 30, 'available_spots': 1}, ...]
        """
        day_of_week = date.weekday()

        # Check if doctor is on leave
        is_on_leave = DoctorLeave.objects.filter(
            doctor=doctor,
            start_date__lte=date,
            end_date__gte=date,
            is_approved=True
        ).exists()

        if is_on_leave:
            logger.info(f"Doctor {doctor.get_full_name()} is on leave on {date}")
            return []

        # Get doctor's schedule for this day
        schedules = DoctorSchedule.objects.filter(
            doctor=doctor,
            day_of_week=day_of_week,
            is_active=True
        )

        if not schedules.exists():
            logger.info(f"No schedule found for {doctor.get_full_name()} on {date.strftime('%A')}")
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

        logger.info(f"Found {len(available_slots)} available slots for {doctor.get_full_name()} on {date}")
        return available_slots

    @staticmethod
    def book_appointment(patient, doctor, appointment_date, appointment_time, **kwargs) -> Appointment:
        """
        Book an appointment for a patient with a doctor.

        This method creates an appointment, schedules reminders,
        and sends a confirmation notification.

        Args:
            patient: The Patient object
            doctor: The doctor User object
            appointment_date: The date of the appointment
            appointment_time: The time of the appointment
            **kwargs: Additional appointment fields (reason, duration, etc.)

        Returns:
            The created Appointment object

        Raises:
            ValueError: If the slot is not available

        Example:
            >>> from datetime import date, time
            >>> appointment = AppointmentScheduler.book_appointment(
            ...     patient=patient_obj,
            ...     doctor=doctor_obj,
            ...     appointment_date=date(2025, 11, 20),
            ...     appointment_time=time(9, 0),
            ...     reason="COVID-19 test results discussion",
            ...     appointment_type="results_discussion",
            ...     duration=30
            ... )
        """
        # Verify slot is available
        available_slots = AppointmentScheduler.get_available_slots(doctor, appointment_date)
        slot_available = any(slot['time'] == appointment_time for slot in available_slots)

        if not slot_available:
            logger.warning(f"Attempted to book unavailable slot: {appointment_date} {appointment_time}")
            raise ValueError("This time slot is not available")

        # Create appointment
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            **kwargs
        )

        logger.info(f"Created appointment {appointment.appointment_id} for {patient.user.get_full_name()}")

        # Schedule reminders
        AppointmentScheduler.schedule_reminders(appointment)

        # Send confirmation notification
        try:
            from notifications.services import NotificationService
            NotificationService.send_notification(
                user=patient.user,
                template_type='appointment_confirmed',
                context_data={
                    'patient_name': patient.user.get_full_name(),
                    'doctor_name': doctor.get_full_name(),
                    'date': appointment_date.strftime('%B %d, %Y'),
                    'time': appointment_time.strftime('%I:%M %p'),
                    'appointment_type': appointment.get_appointment_type_display(),
                    'reason': appointment.reason,
                },
                priority='normal'
            )
            appointment.confirmation_sent = True
            appointment.save(update_fields=['confirmation_sent'])
            logger.info(f"Sent confirmation for appointment {appointment.appointment_id}")
        except Exception as e:
            logger.error(f"Failed to send confirmation for appointment {appointment.appointment_id}: {e}")

        return appointment

    @staticmethod
    def schedule_reminders(appointment: Appointment) -> None:
        """
        Schedule appointment reminders.

        Creates reminder records for 24 hours and 2 hours before
        the appointment if the appointment is far enough in the future.

        Args:
            appointment: The Appointment object to schedule reminders for
        """
        appointment_datetime = timezone.make_aware(
            datetime.combine(
                appointment.appointment_date,
                appointment.appointment_time
            )
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
            logger.info(f"Scheduled 24h reminder for appointment {appointment.appointment_id}")

        # 2 hours before
        reminder_2h = appointment_datetime - timedelta(hours=2)
        if reminder_2h > timezone.now():
            AppointmentReminder.objects.create(
                appointment=appointment,
                reminder_type='2h',
                scheduled_for=reminder_2h,
                channel='sms'
            )
            logger.info(f"Scheduled 2h reminder for appointment {appointment.appointment_id}")

    @staticmethod
    def send_due_reminders() -> int:
        """
        Send all due reminders.

        This method should be called periodically (e.g., via Celery task)
        to send reminders that are due.

        Returns:
            Number of reminders sent

        Example:
            This would typically be called from a Celery periodic task:
            >>> @periodic_task(run_every=timedelta(minutes=5))
            >>> def send_appointment_reminders():
            ...     count = AppointmentScheduler.send_due_reminders()
            ...     logger.info(f"Sent {count} appointment reminders")
        """
        due_reminders = AppointmentReminder.objects.filter(
            sent=False,
            scheduled_for__lte=timezone.now()
        ).select_related('appointment', 'appointment__patient', 'appointment__doctor')

        sent_count = 0

        for reminder in due_reminders:
            try:
                from notifications.services import NotificationService
                NotificationService.send_notification(
                    user=reminder.appointment.patient.user,
                    template_type='appointment_reminder',
                    context_data={
                        'patient_name': reminder.appointment.patient.user.get_full_name(),
                        'doctor_name': reminder.appointment.doctor.get_full_name(),
                        'date': reminder.appointment.appointment_date.strftime('%B %d, %Y'),
                        'time': reminder.appointment.appointment_time.strftime('%I:%M %p'),
                        'appointment_type': reminder.appointment.get_appointment_type_display(),
                        'reminder_type': reminder.get_reminder_type_display(),
                    },
                    priority='high'
                )

                reminder.sent = True
                reminder.sent_at = timezone.now()
                reminder.save(update_fields=['sent', 'sent_at'])
                sent_count += 1

                logger.info(f"Sent reminder for appointment {reminder.appointment.appointment_id}")

            except Exception as e:
                logger.error(f"Failed to send reminder {reminder.id}: {e}")

        if sent_count > 0:
            logger.info(f"Sent {sent_count} appointment reminders")

        return sent_count

    @staticmethod
    def cancel_appointment(appointment: Appointment, cancelled_by: str, reason: str = "") -> None:
        """
        Cancel an appointment.

        Args:
            appointment: The Appointment object to cancel
            cancelled_by: 'patient' or 'doctor'
            reason: Reason for cancellation

        Example:
            >>> AppointmentScheduler.cancel_appointment(
            ...     appointment=appointment_obj,
            ...     cancelled_by='patient',
            ...     reason='Unable to attend due to emergency'
            ... )
        """
        if cancelled_by == 'patient':
            appointment.status = 'cancelled_patient'
        elif cancelled_by == 'doctor':
            appointment.status = 'cancelled_doctor'
        else:
            raise ValueError("cancelled_by must be 'patient' or 'doctor'")

        appointment.cancelled_at = timezone.now()
        appointment.cancellation_reason = reason
        appointment.save(update_fields=['status', 'cancelled_at', 'cancellation_reason'])

        logger.info(f"Cancelled appointment {appointment.appointment_id} by {cancelled_by}")

        # Notify the other party
        try:
            from notifications.services import NotificationService
            if cancelled_by == 'patient':
                notify_user = appointment.doctor
            else:
                notify_user = appointment.patient.user

            NotificationService.send_notification(
                user=notify_user,
                template_type='appointment_cancelled',
                context_data={
                    'patient_name': appointment.patient.user.get_full_name(),
                    'doctor_name': appointment.doctor.get_full_name(),
                    'date': appointment.appointment_date.strftime('%B %d, %Y'),
                    'time': appointment.appointment_time.strftime('%I:%M %p'),
                    'cancelled_by': cancelled_by,
                    'reason': reason,
                },
                priority='high'
            )
            logger.info(f"Sent cancellation notification for appointment {appointment.appointment_id}")
        except Exception as e:
            logger.error(f"Failed to send cancellation notification: {e}")

    @staticmethod
    def complete_appointment(appointment: Appointment, doctor_notes: str = "") -> None:
        """
        Mark an appointment as completed.

        Args:
            appointment: The Appointment object to complete
            doctor_notes: Doctor's notes from the appointment

        Example:
            >>> AppointmentScheduler.complete_appointment(
            ...     appointment=appointment_obj,
            ...     doctor_notes="Patient responded well to treatment. Schedule follow-up in 2 weeks."
            ... )
        """
        appointment.status = 'completed'
        appointment.completed_at = timezone.now()
        appointment.doctor_notes = doctor_notes
        appointment.save(update_fields=['status', 'completed_at', 'doctor_notes'])

        logger.info(f"Completed appointment {appointment.appointment_id}")
