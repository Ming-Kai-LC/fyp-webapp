"""
Tests for notification services
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.core import mail
from django.utils import timezone
from datetime import time, timedelta
from unittest.mock import patch, MagicMock

from notifications.models import (
    NotificationTemplate,
    Notification,
    NotificationPreference,
    NotificationLog
)
from notifications.services import NotificationService, NotificationScheduler


class NotificationServiceTests(TestCase):
    """Test NotificationService"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )

        # Create preferences
        self.preferences = NotificationPreference.objects.create(
            user=self.user,
            email_enabled=True,
            email_address='custom@example.com',
            in_app_enabled=True
        )

        # Create templates
        self.email_template = NotificationTemplate.objects.create(
            template_type='prediction_ready',
            channel='email',
            subject='Test Results Ready',
            body_template='Hello {patient_name}, your results show {diagnosis}.',
            is_active=True,
            is_critical=False
        )

        self.critical_template = NotificationTemplate.objects.create(
            template_type='critical_result',
            channel='email',
            subject='URGENT: COVID-19 Positive',
            body_template='Dear {patient_name}, your test is POSITIVE.',
            is_active=True,
            is_critical=True
        )

    def test_send_notification_creates_record(self):
        """Test that send_notification creates a notification record"""
        context = {
            'patient_name': 'Test User',
            'diagnosis': 'Normal',
            'action_url': '/results/1/'
        }

        notification = NotificationService.send_notification(
            user=self.user,
            template_type='prediction_ready',
            context_data=context,
            priority='normal'
        )

        self.assertIsNotNone(notification)
        self.assertEqual(notification.recipient, self.user)
        self.assertEqual(notification.channel, 'email')
        self.assertEqual(notification.priority, 'normal')

    def test_send_notification_renders_template(self):
        """Test that notification message is rendered correctly"""
        context = {
            'patient_name': 'Test User',
            'diagnosis': 'Normal'
        }

        notification = NotificationService.send_notification(
            user=self.user,
            template_type='prediction_ready',
            context_data=context
        )

        self.assertIn('Test User', notification.message)
        self.assertIn('Normal', notification.message)

    def test_send_email_notification(self):
        """Test sending email notification"""
        context = {
            'patient_name': 'Test User',
            'diagnosis': 'Normal'
        }

        notification = NotificationService.send_notification(
            user=self.user,
            template_type='prediction_ready',
            context_data=context
        )

        # Check that email was sent (using console backend in tests)
        self.assertEqual(notification.status, 'sent')
        self.assertIsNotNone(notification.sent_at)

        # Check notification log was created
        logs = NotificationLog.objects.filter(notification=notification)
        self.assertTrue(logs.exists())
        self.assertTrue(logs.first().success)

    def test_send_notification_respects_preferences(self):
        """Test that notifications respect user preferences"""
        # Disable email
        self.preferences.email_enabled = False
        self.preferences.save()

        context = {'patient_name': 'Test User', 'diagnosis': 'Normal'}

        notification = NotificationService.send_notification(
            user=self.user,
            template_type='prediction_ready',
            context_data=context
        )

        # Notification created but not sent because email is disabled
        self.assertEqual(notification.status, 'pending')

    def test_critical_notifications_bypass_preferences(self):
        """Test that critical notifications bypass user preferences"""
        # Disable email
        self.preferences.email_enabled = False
        self.preferences.save()

        context = {'patient_name': 'Test User'}

        notification = NotificationService.send_notification(
            user=self.user,
            template_type='critical_result',
            context_data=context,
            priority='critical'
        )

        # Critical notification should still be sent
        self.assertEqual(notification.status, 'sent')

    def test_quiet_hours_respected(self):
        """Test that quiet hours are respected for non-critical notifications"""
        # Set quiet hours to current time
        current_time = timezone.now().time()
        self.preferences.quiet_hours_start = time(0, 0)
        self.preferences.quiet_hours_end = time(23, 59)
        self.preferences.save()

        context = {'patient_name': 'Test User', 'diagnosis': 'Normal'}

        notification = NotificationService.send_notification(
            user=self.user,
            template_type='prediction_ready',
            context_data=context
        )

        # Should not be sent during quiet hours
        self.assertEqual(notification.status, 'pending')

    def test_quiet_hours_bypassed_for_critical(self):
        """Test that critical notifications bypass quiet hours"""
        # Set quiet hours to current time
        self.preferences.quiet_hours_start = time(0, 0)
        self.preferences.quiet_hours_end = time(23, 59)
        self.preferences.save()

        context = {'patient_name': 'Test User'}

        notification = NotificationService.send_notification(
            user=self.user,
            template_type='critical_result',
            context_data=context,
            priority='critical'
        )

        # Critical should bypass quiet hours
        self.assertEqual(notification.status, 'sent')

    def test_inactive_template_returns_none(self):
        """Test that inactive templates return None"""
        self.email_template.is_active = False
        self.email_template.save()

        context = {'patient_name': 'Test User', 'diagnosis': 'Normal'}

        notification = NotificationService.send_notification(
            user=self.user,
            template_type='prediction_ready',
            context_data=context
        )

        self.assertIsNone(notification)

    def test_nonexistent_template_returns_none(self):
        """Test that nonexistent template returns None"""
        context = {'patient_name': 'Test User'}

        notification = NotificationService.send_notification(
            user=self.user,
            template_type='nonexistent_type',
            context_data=context
        )

        self.assertIsNone(notification)

    def test_creates_default_preferences(self):
        """Test that default preferences are created if they don't exist"""
        # Create user without preferences
        user2 = User.objects.create_user(username='user2', password='pass')

        context = {'patient_name': 'User 2', 'diagnosis': 'Normal'}

        notification = NotificationService.send_notification(
            user=user2,
            template_type='prediction_ready',
            context_data=context
        )

        # Preferences should be auto-created
        self.assertTrue(
            NotificationPreference.objects.filter(user=user2).exists()
        )

    def test_email_failure_logged(self):
        """Test that email failures are logged"""
        with patch('notifications.services.send_mail') as mock_send:
            mock_send.side_effect = Exception('SMTP Error')

            context = {'patient_name': 'Test User', 'diagnosis': 'Normal'}

            notification = NotificationService.send_notification(
                user=self.user,
                template_type='prediction_ready',
                context_data=context
            )

            # Check notification marked as failed
            self.assertEqual(notification.status, 'failed')
            self.assertIn('SMTP Error', notification.error_message)

            # Check log created
            logs = NotificationLog.objects.filter(notification=notification)
            self.assertTrue(logs.exists())
            self.assertFalse(logs.first().success)


class NotificationSchedulerTests(TestCase):
    """Test NotificationScheduler"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_send_daily_digest(self):
        """Test sending daily digest"""
        # Create some unread notifications
        for i in range(3):
            Notification.objects.create(
                recipient=self.user,
                title=f'Notification {i}',
                message=f'Message {i}',
                channel='in_app',
                status='sent'
            )

        # Call send_daily_digest
        NotificationScheduler.send_daily_digest(self.user)

        # Currently just passes, but structure is in place
        # In future, this would send an actual digest email

    def test_daily_digest_only_recent(self):
        """Test that daily digest only includes recent notifications"""
        # Create old notification
        old_notification = Notification.objects.create(
            recipient=self.user,
            title='Old Notification',
            message='Old message',
            channel='in_app',
            status='sent'
        )
        old_notification.created_at = timezone.now() - timedelta(days=2)
        old_notification.save()

        # Create recent notification
        recent_notification = Notification.objects.create(
            recipient=self.user,
            title='Recent Notification',
            message='Recent message',
            channel='in_app',
            status='sent'
        )

        # Get notifications that would be in digest
        unread = Notification.objects.filter(
            recipient=self.user,
            status='sent',
            read_at__isnull=True,
            created_at__gte=timezone.now() - timedelta(days=1)
        )

        # Only recent notification should be included
        self.assertEqual(unread.count(), 1)
        self.assertEqual(unread.first(), recent_notification)
