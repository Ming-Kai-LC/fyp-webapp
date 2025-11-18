"""
Appointment & Scheduling Module - Forms

This module contains forms for appointment booking, scheduling,
and management with Bootstrap 5 styling.

Forms:
    - AppointmentBookingForm: Form for booking new appointments
    - DoctorScheduleForm: Form for managing doctor schedules
    - AppointmentCancellationForm: Form for cancelling appointments
    - AppointmentCompletionForm: Form for completing appointments
    - WaitlistForm: Form for joining waitlist
"""

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import date, time, datetime

from .models import Appointment, DoctorSchedule, Waitlist, DoctorLeave
from detection.models import Patient

User = get_user_model()


class AppointmentBookingForm(forms.ModelForm):
    """
    Form for booking new appointments.

    Provides Bootstrap-styled form fields for patients or staff
    to book appointments with doctors.
    """
    doctor = forms.ModelChoiceField(
        queryset=User.objects.filter(profile__role='doctor', is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True,
        }),
        help_text="Select the doctor you want to see"
    )

    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'required': True,
        }),
        help_text="Select your preferred appointment date"
    )

    appointment_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time',
            'required': True,
        }),
        help_text="Select your preferred appointment time"
    )

    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'appointment_time', 'appointment_type', 'reason', 'notes', 'duration']
        widgets = {
            'appointment_type': forms.Select(attrs={
                'class': 'form-select',
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Please describe the reason for your visit',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Any additional notes or information (optional)',
            }),
            'duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 15,
                'max': 120,
                'step': 15,
                'value': 30,
            }),
        }
        help_texts = {
            'appointment_type': 'Select the type of appointment',
            'reason': 'Briefly describe the reason for your visit',
            'notes': 'Optional: Any additional information the doctor should know',
            'duration': 'Expected duration in minutes',
        }

    def clean_appointment_date(self):
        """Validate that appointment date is not in the past."""
        appointment_date = self.cleaned_data.get('appointment_date')
        if appointment_date and appointment_date < date.today():
            raise ValidationError("Appointment date cannot be in the past.")
        return appointment_date

    def clean(self):
        """Validate that the selected time slot is available."""
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        appointment_date = cleaned_data.get('appointment_date')
        appointment_time = cleaned_data.get('appointment_time')

        if doctor and appointment_date and appointment_time:
            # Check if slot is available
            from .services import AppointmentScheduler
            available_slots = AppointmentScheduler.get_available_slots(doctor, appointment_date)

            if not any(slot['time'] == appointment_time for slot in available_slots):
                raise ValidationError(
                    "This time slot is not available. Please select a different time."
                )

        return cleaned_data


class DoctorScheduleForm(forms.ModelForm):
    """
    Form for managing doctor schedules.

    Allows doctors or admins to set up weekly working hours
    and appointment slot configurations.
    """
    class Meta:
        model = DoctorSchedule
        fields = ['day_of_week', 'start_time', 'end_time', 'slot_duration', 'max_appointments_per_slot', 'is_active']
        widgets = {
            'day_of_week': forms.Select(attrs={
                'class': 'form-select',
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
            }),
            'slot_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 15,
                'max': 120,
                'step': 15,
            }),
            'max_appointments_per_slot': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10,
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        help_texts = {
            'day_of_week': 'Select the day of the week',
            'start_time': 'Schedule start time',
            'end_time': 'Schedule end time',
            'slot_duration': 'Duration of each appointment slot in minutes',
            'max_appointments_per_slot': 'Maximum number of appointments per time slot',
            'is_active': 'Check to activate this schedule',
        }

    def clean(self):
        """Validate that end time is after start time."""
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time:
            if end_time <= start_time:
                raise ValidationError("End time must be after start time.")

        return cleaned_data


class AppointmentCancellationForm(forms.Form):
    """
    Form for cancelling appointments.

    Collects cancellation reason from the user.
    """
    cancellation_reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Please provide a reason for cancellation',
            'required': True,
        }),
        help_text='Please explain why you need to cancel this appointment'
    )


class AppointmentCompletionForm(forms.Form):
    """
    Form for completing appointments (doctor use).

    Collects doctor's notes after completing an appointment.
    """
    doctor_notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Enter your notes about this appointment, diagnosis, treatment, etc.',
            'required': True,
        }),
        help_text='Document the appointment details, diagnosis, and treatment plan'
    )

    create_follow_up = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
        help_text='Check if patient needs a follow-up appointment'
    )


class WaitlistForm(forms.ModelForm):
    """
    Form for joining waitlist when slots are full.

    Allows patients to request notification when slots become available.
    """
    doctor = forms.ModelChoiceField(
        queryset=User.objects.filter(profile__role='doctor', is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True,
        }),
        help_text="Select the doctor you want to see"
    )

    preferred_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'required': True,
        }),
        help_text="Select your preferred appointment date"
    )

    preferred_time_start = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time',
            'required': True,
        }),
        help_text="Earliest time you're available"
    )

    preferred_time_end = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time',
            'required': True,
        }),
        help_text="Latest time you're available"
    )

    class Meta:
        model = Waitlist
        fields = ['doctor', 'preferred_date', 'preferred_time_start', 'preferred_time_end', 'appointment_type', 'reason']
        widgets = {
            'appointment_type': forms.Select(attrs={
                'class': 'form-select',
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Please describe the reason for your visit',
            }),
        }
        help_texts = {
            'appointment_type': 'Select the type of appointment',
            'reason': 'Briefly describe the reason for your visit',
        }

    def clean_preferred_date(self):
        """Validate that preferred date is not in the past."""
        preferred_date = self.cleaned_data.get('preferred_date')
        if preferred_date and preferred_date < date.today():
            raise ValidationError("Preferred date cannot be in the past.")
        return preferred_date

    def clean(self):
        """Validate that end time is after start time."""
        cleaned_data = super().clean()
        start_time = cleaned_data.get('preferred_time_start')
        end_time = cleaned_data.get('preferred_time_end')

        if start_time and end_time:
            if end_time <= start_time:
                raise ValidationError("End time must be after start time.")

        return cleaned_data


class DoctorLeaveForm(forms.ModelForm):
    """
    Form for doctors to request leave/time off.

    Allows doctors to block out dates when they're unavailable.
    """
    class Meta:
        model = DoctorLeave
        fields = ['start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'reason': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Reason for leave (optional)',
            }),
        }
        help_texts = {
            'start_date': 'First day of leave',
            'end_date': 'Last day of leave',
            'reason': 'Optional reason for leave',
        }

    def clean(self):
        """Validate that end date is after start date."""
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if end_date < start_date:
                raise ValidationError("End date must be after or equal to start date.")

        return cleaned_data
