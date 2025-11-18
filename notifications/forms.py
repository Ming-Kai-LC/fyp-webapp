from django import forms
from .models import NotificationPreference


class NotificationPreferenceForm(forms.ModelForm):
    """
    Form for managing user notification preferences
    """
    class Meta:
        model = NotificationPreference
        fields = [
            'email_enabled',
            'sms_enabled',
            'in_app_enabled',
            'prediction_results',
            'appointment_reminders',
            'report_ready',
            'doctor_notes',
            'system_updates',
            'email_address',
            'phone_number',
            'quiet_hours_start',
            'quiet_hours_end',
            'daily_digest',
        ]
        widgets = {
            'email_address': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890'
            }),
            'quiet_hours_start': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'quiet_hours_end': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'email_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'sms_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'in_app_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'prediction_results': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'appointment_reminders': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'report_ready': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'doctor_notes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'system_updates': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'daily_digest': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'quiet_hours_start': 'Start time for quiet hours (notifications paused)',
            'quiet_hours_end': 'End time for quiet hours',
            'daily_digest': 'Receive a daily summary instead of individual notifications',
        }
