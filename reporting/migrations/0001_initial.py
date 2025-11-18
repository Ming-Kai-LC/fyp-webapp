# Generated migration for reporting app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('detection', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('template_type', models.CharField(choices=[('standard', 'Standard Report'), ('detailed', 'Detailed Report'), ('summary', 'Summary Report'), ('research', 'Research Export')], max_length=20)),
                ('description', models.TextField(blank=True)),
                ('html_template', models.TextField(help_text='HTML template content')),
                ('css_styles', models.TextField(blank=True, help_text='Custom CSS')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['template_type', 'name'],
            },
        ),
        migrations.CreateModel(
            name='BatchReportJob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('total_reports', models.IntegerField(default=0)),
                ('completed_reports', models.IntegerField(default=0)),
                ('failed_reports', models.IntegerField(default=0)),
                ('zip_file', models.FileField(blank=True, null=True, upload_to='reports/batch/%Y/%m/%d/')),
                ('error_log', models.TextField(blank=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('predictions', models.ManyToManyField(related_name='batch_jobs', to='detection.prediction')),
                ('template', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='reporting.reporttemplate')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('title', models.CharField(default='COVID-19 Detection Report', max_length=200)),
                ('generated_at', models.DateTimeField(auto_now_add=True)),
                ('pdf_file', models.FileField(blank=True, null=True, upload_to='reports/pdf/%Y/%m/%d/')),
                ('file_size', models.IntegerField(blank=True, help_text='File size in bytes', null=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('generated', 'Generated'), ('sent', 'Sent to Patient'), ('printed', 'Printed')], default='draft', max_length=20)),
                ('version', models.IntegerField(default=1)),
                ('include_signature', models.BooleanField(default=True)),
                ('include_hospital_logo', models.BooleanField(default=True)),
                ('include_qr_code', models.BooleanField(default=True)),
                ('sent_to_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('downloaded_count', models.IntegerField(default=0)),
                ('last_downloaded_at', models.DateTimeField(blank=True, null=True)),
                ('custom_notes', models.TextField(blank=True, help_text='Additional notes for the report')),
                ('generated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='generated_reports', to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='detection.patient')),
                ('prediction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='detection.prediction')),
                ('template', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='reporting.reporttemplate')),
            ],
            options={
                'ordering': ['-generated_at'],
            },
        ),
        migrations.AddIndex(
            model_name='report',
            index=models.Index(fields=['report_id'], name='reporting_r_report__f9c8a0_idx'),
        ),
        migrations.AddIndex(
            model_name='report',
            index=models.Index(fields=['patient', '-generated_at'], name='reporting_r_patient_8f3e3a_idx'),
        ),
    ]
