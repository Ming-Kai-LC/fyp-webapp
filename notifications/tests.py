from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import NotificationTemplate, Notification, NotificationPreference
from .services import NotificationService

User = get_user_model()


class NotificationTestCase(TestCase):
    """
    Test cases for notification system
    """

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_notification_preference_creation(self):
        """Test that notification preferences are created"""
        prefs = NotificationPreference.objects.create(user=self.user)
        self.assertTrue(prefs.email_enabled)
        self.assertTrue(prefs.in_app_enabled)
        self.assertFalse(prefs.sms_enabled)

    def test_notification_creation(self):
        """Test creating a notification"""
        notification = Notification.objects.create(
            recipient=self.user,
            title='Test Notification',
            message='This is a test',
            channel='in_app',
            priority='normal'
        )
        self.assertEqual(notification.status, 'pending')
        self.assertIsNotNone(notification.notification_id)

    def test_mark_as_read(self):
        """Test marking notification as read"""
        notification = Notification.objects.create(
            recipient=self.user,
            title='Test',
            message='Test message',
            status='sent'
        )
        notification.mark_as_read()
        self.assertEqual(notification.status, 'read')
        self.assertIsNotNone(notification.read_at)
