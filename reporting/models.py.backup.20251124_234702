from django.db import models
from django.conf import settings
from detection.models import Prediction, Patient
import uuid


class ReportTemplate(models.Model):
    """
    Defines different report templates with customizable layouts
    """
    TEMPLATE_TYPES = (
        ('standard', 'Standard Report'),
        ('detailed', 'Detailed Report'),
        ('summary', 'Summary Report'),
        ('research', 'Research Export'),
    )

    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    description = models.TextField(blank=True)
    html_template = models.TextField(help_text="HTML template content")
    css_styles = models.TextField(blank=True, help_text="Custom CSS")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['template_type', 'name']

    def __str__(self):
        return f"{self.get_template_type_display()} - {self.name}"


class Report(models.Model):
    """
    Stores generated reports with metadata for tracking and versioning
    """
    REPORT_STATUS = (
        ('draft', 'Draft'),
        ('generated', 'Generated'),
        ('sent', 'Sent to Patient'),
        ('printed', 'Printed'),
    )

    report_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    prediction = models.ForeignKey(Prediction, on_delete=models.CASCADE, related_name='reports')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='reports')
    template = models.ForeignKey(ReportTemplate, on_delete=models.SET_NULL, null=True)

    # Report metadata
    title = models.CharField(max_length=200, default="COVID-19 Detection Report")
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='generated_reports')
    generated_at = models.DateTimeField(auto_now_add=True)

    # File storage
    pdf_file = models.FileField(upload_to='reports/pdf/%Y/%m/%d/', null=True, blank=True)
    file_size = models.IntegerField(null=True, blank=True, help_text="File size in bytes")

    # Status tracking
    status = models.CharField(max_length=20, choices=REPORT_STATUS, default='draft')
    version = models.IntegerField(default=1)

    # Signature and branding
    include_signature = models.BooleanField(default=True)
    include_hospital_logo = models.BooleanField(default=True)
    include_qr_code = models.BooleanField(default=True)

    # Delivery tracking
    sent_to_email = models.EmailField(blank=True, null=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    downloaded_count = models.IntegerField(default=0)
    last_downloaded_at = models.DateTimeField(null=True, blank=True)

    # Custom notes
    custom_notes = models.TextField(blank=True, help_text="Additional notes for the report")

    class Meta:
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['report_id']),
            models.Index(fields=['patient', '-generated_at']),
        ]

    def __str__(self):
        return f"Report {self.report_id} - {self.patient.user.get_full_name()} - {self.generated_at.strftime('%Y-%m-%d')}"

    def increment_download_count(self):
        from django.utils import timezone
        self.downloaded_count += 1
        self.last_downloaded_at = timezone.now()
        self.save(update_fields=['downloaded_count', 'last_downloaded_at'])


class BatchReportJob(models.Model):
    """
    Tracks batch report generation jobs for multiple patients
    """
    JOB_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    job_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Job configuration
    predictions = models.ManyToManyField(Prediction, related_name='batch_jobs')
    template = models.ForeignKey(ReportTemplate, on_delete=models.SET_NULL, null=True)

    # Status
    status = models.CharField(max_length=20, choices=JOB_STATUS, default='pending')
    total_reports = models.IntegerField(default=0)
    completed_reports = models.IntegerField(default=0)
    failed_reports = models.IntegerField(default=0)

    # Output
    zip_file = models.FileField(upload_to='reports/batch/%Y/%m/%d/', null=True, blank=True)
    error_log = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Batch Job {self.job_id} - {self.status}"

    def get_progress_percentage(self):
        if self.total_reports == 0:
            return 0
        return int((self.completed_reports / self.total_reports) * 100)
