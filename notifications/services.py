from django.core.mail import send_mail
from django.conf import settings
from django.template import Template, Context
from django.utils import timezone
from .models import Notification, NotificationTemplate, NotificationLog, NotificationPreference


class NotificationService:
    """
    Core service for sending notifications via multiple channels
    """
    @staticmethod
    def send_notification(user, template_type, context_data, priority='normal', related_prediction=None):
        """
        Send notification using appropriate template and channel
        """
        # Get template
        try:
            template = NotificationTemplate.objects.get(
                template_type=template_type,
                is_active=True
            )
        except NotificationTemplate.DoesNotExist:
            return None

        # Get user preferences
        try:
            prefs = NotificationPreference.objects.get(user=user)
        except NotificationPreference.DoesNotExist:
            # Create default preferences
            prefs = NotificationPreference.objects.create(user=user)

        # Render message
        subject = Template(template.subject).render(Context(context_data)) if template.subject else ''
        message = Template(template.body_template).render(Context(context_data))

        # Create notification record
        notification = Notification.objects.create(
            recipient=user,
            template=template,
            title=subject or template.get_template_type_display(),
            message=message,
            channel=template.channel,
            priority=priority,
            related_prediction=related_prediction,
            recipient_email=prefs.email_address or user.email,
            recipient_phone=prefs.phone_number,
            action_url=context_data.get('action_url', '')
        )

        # Send based on channel and preferences
        if template.is_critical or NotificationService._should_send_now(prefs, template):
            if template.channel == 'email' and prefs.email_enabled:
                NotificationService._send_email(notification)
            elif template.channel == 'sms' and prefs.sms_enabled:
                NotificationService._send_sms(notification)
            elif template.channel == 'in_app':
                notification.status = 'sent'
                notification.sent_at = timezone.now()
                notification.save()

        return notification

    @staticmethod
    def _should_send_now(prefs, template):
        """
        Check if notification should be sent now based on preferences and quiet hours
        """
        # Critical notifications always send
        if template.is_critical:
            return True

        # Check quiet hours for non-critical
        now = timezone.now().time()
        if prefs.quiet_hours_start and prefs.quiet_hours_end:
            if prefs.quiet_hours_start <= now <= prefs.quiet_hours_end:
                return False

        return True

    @staticmethod
    def _send_email(notification):
        """
        Send email notification
        """
        try:
            send_mail(
                subject=notification.title,
                message=notification.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.recipient_email],
                fail_silently=False,
            )

            notification.status = 'sent'
            notification.sent_at = timezone.now()
            notification.save()

            NotificationLog.objects.create(
                notification=notification,
                success=True,
                channel='email'
            )

        except Exception as e:
            notification.status = 'failed'
            notification.error_message = str(e)
            notification.save()

            NotificationLog.objects.create(
                notification=notification,
                success=False,
                channel='email',
                error_details=str(e)
            )

    @staticmethod
    def _send_sms(notification):
        """
        Send SMS notification using Twilio or similar service
        """
        try:
            # Implement SMS sending logic using Twilio, AWS SNS, or similar
            # from twilio.rest import Client
            # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            # message = client.messages.create(
            #     body=notification.message,
            #     from_=settings.TWILIO_PHONE_NUMBER,
            #     to=notification.recipient_phone
            # )

            # For now, mark as sent (implement actual SMS later)
            notification.status = 'sent'
            notification.sent_at = timezone.now()
            notification.save()

            NotificationLog.objects.create(
                notification=notification,
                success=True,
                channel='sms',
                provider='twilio'
            )

        except Exception as e:
            notification.status = 'failed'
            notification.error_message = str(e)
            notification.save()

            NotificationLog.objects.create(
                notification=notification,
                success=False,
                channel='sms',
                error_details=str(e)
            )

    @staticmethod
    def send_prediction_notification(prediction):
        """
        Send notification when prediction is ready
        """
        patient_user = prediction.xray.patient.user
        context = {
            'patient_name': patient_user.get_full_name(),
            'diagnosis': prediction.final_diagnosis,
            'confidence': prediction.consensus_confidence,
            'action_url': f'/detection/results/{prediction.id}/',
        }

        # Determine priority based on diagnosis
        priority = 'critical' if prediction.final_diagnosis == 'COVID' else 'normal'

        return NotificationService.send_notification(
            user=patient_user,
            template_type='prediction_ready' if priority == 'normal' else 'critical_result',
            context_data=context,
            priority=priority,
            related_prediction=prediction
        )


class NotificationScheduler:
    """
    Schedule and batch notifications
    """
    @staticmethod
    def send_daily_digest(user):
        """
        Send daily digest of unread notifications
        """
        unread = Notification.objects.filter(
            recipient=user,
            status='sent',
            read_at__isnull=True,
            created_at__gte=timezone.now() - timezone.timedelta(days=1)
        )

        if unread.count() > 0:
            # Send digest email
            # Implementation here
            pass
