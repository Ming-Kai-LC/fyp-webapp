"""
Batch Processing Models for COVID-19 Detection System
Handles batch upload jobs and progress tracking
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class BatchUploadJob(models.Model):
    """
    Track batch X-ray upload jobs for async processing
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('partial', 'Partially Completed'),
    )

    job_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='batch_upload_jobs'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Job status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Progress tracking
    total_images = models.IntegerField(default=0)
    images_processed = models.IntegerField(default=0)
    images_successful = models.IntegerField(default=0)
    images_failed = models.IntegerField(default=0)

    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Configuration
    apply_clahe = models.BooleanField(default=True, help_text="Apply CLAHE preprocessing")
    patient = models.ForeignKey(
        'detection.Patient',
        on_delete=models.CASCADE,
        related_name='batch_jobs',
        help_text="Patient for all X-rays in this batch"
    )

    # Notes and metadata
    notes = models.TextField(blank=True, help_text="Batch upload notes")
    error_log = models.TextField(blank=True, help_text="Errors encountered during processing")

    # Celery task ID
    celery_task_id = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Batch Upload Job"
        verbose_name_plural = "Batch Upload Jobs"
        indexes = [
            models.Index(fields=['created_by', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self):
        return f"Batch Job {self.job_id} - {self.status} ({self.images_processed}/{self.total_images})"

    def get_progress_percentage(self):
        """Calculate progress percentage"""
        if self.total_images == 0:
            return 0
        return int((self.images_processed / self.total_images) * 100)

    def get_success_rate(self):
        """Calculate success rate percentage"""
        if self.images_processed == 0:
            return 0
        return int((self.images_successful / self.images_processed) * 100)

    def mark_as_processing(self):
        """Mark job as processing"""
        self.status = 'processing'
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at', 'updated_at'])

    def mark_as_completed(self):
        """Mark job as completed"""
        self.completed_at = timezone.now()
        if self.images_failed > 0:
            self.status = 'partial'
        else:
            self.status = 'completed'
        self.save(update_fields=['status', 'completed_at', 'updated_at'])

    def mark_as_failed(self, error_message=''):
        """Mark job as failed"""
        self.status = 'failed'
        self.completed_at = timezone.now()
        if error_message:
            self.error_log = error_message
        self.save(update_fields=['status', 'completed_at', 'error_log', 'updated_at'])

    def increment_progress(self, success=True):
        """Increment progress counters"""
        self.images_processed += 1
        if success:
            self.images_successful += 1
        else:
            self.images_failed += 1
        self.save(update_fields=['images_processed', 'images_successful', 'images_failed', 'updated_at'])

    def get_duration(self):
        """Get job duration in seconds"""
        if not self.started_at:
            return None
        end_time = self.completed_at or timezone.now()
        return (end_time - self.started_at).total_seconds()


class BatchUploadImage(models.Model):
    """
    Individual images within a batch upload job
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    batch_job = models.ForeignKey(
        BatchUploadJob,
        on_delete=models.CASCADE,
        related_name='images'
    )

    # Image file
    image_file = models.ImageField(upload_to='xrays/batch/%Y/%m/%d/')
    original_filename = models.CharField(max_length=255)

    # Processing status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    order = models.IntegerField(help_text="Processing order within batch")

    # Linked to main XRayImage after processing
    xray_image = models.ForeignKey(
        'detection.XRayImage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='batch_upload_source'
    )

    # Error tracking
    error_message = models.TextField(blank=True)

    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['batch_job', 'order']
        verbose_name = "Batch Upload Image"
        verbose_name_plural = "Batch Upload Images"
        indexes = [
            models.Index(fields=['batch_job', 'status']),
        ]

    def __str__(self):
        return f"{self.original_filename} - {self.status}"

    def mark_as_processing(self):
        """Mark image as processing"""
        self.status = 'processing'
        self.save(update_fields=['status'])

    def mark_as_completed(self, xray_image):
        """Mark image as completed"""
        self.status = 'completed'
        self.xray_image = xray_image
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'xray_image', 'processed_at'])

    def mark_as_failed(self, error_message):
        """Mark image as failed"""
        self.status = 'failed'
        self.error_message = error_message
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'error_message', 'processed_at'])
