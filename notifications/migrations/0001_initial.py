# Generated manually for notifications app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('detection', '0001_initial'),  # Adjust based on your detection app migration
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('template_type', models.CharField(choices=[('prediction_ready', 'Prediction Ready'), ('critical_result', 'Critical Result - COVID Positive'), ('appointment_reminder', 'Appointment Reminder'), ('appointment_confirmed', 'Appointment Confirmed'), ('report_ready', 'Report Ready'), ('account_created', 'Account Created'), ('password_reset', 'Password Reset'), ('test_result_updated', 'Test Result Updated'), ('doctor_notes_added', 'Doctor Notes Added')], max_length=50, unique=True)),
                ('channel', models.CharField(choices=[('email', 'Email'), ('sms', 'SMS'), ('in_app', 'In-App')], max_length=20)),
                ('subject', models.CharField(help_text='For email only', max_length=200)),
                ('body_template', models.TextField(help_text='Use {variable} for placeholders')),
                ('is_active', models.BooleanField(default=True)),
                ('is_critical', models.BooleanField(default=False, help_text='Critical notifications bypass user preferences')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='NotificationPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_enabled', models.BooleanField(default=True)),
                ('sms_enabled', models.BooleanField(default=False)),
                ('in_app_enabled', models.BooleanField(default=True)),
                ('prediction_results', models.BooleanField(default=True)),
                ('appointment_reminders', models.BooleanField(default=True)),
                ('report_ready', models.BooleanField(default=True)),
                ('doctor_notes', models.BooleanField(default=True)),
                ('system_updates', models.BooleanField(default=False)),
                ('email_address', models.EmailField(blank=True, max_length=254)),
                ('phone_number', models.CharField(blank=True, max_length=20)),
                ('quiet_hours_start', models.TimeField(blank=True, help_text="Don't send non-critical notifications during quiet hours", null=True)),
                ('quiet_hours_end', models.TimeField(blank=True, null=True)),
                ('daily_digest', models.BooleanField(default=False, help_text='Receive daily summary instead of individual notifications')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='notification_preferences', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('channel', models.CharField(choices=[('email', 'Email'), ('sms', 'SMS'), ('in_app', 'In-App')], default='in_app', max_length=20)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('sent', 'Sent'), ('failed', 'Failed'), ('read', 'Read')], default='pending', max_length=20)),
                ('priority', models.CharField(choices=[('low', 'Low'), ('normal', 'Normal'), ('high', 'High'), ('critical', 'Critical')], default='normal', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('recipient_email', models.EmailField(blank=True, max_length=254)),
                ('recipient_phone', models.CharField(blank=True, max_length=20)),
                ('error_message', models.TextField(blank=True)),
                ('action_url', models.URLField(blank=True, help_text='Link to related resource')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
                ('related_prediction', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notifications', to='detection.prediction')),
                ('template', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='notifications.notificationtemplate')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='NotificationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attempted_at', models.DateTimeField(auto_now_add=True)),
                ('success', models.BooleanField()),
                ('channel', models.CharField(max_length=20)),
                ('error_details', models.TextField(blank=True)),
                ('provider', models.CharField(blank=True, max_length=50)),
                ('provider_response', models.TextField(blank=True)),
                ('notification', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='delivery_logs', to='notifications.notification')),
            ],
            options={
                'ordering': ['-attempted_at'],
            },
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['recipient', '-created_at'], name='notificatio_recipie_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['status', 'priority'], name='notificatio_status_idx'),
        ),
    ]
