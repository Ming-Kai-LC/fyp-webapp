"""
Appointment & Scheduling Module - Views

This module contains all views for appointment booking, scheduling,
and management functionality.

Views:
    - book_appointment: Book a new appointment
    - get_available_slots_api: API endpoint for available slots
    - my_appointments: List user's appointments
    - appointment_detail: View appointment details
    - cancel_appointment: Cancel an appointment
    - reschedule_appointment: Reschedule an appointment
    - complete_appointment: Mark appointment as complete (doctor only)
    - manage_schedule: Manage doctor's schedule
    - doctor_appointments: List doctor's appointments
    - join_waitlist: Join waitlist for full slots
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta, date

from .models import Appointment, DoctorSchedule, Waitlist, DoctorLeave
from .forms import (
    AppointmentBookingForm,
    DoctorScheduleForm,
    AppointmentCancellationForm,
    AppointmentCompletionForm,
    WaitlistForm,
    DoctorLeaveForm,
)
from .services import AppointmentScheduler
from detection.models import Patient

import logging

logger = logging.getLogger(__name__)


def role_required(role):
    """Decorator to require specific user role."""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "Please login to access this page.")
                return redirect('login')

            user_role = getattr(request.user.profile, 'role', None)
            if user_role != role:
                messages.error(request, f"Access denied. This page is for {role}s only.")
                return redirect('home')

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


@login_required
def book_appointment(request):
    """
    Book a new appointment.

    Available to: Patients and staff
    Method: GET (show form), POST (process booking)
    """
    # Get or create patient profile for current user
    try:
        if hasattr(request.user, 'patient_profile'):
            patient = request.user.patient_profile
        else:
            # If user doesn't have patient profile, redirect to create one
            messages.warning(request, "Please complete your patient profile first.")
            return redirect('detection:patient_dashboard')
    except Patient.DoesNotExist:
        messages.error(request, "Patient profile not found. Please contact support.")
        return redirect('home')

    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            try:
                appointment = AppointmentScheduler.book_appointment(
                    patient=patient,
                    doctor=form.cleaned_data['doctor'],
                    appointment_date=form.cleaned_data['appointment_date'],
                    appointment_time=form.cleaned_data['appointment_time'],
                    appointment_type=form.cleaned_data['appointment_type'],
                    reason=form.cleaned_data['reason'],
                    notes=form.cleaned_data.get('notes', ''),
                    duration=form.cleaned_data['duration'],
                    booked_by=request.user,
                )

                messages.success(
                    request,
                    f"Appointment booked successfully! Your appointment is on "
                    f"{appointment.appointment_date.strftime('%B %d, %Y')} at "
                    f"{appointment.appointment_time.strftime('%I:%M %p')}."
                )
                logger.info(f"User {request.user.username} booked appointment {appointment.appointment_id}")
                return redirect('appointments:appointment_detail', appointment_id=appointment.appointment_id)

            except ValueError as e:
                messages.error(request, str(e))
                logger.warning(f"Failed to book appointment: {e}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AppointmentBookingForm()

    context = {
        'form': form,
        'page_title': 'Book Appointment',
    }
    return render(request, 'appointments/pages/book_appointment.html', context)


@login_required
@require_GET
def get_available_slots_api(request):
    """
    API endpoint to get available appointment slots for a doctor on a specific date.

    Query parameters:
        - doctor_id: ID of the doctor
        - date: Date in YYYY-MM-DD format

    Returns:
        JSON response with available slots
    """
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')

    if not doctor_id or not date_str:
        return JsonResponse({'error': 'doctor_id and date are required'}, status=400)

    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        doctor = User.objects.get(id=doctor_id, profile__role='doctor')
        appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        slots = AppointmentScheduler.get_available_slots(doctor, appointment_date)

        # Convert time objects to strings
        slots_data = [
            {
                'time': slot['time'].strftime('%H:%M'),
                'time_display': slot['time'].strftime('%I:%M %p'),
                'duration': slot['duration'],
                'available_spots': slot['available_spots'],
            }
            for slot in slots
        ]

        return JsonResponse({'slots': slots_data})

    except User.DoesNotExist:
        return JsonResponse({'error': 'Doctor not found'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
    except Exception as e:
        logger.error(f"Error fetching available slots: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


@login_required
def my_appointments(request):
    """
    List current user's appointments.

    Available to: All authenticated users
    Shows: Upcoming and past appointments
    """
    user = request.user
    user_role = getattr(user.profile, 'role', 'patient')

    # Get appointments based on role
    if user_role == 'doctor':
        appointments = Appointment.objects.filter(doctor=user)
    else:
        # Patient
        try:
            patient = user.patient_profile
            appointments = Appointment.objects.filter(patient=patient)
        except Patient.DoesNotExist:
            messages.warning(request, "Please complete your patient profile first.")
            return redirect('detection:patient_dashboard')

    # Filter by status
    status_filter = request.GET.get('status', 'all')
    if status_filter != 'all':
        appointments = appointments.filter(status=status_filter)

    # Separate upcoming and past appointments
    today = date.today()
    upcoming = appointments.filter(
        appointment_date__gte=today
    ).order_by('appointment_date', 'appointment_time')

    past = appointments.filter(
        appointment_date__lt=today
    ).order_by('-appointment_date', '-appointment_time')

    # Pagination
    upcoming_paginator = Paginator(upcoming, 10)
    past_paginator = Paginator(past, 10)

    upcoming_page = request.GET.get('upcoming_page', 1)
    past_page = request.GET.get('past_page', 1)

    upcoming_appointments = upcoming_paginator.get_page(upcoming_page)
    past_appointments = past_paginator.get_page(past_page)

    context = {
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
        'status_filter': status_filter,
        'page_title': 'My Appointments',
        'user_role': user_role,
    }
    return render(request, 'appointments/pages/my_appointments.html', context)


@login_required
def appointment_detail(request, appointment_id):
    """
    View detailed information about a specific appointment.

    Available to: Appointment participants (patient, doctor) and staff
    """
    appointment = get_object_or_404(Appointment, appointment_id=appointment_id)

    # Check authorization
    user_role = getattr(request.user.profile, 'role', 'patient')
    if user_role == 'doctor':
        if appointment.doctor != request.user:
            messages.error(request, "You don't have permission to view this appointment.")
            return redirect('appointments:my_appointments')
    else:
        if appointment.patient.user != request.user:
            messages.error(request, "You don't have permission to view this appointment.")
            return redirect('appointments:my_appointments')

    context = {
        'appointment': appointment,
        'page_title': 'Appointment Details',
        'user_role': user_role,
    }
    return render(request, 'appointments/pages/appointment_detail.html', context)


@login_required
@require_POST
def cancel_appointment(request, appointment_id):
    """
    Cancel an appointment.

    Available to: Appointment participants (patient, doctor)
    Method: POST
    """
    appointment = get_object_or_404(Appointment, appointment_id=appointment_id)

    # Check authorization and determine who is cancelling
    user_role = getattr(request.user.profile, 'role', 'patient')
    if user_role == 'doctor':
        if appointment.doctor != request.user:
            messages.error(request, "You don't have permission to cancel this appointment.")
            return redirect('appointments:my_appointments')
        cancelled_by = 'doctor'
    else:
        if appointment.patient.user != request.user:
            messages.error(request, "You don't have permission to cancel this appointment.")
            return redirect('appointments:my_appointments')
        cancelled_by = 'patient'

    # Check if appointment can be cancelled
    if appointment.status in ['completed', 'cancelled_patient', 'cancelled_doctor']:
        messages.error(request, "This appointment cannot be cancelled.")
        return redirect('appointments:appointment_detail', appointment_id=appointment_id)

    form = AppointmentCancellationForm(request.POST)
    if form.is_valid():
        AppointmentScheduler.cancel_appointment(
            appointment=appointment,
            cancelled_by=cancelled_by,
            reason=form.cleaned_data['cancellation_reason']
        )
        messages.success(request, "Appointment cancelled successfully.")
        logger.info(f"Appointment {appointment_id} cancelled by {cancelled_by}")
    else:
        messages.error(request, "Please provide a cancellation reason.")

    return redirect('appointments:my_appointments')


@login_required
def reschedule_appointment(request, appointment_id):
    """
    Reschedule an appointment.

    Available to: Appointment participants (patient, doctor)
    Method: GET (show form), POST (process reschedule)
    """
    appointment = get_object_or_404(Appointment, appointment_id=appointment_id)

    # Check authorization
    user_role = getattr(request.user.profile, 'role', 'patient')
    if user_role == 'doctor':
        if appointment.doctor != request.user:
            messages.error(request, "You don't have permission to reschedule this appointment.")
            return redirect('appointments:my_appointments')
    else:
        if appointment.patient.user != request.user:
            messages.error(request, "You don't have permission to reschedule this appointment.")
            return redirect('appointments:my_appointments')

    # Check if appointment can be rescheduled
    if appointment.status in ['completed', 'cancelled_patient', 'cancelled_doctor']:
        messages.error(request, "This appointment cannot be rescheduled.")
        return redirect('appointments:appointment_detail', appointment_id=appointment_id)

    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST)
        if form.is_valid():
            try:
                # Mark old appointment as rescheduled
                appointment.status = 'rescheduled'
                appointment.save(update_fields=['status'])

                # Create new appointment
                new_appointment = AppointmentScheduler.book_appointment(
                    patient=appointment.patient,
                    doctor=form.cleaned_data['doctor'],
                    appointment_date=form.cleaned_data['appointment_date'],
                    appointment_time=form.cleaned_data['appointment_time'],
                    appointment_type=form.cleaned_data['appointment_type'],
                    reason=form.cleaned_data['reason'],
                    notes=form.cleaned_data.get('notes', ''),
                    duration=form.cleaned_data['duration'],
                    booked_by=request.user,
                )

                messages.success(
                    request,
                    f"Appointment rescheduled successfully! Your new appointment is on "
                    f"{new_appointment.appointment_date.strftime('%B %d, %Y')} at "
                    f"{new_appointment.appointment_time.strftime('%I:%M %p')}."
                )
                logger.info(f"Appointment {appointment_id} rescheduled to {new_appointment.appointment_id}")
                return redirect('appointments:appointment_detail', appointment_id=new_appointment.appointment_id)

            except ValueError as e:
                messages.error(request, str(e))
                logger.warning(f"Failed to reschedule appointment: {e}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        # Pre-fill form with existing appointment data
        initial_data = {
            'doctor': appointment.doctor,
            'appointment_date': appointment.appointment_date,
            'appointment_time': appointment.appointment_time,
            'appointment_type': appointment.appointment_type,
            'reason': appointment.reason,
            'notes': appointment.notes,
            'duration': appointment.duration,
        }
        form = AppointmentBookingForm(initial=initial_data)

    context = {
        'form': form,
        'appointment': appointment,
        'page_title': 'Reschedule Appointment',
    }
    return render(request, 'appointments/pages/reschedule_appointment.html', context)


@login_required
@require_POST
def complete_appointment(request, appointment_id):
    """
    Mark an appointment as completed (doctor only).

    Available to: Doctors
    Method: POST
    """
    appointment = get_object_or_404(Appointment, appointment_id=appointment_id)

    # Check authorization
    if appointment.doctor != request.user:
        messages.error(request, "You don't have permission to complete this appointment.")
        return redirect('appointments:my_appointments')

    # Check if appointment can be completed
    if appointment.status == 'completed':
        messages.info(request, "This appointment is already marked as completed.")
        return redirect('appointments:appointment_detail', appointment_id=appointment_id)

    form = AppointmentCompletionForm(request.POST)
    if form.is_valid():
        AppointmentScheduler.complete_appointment(
            appointment=appointment,
            doctor_notes=form.cleaned_data['doctor_notes']
        )
        messages.success(request, "Appointment marked as completed.")
        logger.info(f"Appointment {appointment_id} completed by doctor {request.user.username}")
    else:
        messages.error(request, "Please provide appointment notes.")

    return redirect('appointments:appointment_detail', appointment_id=appointment_id)


@login_required
def manage_schedule(request):
    """
    Manage doctor's schedule (doctor only).

    Available to: Doctors
    Shows: Current schedule, allows adding/editing/deleting schedule entries
    """
    # Check if user is a doctor
    user_role = getattr(request.user.profile, 'role', None)
    if user_role != 'doctor':
        messages.error(request, "Access denied. This page is for doctors only.")
        return redirect('home')

    if request.method == 'POST':
        form = DoctorScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.doctor = request.user
            schedule.save()
            messages.success(request, "Schedule added successfully.")
            logger.info(f"Doctor {request.user.username} added schedule for {schedule.get_day_of_week_display()}")
            return redirect('appointments:manage_schedule')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DoctorScheduleForm()

    # Get doctor's current schedules
    schedules = DoctorSchedule.objects.filter(doctor=request.user).order_by('day_of_week', 'start_time')

    context = {
        'form': form,
        'schedules': schedules,
        'page_title': 'Manage Schedule',
    }
    return render(request, 'appointments/pages/manage_schedule.html', context)


@login_required
def doctor_appointments(request):
    """
    List doctor's appointments (doctor only).

    Available to: Doctors
    Shows: Today's appointments, upcoming appointments, calendar view
    """
    # Check if user is a doctor
    user_role = getattr(request.user.profile, 'role', None)
    if user_role != 'doctor':
        messages.error(request, "Access denied. This page is for doctors only.")
        return redirect('home')

    today = date.today()

    # Get today's appointments
    todays_appointments = Appointment.objects.filter(
        doctor=request.user,
        appointment_date=today
    ).order_by('appointment_time')

    # Get upcoming appointments (next 7 days)
    next_week = today + timedelta(days=7)
    upcoming_appointments = Appointment.objects.filter(
        doctor=request.user,
        appointment_date__gt=today,
        appointment_date__lte=next_week
    ).order_by('appointment_date', 'appointment_time')

    # Get appointments by status for statistics
    scheduled_count = Appointment.objects.filter(
        doctor=request.user,
        status='scheduled',
        appointment_date__gte=today
    ).count()

    confirmed_count = Appointment.objects.filter(
        doctor=request.user,
        status='confirmed',
        appointment_date__gte=today
    ).count()

    context = {
        'todays_appointments': todays_appointments,
        'upcoming_appointments': upcoming_appointments,
        'scheduled_count': scheduled_count,
        'confirmed_count': confirmed_count,
        'page_title': 'My Appointments',
    }
    return render(request, 'appointments/pages/doctor_appointments.html', context)


@login_required
def join_waitlist(request):
    """
    Join waitlist for fully booked slots.

    Available to: Patients
    Method: GET (show form), POST (process join)
    """
    # Get or create patient profile for current user
    try:
        if hasattr(request.user, 'patient_profile'):
            patient = request.user.patient_profile
        else:
            messages.warning(request, "Please complete your patient profile first.")
            return redirect('detection:patient_dashboard')
    except Patient.DoesNotExist:
        messages.error(request, "Patient profile not found. Please contact support.")
        return redirect('home')

    if request.method == 'POST':
        form = WaitlistForm(request.POST)
        if form.is_valid():
            waitlist_entry = form.save(commit=False)
            waitlist_entry.patient = patient
            waitlist_entry.save()

            messages.success(
                request,
                "You've been added to the waitlist! We'll notify you when a slot becomes available."
            )
            logger.info(f"User {request.user.username} joined waitlist for doctor {waitlist_entry.doctor.username}")
            return redirect('appointments:my_appointments')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = WaitlistForm()

    context = {
        'form': form,
        'page_title': 'Join Waitlist',
    }
    return render(request, 'appointments/pages/join_waitlist.html', context)
