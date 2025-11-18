# Notification System Module

## Overview
Real-time notification system for critical COVID-19 results, appointment reminders, and system alerts via email, SMS, and in-app notifications.

## Features
- Email notifications for results and critical findings
- SMS alerts for positive COVID-19 cases
- In-app notifications with real-time updates
- User notification preferences management
- Notification templates
- Delivery status tracking and logging

## Installation

### 1. Run Migrations
```bash
python manage.py makemigrations notifications
python manage.py migrate notifications
```

### 2. Load Default Templates
```bash
python manage.py loaddata notification_templates
```

### 3. Configure Email Settings
Update `config/settings.py` with your email provider settings:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'COVID-19 Detection System <noreply@example.com>'
```

## Usage

### Sending Notifications

#### From Detection Views
```python
from notifications.services import NotificationService

# Send notification when prediction is ready
NotificationService.send_prediction_notification(prediction)
```

#### Custom Notifications
```python
from notifications.services import NotificationService

context = {
    'patient_name': user.get_full_name(),
    'diagnosis': 'COVID',
    'confidence': 95.5,
    'action_url': '/detection/results/123/',
}

NotificationService.send_notification(
    user=user,
    template_type='prediction_ready',
    context_data=context,
    priority='critical',
    related_prediction=prediction
)
```

### User Preferences
Users can manage their notification preferences at:
```
/notifications/preferences/
```

### API Endpoints

#### Get Unread Count
```javascript
fetch('/notifications/api/unread-count/')
    .then(response => response.json())
    .then(data => console.log(data.unread_count));
```

#### Get Latest Notifications
```javascript
fetch('/notifications/api/latest/?limit=10')
    .then(response => response.json())
    .then(data => console.log(data.notifications));
```

## Models

### NotificationTemplate
Stores templates for different notification types.

### Notification
Individual notification instances with status tracking.

### NotificationPreference
User-specific notification settings.

### NotificationLog
Delivery attempt logs for debugging.

## Admin Interface
Access Django admin to manage:
- Notification templates
- User notifications
- User preferences
- Delivery logs

## Integration with Detection App

### Automatic Notifications
Add to `detection/views.py` after prediction creation:

```python
from notifications.services import NotificationService

# After creating prediction
NotificationService.send_prediction_notification(prediction)
```

## SMS Configuration (Optional)

To enable SMS notifications, install Twilio and configure:

```bash
pip install twilio==8.10.0
```

Update `config/settings.py`:
```python
TWILIO_ACCOUNT_SID = 'your-account-sid'
TWILIO_AUTH_TOKEN = 'your-auth-token'
TWILIO_PHONE_NUMBER = '+1234567890'
```

Uncomment the Twilio code in `notifications/services.py`:
```python
def _send_sms(notification):
    from twilio.rest import Client
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=notification.message,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=notification.recipient_phone
    )
```

## Testing

### Test Email Notifications
```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from notifications.services import NotificationService

user = User.objects.first()
context = {
    'patient_name': user.get_full_name(),
    'diagnosis': 'Normal',
    'confidence': 98.5,
    'action_url': '/detection/results/1/',
}

NotificationService.send_notification(
    user=user,
    template_type='prediction_ready',
    context_data=context
)
```

## URL Structure
- `/notifications/` - List all notifications
- `/notifications/preferences/` - Manage preferences
- `/notifications/<uuid>/read/` - Mark as read
- `/notifications/mark-all-read/` - Mark all as read
- `/notifications/api/unread-count/` - API: Get unread count
- `/notifications/api/latest/` - API: Get latest notifications

## Success Criteria
- ✅ Email notifications sent for critical results
- ✅ In-app notifications display in real-time
- ✅ Users can manage notification preferences
- ✅ SMS alerts for COVID-positive cases
- ✅ Notification history is tracked
- ✅ Delivery failures are logged and can be retried

## Future Enhancements
- Push notifications for mobile apps
- Scheduled notifications (appointment reminders)
- Notification batching (daily digest)
- Multi-language support
- Notification categories and filtering
- Rich notifications with images and action buttons
