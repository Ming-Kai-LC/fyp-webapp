"""
Tests for notification models
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from notifications.models import (
    NotificationTemplate,
    Notification,
    NotificationPreference,
    NotificationLog
)


class NotificationTemplateTests(TestCase):
    """Test NotificationTemplate model"""

    def setUp(self):
        """Set up test data"""
        self.template = NotificationTemplate.objects.create(
            template_type='prediction_ready',
            channel='email',
            subject='Test Results Ready',
            body_template='Hello {patient_name}, your results are ready.',
            is_active=True,
            is_critical=False
        )

    def test_template_creation(self):
        """Test creating a notification template"""
        self.assertEqual(self.template.template_type, 'prediction_ready')
        self.assertEqual(self.template.channel, 'email')
        self.assertTrue(self.template.is_active)
        self.assertFalse(self.template.is_critical)

    def test_template_str(self):
        """Test string representation"""
        expected = "Prediction Ready - Email"
        self.assertEqual(str(self.template), expected)

    def test_unique_template_type(self):
        """Test that template_type is unique"""
        with self.assertRaises(Exception):
            NotificationTemplate.objects.create(
                template_type='prediction_ready',  # Duplicate
                channel='sms',
                subject='Test',
                body_template='Test body'
            )

    def test_template_timestamps(self):
        """Test that timestamps are set correctly"""
        self.assertIsNotNone(self.template.created_at)
        self.assertIsNotNone(self.template.updated_at)


class NotificationTests(TestCase):
    """Test Notification model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.template = NotificationTemplate.objects.create(
            template_type='prediction_ready',
            channel='in_app',
            subject='Results Ready',
            body_template='Your results are ready.'
        )
        self.notification = Notification.objects.create(
            recipient=self.user,
            template=self.template,
            title='Test Notification',
            message='This is a test notification',
            channel='in_app',
            status='sent',
            priority='normal'
        )

    def test_notification_creation(self):
        """Test creating a notification"""
        self.assertEqual(self.notification.recipient, self.user)
        self.assertEqual(self.notification.title, 'Test Notification')
        self.assertEqual(self.notification.status, 'sent')
        self.assertEqual(self.notification.priority, 'normal')

    def test_notification_uuid(self):
        """Test that notification has a UUID"""
        self.assertIsNotNone(self.notification.notification_id)
        # Check it's a valid UUID format
        self.assertEqual(len(str(self.notification.notification_id)), 36)

    def test_notification_str(self):
        """Test string representation"""
        expected = f"{self.user.username} - Test Notification (sent)"
        self.assertEqual(str(self.notification), expected)

    def test_mark_as_read(self):
        """Test marking notification as read"""
        self.assertIsNone(self.notification.read_at)
        self.notification.mark_as_read()
        self.assertEqual(self.notification.status, 'read')
        self.assertIsNotNone(self.notification.read_at)

    def test_notification_ordering(self):
        """Test that notifications are ordered by created_at descending"""
        notification2 = Notification.objects.create(
            recipient=self.user,
            title='Second Notification',
            message='Second message',
            channel='in_app'
        )
        notifications = Notification.objects.all()
        self.assertEqual(notifications[0], notification2)
        self.assertEqual(notifications[1], self.notification)


class NotificationPreferenceTests(TestCase):
    """Test NotificationPreference model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.preferences = NotificationPreference.objects.create(
            user=self.user,
            email_enabled=True,
            sms_enabled=False,
            in_app_enabled=True,
            email_address='custom@example.com',
            phone_number='+1234567890'
        )

    def test_preferences_creation(self):
        """Test creating notification preferences"""
        self.assertEqual(self.preferences.user, self.user)
        self.assertTrue(self.preferences.email_enabled)
        self.assertFalse(self.preferences.sms_enabled)
        self.assertTrue(self.preferences.in_app_enabled)

    def test_preferences_str(self):
        """Test string representation"""
        expected = f"{self.user.username} - Notification Preferences"
        self.assertEqual(str(self.preferences), expected)

    def test_default_preferences(self):
        """Test default preference values"""
        user2 = User.objects.create_user(username='user2', password='pass')
        prefs = NotificationPreference.objects.create(user=user2)
        self.assertTrue(prefs.email_enabled)
        self.assertFalse(prefs.sms_enabled)
        self.assertTrue(prefs.in_app_enabled)
        self.assertTrue(prefs.prediction_results)
        self.assertTrue(prefs.appointment_reminders)

    def test_quiet_hours(self):
        """Test quiet hours settings"""
        from datetime import time
        self.preferences.quiet_hours_start = time(22, 0)
        self.preferences.quiet_hours_end = time(7, 0)
        self.preferences.save()
        self.assertIsNotNone(self.preferences.quiet_hours_start)
        self.assertIsNotNone(self.preferences.quiet_hours_end)

    def test_one_to_one_relationship(self):
        """Test that each user can only have one preference object"""
        with self.assertRaises(Exception):
            NotificationPreference.objects.create(user=self.user)


class NotificationLogTests(TestCase):
    """Test NotificationLog model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.notification = Notification.objects.create(
            recipient=self.user,
            title='Test',
            message='Test message',
            channel='email'
        )
        self.log = NotificationLog.objects.create(
            notification=self.notification,
            success=True,
            channel='email',
            provider='smtp'
        )

    def test_log_creation(self):
        """Test creating a notification log"""
        self.assertEqual(self.log.notification, self.notification)
        self.assertTrue(self.log.success)
        self.assertEqual(self.log.channel, 'email')
        self.assertEqual(self.log.provider, 'smtp')

    def test_log_str(self):
        """Test string representation"""
        expected = "Test - Success via email"
        self.assertEqual(str(self.log), expected)

    def test_failed_log(self):
        """Test logging a failed delivery"""
        failed_log = NotificationLog.objects.create(
            notification=self.notification,
            success=False,
            channel='sms',
            error_details='Connection timeout'
        )
        self.assertFalse(failed_log.success)
        self.assertEqual(failed_log.error_details, 'Connection timeout')

    def test_log_ordering(self):
        """Test that logs are ordered by attempted_at descending"""
        log2 = NotificationLog.objects.create(
            notification=self.notification,
            success=True,
            channel='email'
        )
        logs = NotificationLog.objects.all()
        self.assertEqual(logs[0], log2)
        self.assertEqual(logs[1], self.log)

    def test_log_timestamp(self):
        """Test that attempted_at is set automatically"""
        self.assertIsNotNone(self.log.attempted_at)
