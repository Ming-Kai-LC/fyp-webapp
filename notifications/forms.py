from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Div, Row, Column
from .models import NotificationPreference


class NotificationPreferenceForm(forms.ModelForm):
    """
    Form for managing user notification preferences
    """
    class Meta:
        model = NotificationPreference
        fields = [
            'email_enabled', 'sms_enabled', 'in_app_enabled',
            'prediction_results', 'appointment_reminders', 'report_ready',
            'doctor_notes', 'system_updates',
            'email_address', 'phone_number',
            'quiet_hours_start', 'quiet_hours_end',
            'daily_digest'
        ]
        widgets = {
            'quiet_hours_start': forms.TimeInput(attrs={'type': 'time'}),
            'quiet_hours_end': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Notification Channels',
                Row(
                    Column('email_enabled', css_class='form-group col-md-4 mb-0'),
                    Column('sms_enabled', css_class='form-group col-md-4 mb-0'),
                    Column('in_app_enabled', css_class='form-group col-md-4 mb-0'),
                    css_class='form-row'
                ),
            ),
            Fieldset(
                'Notification Types',
                Row(
                    Column('prediction_results', css_class='form-group col-md-6 mb-0'),
                    Column('appointment_reminders', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('report_ready', css_class='form-group col-md-6 mb-0'),
                    Column('doctor_notes', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                'system_updates',
            ),
            Fieldset(
                'Contact Information',
                Row(
                    Column('email_address', css_class='form-group col-md-6 mb-0'),
                    Column('phone_number', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
            ),
            Fieldset(
                'Quiet Hours',
                Row(
                    Column('quiet_hours_start', css_class='form-group col-md-6 mb-0'),
                    Column('quiet_hours_end', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                Div(
                    '<small class="form-text text-muted">Non-critical notifications will not be sent during quiet hours.</small>',
                    css_class='form-group'
                ),
            ),
            Fieldset(
                'Digest Options',
                'daily_digest',
                Div(
                    '<small class="form-text text-muted">Receive a daily summary instead of individual notifications.</small>',
                    css_class='form-group'
                ),
            ),
            Submit('submit', 'Save Preferences', css_class='btn btn-primary')
        )
