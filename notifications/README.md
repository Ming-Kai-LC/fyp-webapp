# Notification System Module

Real-time notification system for COVID-19 detection results, appointment reminders, and system alerts.

## Features

### Core Features
- Email notifications for results and critical findings
- SMS alerts for positive COVID-19 cases (Twilio integration ready)
- In-app notifications with real-time updates
- User notification preferences management
- Customizable notification templates
- Delivery status tracking and logging
- Emergency contact notifications

### Advanced Features
- Push notifications (ready for mobile app integration)
- Scheduled notifications (appointment reminders)
- Notification batching (daily digest)
- Priority-based routing
- Quiet hours support
- Multi-channel delivery (email, SMS, in-app)

## Installation

1. The app is already added to `INSTALLED_APPS` in `config/settings.py`

2. Run migrations to create database tables:
```bash
python manage.py migrate notifications
```

3. The default notification templates will be automatically created via the data migration.

## Configuration

### Email Settings (Development)

The system uses Django's console email backend for development (emails print to console):

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Email Settings (Production)

For production, configure SMTP in `config/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'your-email@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'your-app-password')
```

### SMS Settings (Optional - Twilio)

To enable SMS notifications, add to `config/settings.py`:

```python
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '')
```

And uncomment the Twilio code in `notifications/services.py`.

## Usage

### Sending Notifications Programmatically

```python
from notifications.services import NotificationService

# Send a prediction notification
NotificationService.send_prediction_notification(prediction)

# Send custom notification
NotificationService.send_notification(
    user=user,
    template_type='prediction_ready',
    context_data={
        'patient_name': user.get_full_name(),
        'diagnosis': 'COVID',
        'confidence': 95.5,
        'action_url': '/detection/results/123/',
    },
    priority='critical',
    related_prediction=prediction
)
```

### Integration with Detection Module

To send notifications when predictions are ready, add to `detection/views.py`:

```python
from notifications.services import NotificationService

# After creating prediction
prediction = Prediction.objects.create(...)
NotificationService.send_prediction_notification(prediction)
```

### Daily Digest

To send daily digest emails:

```bash
python manage.py send_daily_digest
```

Schedule this with cron or Celery for automated daily emails.

## URLs

- `/notifications/` - List all notifications
- `/notifications/<uuid>/read/` - Mark notification as read
- `/notifications/mark-all-read/` - Mark all as read
- `/notifications/preferences/` - User notification preferences
- `/notifications/api/unread-count/` - API: Get unread count
- `/notifications/api/latest/` - API: Get latest notifications

## Admin Interface

Access the admin panel at `/admin/notifications/` to:

- Manage notification templates
- View all notifications and their delivery status
- Check notification logs for debugging
- Manage user preferences

## Database Models

### NotificationTemplate
Defines reusable templates for different notification types (email/SMS/in-app).

### Notification
Individual notification instances sent to users.

### NotificationPreference
User-specific notification preferences (channels, quiet hours, digest).

### NotificationLog
Delivery attempt logs for debugging and monitoring.

## Notification Types

The system includes templates for:

1. **prediction_ready** - Test results available
2. **critical_result** - COVID-19 positive result (critical priority)
3. **appointment_reminder** - Upcoming appointment
4. **appointment_confirmed** - Appointment confirmation
5. **report_ready** - Medical report available
6. **account_created** - New account welcome
7. **password_reset** - Password reset request
8. **test_result_updated** - Result updated
9. **doctor_notes_added** - Doctor added notes

## Testing

Run tests:

```bash
python manage.py test notifications
```

## Security Considerations

- Email addresses and phone numbers are validated
- Critical notifications bypass quiet hours
- User preferences are enforced for non-critical notifications
- Delivery failures are logged for audit
- CSRF protection on all forms

## Dependencies

- Django 4.2.7
- django-crispy-forms
- crispy-bootstrap5
- Optional: twilio (for SMS)
- Optional: celery (for async tasks)

## Future Enhancements

- [ ] Push notifications for mobile apps
- [ ] WhatsApp integration
- [ ] Telegram bot integration
- [ ] Real-time WebSocket notifications
- [ ] Advanced analytics and reporting
- [ ] A/B testing for notification templates
- [ ] Notification scheduling UI

## Support

For issues or questions, refer to the main project documentation or contact the development team.
