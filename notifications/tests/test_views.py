"""
Tests for notification views
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
import json

from notifications.models import (
    Notification,
    NotificationPreference,
    NotificationTemplate
)


class NotificationListViewTests(TestCase):
    """Test notification list view"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

        # Create notifications
        for i in range(5):
            Notification.objects.create(
                recipient=self.user,
                title=f'Notification {i}',
                message=f'Message {i}',
                channel='in_app',
                status='sent' if i < 3 else 'read'
            )

    def test_notification_list_requires_login(self):
        """Test that notification list requires authentication"""
        self.client.logout()
        response = self.client.get(reverse('notifications:notification_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_notification_list_view(self):
        """Test notification list displays correctly"""
        response = self.client.get(reverse('notifications:notification_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Notification 0')
        self.assertContains(response, 'Notification 4')

    def test_notification_list_only_shows_user_notifications(self):
        """Test that users only see their own notifications"""
        # Create another user with notifications
        other_user = User.objects.create_user(
            username='other',
            password='pass'
        )
        Notification.objects.create(
            recipient=other_user,
            title='Other User Notification',
            message='Should not be visible',
            channel='in_app'
        )

        response = self.client.get(reverse('notifications:notification_list'))
        self.assertNotContains(response, 'Other User Notification')

    def test_notification_list_unread_count(self):
        """Test unread count is displayed"""
        response = self.client.get(reverse('notifications:notification_list'))
        self.assertEqual(response.context['unread_count'], 3)

    def test_notification_list_status_filter(self):
        """Test filtering by status"""
        response = self.client.get(
            reverse('notifications:notification_list') + '?status=sent'
        )
        self.assertEqual(response.status_code, 200)
        # Should only show unread notifications
        notifications = response.context['page_obj']
        for notification in notifications:
            self.assertEqual(notification.status, 'sent')

    def test_notification_list_pagination(self):
        """Test pagination works"""
        # Create more notifications
        for i in range(20):
            Notification.objects.create(
                recipient=self.user,
                title=f'Extra Notification {i}',
                message=f'Extra Message {i}',
                channel='in_app'
            )

        response = self.client.get(reverse('notifications:notification_list'))
        self.assertTrue(response.context['page_obj'].has_next())


class MarkAsReadViewTests(TestCase):
    """Test mark as read view"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

        self.notification = Notification.objects.create(
            recipient=self.user,
            title='Test Notification',
            message='Test message',
            channel='in_app',
            status='sent'
        )

    def test_mark_as_read_requires_login(self):
        """Test that mark as read requires authentication"""
        self.client.logout()
        response = self.client.post(
            reverse('notifications:mark_as_read',
                    args=[self.notification.notification_id])
        )
        self.assertEqual(response.status_code, 302)

    def test_mark_as_read_requires_post(self):
        """Test that mark as read requires POST"""
        response = self.client.get(
            reverse('notifications:mark_as_read',
                    args=[self.notification.notification_id])
        )
        self.assertEqual(response.status_code, 405)  # Method not allowed

    def test_mark_as_read_works(self):
        """Test marking notification as read"""
        response = self.client.post(
            reverse('notifications:mark_as_read',
                    args=[self.notification.notification_id])
        )
        self.assertEqual(response.status_code, 302)  # Redirect

        # Check notification is marked as read
        self.notification.refresh_from_db()
        self.assertEqual(self.notification.status, 'read')
        self.assertIsNotNone(self.notification.read_at)

    def test_mark_as_read_ajax(self):
        """Test AJAX mark as read"""
        response = self.client.post(
            reverse('notifications:mark_as_read',
                    args=[self.notification.notification_id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')

    def test_mark_as_read_wrong_user(self):
        """Test that users can't mark other users' notifications"""
        other_user = User.objects.create_user(
            username='other',
            password='pass'
        )
        other_notification = Notification.objects.create(
            recipient=other_user,
            title='Other Notification',
            message='Other message',
            channel='in_app'
        )

        response = self.client.post(
            reverse('notifications:mark_as_read',
                    args=[other_notification.notification_id])
        )
        self.assertEqual(response.status_code, 404)


class MarkAllAsReadViewTests(TestCase):
    """Test mark all as read view"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

        # Create unread notifications
        for i in range(3):
            Notification.objects.create(
                recipient=self.user,
                title=f'Notification {i}',
                message=f'Message {i}',
                channel='in_app',
                status='sent'
            )

    def test_mark_all_as_read_requires_login(self):
        """Test that mark all requires authentication"""
        self.client.logout()
        response = self.client.post(reverse('notifications:mark_all_as_read'))
        self.assertEqual(response.status_code, 302)

    def test_mark_all_as_read_works(self):
        """Test marking all notifications as read"""
        response = self.client.post(reverse('notifications:mark_all_as_read'))
        self.assertEqual(response.status_code, 302)

        # Check all notifications are marked as read
        unread = Notification.objects.filter(
            recipient=self.user,
            status='sent'
        )
        self.assertEqual(unread.count(), 0)

    def test_mark_all_as_read_ajax(self):
        """Test AJAX mark all as read"""
        response = self.client.post(
            reverse('notifications:mark_all_as_read'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['count'], 3)


class NotificationPreferencesViewTests(TestCase):
    """Test notification preferences view"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_preferences_requires_login(self):
        """Test that preferences requires authentication"""
        self.client.logout()
        response = self.client.get(reverse('notifications:preferences'))
        self.assertEqual(response.status_code, 302)

    def test_preferences_get(self):
        """Test GET request to preferences"""
        response = self.client.get(reverse('notifications:preferences'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_preferences_creates_default(self):
        """Test that default preferences are created if they don't exist"""
        response = self.client.get(reverse('notifications:preferences'))
        self.assertTrue(
            NotificationPreference.objects.filter(user=self.user).exists()
        )

    def test_preferences_post_updates(self):
        """Test POST request updates preferences"""
        data = {
            'email_enabled': True,
            'sms_enabled': False,
            'in_app_enabled': True,
            'prediction_results': True,
            'appointment_reminders': False,
            'report_ready': True,
            'doctor_notes': True,
            'system_updates': False,
            'email_address': 'new@example.com',
            'phone_number': '+1234567890',
            'daily_digest': False
        }

        response = self.client.post(
            reverse('notifications:preferences'),
            data
        )
        self.assertEqual(response.status_code, 302)  # Redirect on success

        # Check preferences were updated
        prefs = NotificationPreference.objects.get(user=self.user)
        self.assertEqual(prefs.email_address, 'new@example.com')
        self.assertFalse(prefs.appointment_reminders)


class NotificationAPIViewTests(TestCase):
    """Test notification API views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

        # Create notifications
        for i in range(5):
            Notification.objects.create(
                recipient=self.user,
                title=f'Notification {i}',
                message=f'Message {i}',
                channel='in_app',
                status='sent' if i < 3 else 'read'
            )

    def test_unread_count_api_requires_login(self):
        """Test that API requires authentication"""
        self.client.logout()
        response = self.client.get(reverse('notifications:unread_count_api'))
        self.assertEqual(response.status_code, 302)

    def test_unread_count_api(self):
        """Test unread count API"""
        response = self.client.get(reverse('notifications:unread_count_api'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['unread_count'], 3)

    def test_latest_notifications_api(self):
        """Test latest notifications API"""
        response = self.client.get(reverse('notifications:latest_notifications_api'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('notifications', data)
        self.assertLessEqual(len(data['notifications']), 10)

    def test_latest_notifications_api_limit(self):
        """Test API limit parameter"""
        response = self.client.get(
            reverse('notifications:latest_notifications_api') + '?limit=3'
        )
        data = json.loads(response.content)
        self.assertEqual(len(data['notifications']), 3)

    def test_latest_notifications_api_structure(self):
        """Test API response structure"""
        response = self.client.get(reverse('notifications:latest_notifications_api'))
        data = json.loads(response.content)

        if data['notifications']:
            notification = data['notifications'][0]
            self.assertIn('id', notification)
            self.assertIn('title', notification)
            self.assertIn('message', notification)
            self.assertIn('status', notification)
            self.assertIn('priority', notification)
            self.assertIn('created_at', notification)
            self.assertIn('action_url', notification)
