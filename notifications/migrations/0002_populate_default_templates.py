# Data migration to populate default notification templates

from django.db import migrations


def create_default_templates(apps, schema_editor):
    """
    Create default notification templates for the system
    """
    NotificationTemplate = apps.get_model('notifications', 'NotificationTemplate')

    templates = [
        {
            'template_type': 'prediction_ready',
            'channel': 'in_app',
            'subject': 'Your COVID-19 Test Results are Ready',
            'body_template': 'Hello {patient_name},\n\nYour COVID-19 test results are now ready. Diagnosis: {diagnosis} (Confidence: {confidence}%)\n\nPlease check your account for detailed results.',
            'is_critical': False,
        },
        {
            'template_type': 'critical_result',
            'channel': 'email',
            'subject': 'URGENT: COVID-19 Positive Result',
            'body_template': 'URGENT NOTIFICATION\n\nDear {patient_name},\n\nYour COVID-19 test result is POSITIVE (Confidence: {confidence}%).\n\nPlease take immediate action:\n1. Self-isolate immediately\n2. Contact your healthcare provider\n3. Follow local health guidelines\n\nView full details: {action_url}',
            'is_critical': True,
        },
        {
            'template_type': 'appointment_reminder',
            'channel': 'in_app',
            'subject': 'Appointment Reminder',
            'body_template': 'Hello {patient_name},\n\nThis is a reminder about your upcoming appointment.\n\nDate: {appointment_date}\nTime: {appointment_time}\nLocation: {location}',
            'is_critical': False,
        },
        {
            'template_type': 'appointment_confirmed',
            'channel': 'email',
            'subject': 'Appointment Confirmed',
            'body_template': 'Dear {patient_name},\n\nYour appointment has been confirmed.\n\nDetails:\n- Date: {appointment_date}\n- Time: {appointment_time}\n- Doctor: {doctor_name}\n- Location: {location}\n\nPlease arrive 15 minutes early.',
            'is_critical': False,
        },
        {
            'template_type': 'report_ready',
            'channel': 'in_app',
            'subject': 'Medical Report Ready for Download',
            'body_template': 'Hello {patient_name},\n\nYour medical report is now ready for download.\n\nReport Type: {report_type}\nGenerated: {generated_date}\n\nView report: {action_url}',
            'is_critical': False,
        },
        {
            'template_type': 'account_created',
            'channel': 'email',
            'subject': 'Welcome to COVID-19 Detection System',
            'body_template': 'Welcome {patient_name}!\n\nYour account has been successfully created.\n\nUsername: {username}\n\nYou can now access all features of the COVID-19 Detection System.\n\nLogin here: {action_url}',
            'is_critical': False,
        },
        {
            'template_type': 'password_reset',
            'channel': 'email',
            'subject': 'Password Reset Request',
            'body_template': 'Hello {patient_name},\n\nWe received a request to reset your password.\n\nClick here to reset: {action_url}\n\nIf you did not request this, please ignore this message.\n\nThis link expires in 24 hours.',
            'is_critical': False,
        },
        {
            'template_type': 'test_result_updated',
            'channel': 'in_app',
            'subject': 'Test Result Updated',
            'body_template': 'Hello {patient_name},\n\nYour test results have been updated.\n\nPrevious: {previous_diagnosis}\nUpdated: {current_diagnosis}\n\nReason: {update_reason}\n\nView details: {action_url}',
            'is_critical': False,
        },
        {
            'template_type': 'doctor_notes_added',
            'channel': 'in_app',
            'subject': 'Doctor Added Notes to Your Record',
            'body_template': 'Hello {patient_name},\n\nDr. {doctor_name} has added notes to your medical record.\n\nDate: {note_date}\n\nPlease login to view the details: {action_url}',
            'is_critical': False,
        },
    ]

    for template_data in templates:
        NotificationTemplate.objects.get_or_create(
            template_type=template_data['template_type'],
            defaults=template_data
        )


def remove_default_templates(apps, schema_editor):
    """
    Remove default templates if migration is reversed
    """
    NotificationTemplate = apps.get_model('notifications', 'NotificationTemplate')
    NotificationTemplate.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_templates, remove_default_templates),
    ]
