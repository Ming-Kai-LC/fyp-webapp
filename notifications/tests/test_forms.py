"""
Tests for notification forms
"""
from django.test import TestCase
from django.contrib.auth.models import User
from datetime import time

from notifications.forms import NotificationPreferenceForm
from notifications.models import NotificationPreference


class NotificationPreferenceFormTests(TestCase):
    """Test NotificationPreferenceForm"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.preferences = NotificationPreference.objects.create(
            user=self.user
        )

    def test_form_fields(self):
        """Test that form has all required fields"""
        form = NotificationPreferenceForm()
        expected_fields = [
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
        for field in expected_fields:
            self.assertIn(field, form.fields)

    def test_form_valid_data(self):
        """Test form with valid data"""
        data = {
            'email_enabled': True,
            'sms_enabled': False,
            'in_app_enabled': True,
            'prediction_results': True,
            'appointment_reminders': True,
            'report_ready': True,
            'doctor_notes': True,
            'system_updates': False,
            'email_address': 'test@example.com',
            'phone_number': '+1234567890',
            'quiet_hours_start': '22:00',
            'quiet_hours_end': '07:00',
            'daily_digest': False
        }
        form = NotificationPreferenceForm(data=data, instance=self.preferences)
        self.assertTrue(form.is_valid())

    def test_form_save(self):
        """Test that form saves correctly"""
        data = {
            'email_enabled': True,
            'sms_enabled': True,
            'in_app_enabled': True,
            'prediction_results': True,
            'appointment_reminders': False,
            'report_ready': True,
            'doctor_notes': True,
            'system_updates': False,
            'email_address': 'new@example.com',
            'phone_number': '+9876543210',
            'quiet_hours_start': '23:00',
            'quiet_hours_end': '08:00',
            'daily_digest': True
        }
        form = NotificationPreferenceForm(data=data, instance=self.preferences)
        self.assertTrue(form.is_valid())

        saved_prefs = form.save()
        self.assertEqual(saved_prefs.email_address, 'new@example.com')
        self.assertEqual(saved_prefs.phone_number, '+9876543210')
        self.assertTrue(saved_prefs.sms_enabled)
        self.assertFalse(saved_prefs.appointment_reminders)
        self.assertTrue(saved_prefs.daily_digest)

    def test_form_email_validation(self):
        """Test email field validation"""
        data = {
            'email_enabled': True,
            'sms_enabled': False,
            'in_app_enabled': True,
            'prediction_results': True,
            'appointment_reminders': True,
            'report_ready': True,
            'doctor_notes': True,
            'system_updates': False,
            'email_address': 'invalid-email',  # Invalid email
            'phone_number': '',
            'daily_digest': False
        }
        form = NotificationPreferenceForm(data=data, instance=self.preferences)
        self.assertFalse(form.is_valid())
        self.assertIn('email_address', form.errors)

    def test_form_widgets(self):
        """Test that form has proper widgets"""
        form = NotificationPreferenceForm()

        # Check that checkboxes have proper class
        self.assertIn('form-check-input',
                      form.fields['email_enabled'].widget.attrs['class'])
        self.assertIn('form-check-input',
                      form.fields['daily_digest'].widget.attrs['class'])

        # Check that text inputs have form-control class
        self.assertIn('form-control',
                      form.fields['email_address'].widget.attrs['class'])
        self.assertIn('form-control',
                      form.fields['phone_number'].widget.attrs['class'])

    def test_form_time_fields(self):
        """Test time field widgets"""
        form = NotificationPreferenceForm()

        # Check time fields have proper type
        self.assertEqual(
            form.fields['quiet_hours_start'].widget.attrs['type'],
            'time'
        )
        self.assertEqual(
            form.fields['quiet_hours_end'].widget.attrs['type'],
            'time'
        )

    def test_form_optional_fields(self):
        """Test that optional fields can be blank"""
        data = {
            'email_enabled': True,
            'sms_enabled': False,
            'in_app_enabled': True,
            'prediction_results': True,
            'appointment_reminders': True,
            'report_ready': True,
            'doctor_notes': True,
            'system_updates': False,
            'email_address': '',  # Optional
            'phone_number': '',  # Optional
            'daily_digest': False
        }
        form = NotificationPreferenceForm(data=data, instance=self.preferences)
        self.assertTrue(form.is_valid())

    def test_form_initial_data(self):
        """Test form loads initial data from instance"""
        self.preferences.email_address = 'initial@example.com'
        self.preferences.sms_enabled = True
        self.preferences.daily_digest = True
        self.preferences.save()

        form = NotificationPreferenceForm(instance=self.preferences)
        self.assertEqual(form.initial['email_address'], 'initial@example.com')
        self.assertTrue(form.initial['sms_enabled'])
        self.assertTrue(form.initial['daily_digest'])

    def test_form_help_text(self):
        """Test that form has help text"""
        form = NotificationPreferenceForm()
        self.assertIsNotNone(form.fields['quiet_hours_start'].help_text)
        self.assertIsNotNone(form.fields['quiet_hours_end'].help_text)
        self.assertIsNotNone(form.fields['daily_digest'].help_text)

    def test_form_placeholder_text(self):
        """Test that form has placeholders"""
        form = NotificationPreferenceForm()
        self.assertIn('placeholder',
                      form.fields['email_address'].widget.attrs)
        self.assertIn('placeholder',
                      form.fields['phone_number'].widget.attrs)
