# analytics/models.py
"""
Database models for Advanced Analytics Module
Tracks snapshots, performance metrics, custom reports, and data exports
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class AnalyticsSnapshot(models.Model):
    """
    Daily/weekly/monthly snapshots of key metrics
    """
    PERIOD_TYPES = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    )

    period_type = models.CharField(max_length=20, choices=PERIOD_TYPES)
    snapshot_date = models.DateField(db_index=True)

    # Prediction statistics
    total_predictions = models.IntegerField(default=0)
    covid_positive = models.IntegerField(default=0)
    normal_cases = models.IntegerField(default=0)
    viral_pneumonia = models.IntegerField(default=0)
    lung_opacity = models.IntegerField(default=0)

    # User statistics
    total_patients = models.IntegerField(default=0)
    new_patients = models.IntegerField(default=0)
    active_doctors = models.IntegerField(default=0)

    # Performance metrics
    avg_inference_time = models.FloatField(null=True, blank=True)
    avg_confidence = models.FloatField(null=True, blank=True)

    # Model accuracy (if validation data available)
    model_accuracy = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-snapshot_date']
        unique_together = ['period_type', 'snapshot_date']
        indexes = [
            models.Index(fields=['-snapshot_date']),
            models.Index(fields=['period_type', '-snapshot_date']),
        ]

    def __str__(self):
        return f"{self.get_period_type_display()} Snapshot - {self.snapshot_date}"


class ModelPerformanceMetric(models.Model):
    """
    Track individual model performance over time
    """
    MODEL_CHOICES = (
        ('crossvit', 'CrossViT'),
        ('resnet50', 'ResNet-50'),
        ('densenet121', 'DenseNet-121'),
        ('efficientnet', 'EfficientNet-B0'),
        ('vit', 'ViT-Base'),
        ('swin', 'Swin-Tiny'),
    )

    model_name = models.CharField(max_length=20, choices=MODEL_CHOICES)
    date = models.DateField(db_index=True)

    # Performance metrics
    total_predictions = models.IntegerField(default=0)
    avg_confidence = models.FloatField()
    avg_inference_time = models.FloatField()

    # Accuracy metrics (if validation data available)
    accuracy = models.FloatField(null=True, blank=True)
    precision = models.FloatField(null=True, blank=True)
    recall = models.FloatField(null=True, blank=True)
    f1_score = models.FloatField(null=True, blank=True)

    # Agreement with other models
    agreement_rate = models.FloatField(
        null=True,
        blank=True,
        help_text="How often this model agrees with consensus"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['model_name', 'date']
        indexes = [
            models.Index(fields=['-date']),
            models.Index(fields=['model_name', '-date']),
        ]

    def __str__(self):
        return f"{self.get_model_name_display()} - {self.date}"


class CustomReport(models.Model):
    """
    User-defined custom analytics reports
    """
    REPORT_TYPES = (
        ('prediction_trends', 'Prediction Trends'),
        ('demographic_analysis', 'Demographic Analysis'),
        ('model_comparison', 'Model Comparison'),
        ('doctor_productivity', 'Doctor Productivity'),
        ('patient_outcomes', 'Patient Outcomes'),
        ('custom', 'Custom Query'),
    )

    CHART_TYPES = (
        ('line', 'Line Chart'),
        ('bar', 'Bar Chart'),
        ('pie', 'Pie Chart'),
        ('heatmap', 'Heatmap'),
        ('table', 'Table'),
    )

    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    description = models.TextField(blank=True)

    # Configuration
    filters = models.JSONField(help_text="Report filters and parameters")
    chart_type = models.CharField(max_length=20, choices=CHART_TYPES)

    # Ownership
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['created_by', '-created_at']),
        ]

    def __str__(self):
        return self.name


class DataExport(models.Model):
    """
    Track data exports for research
    """
    EXPORT_TYPES = (
        ('predictions', 'Predictions Data'),
        ('demographics', 'Demographics'),
        ('full_dataset', 'Full Dataset'),
        ('custom', 'Custom Query'),
    )

    FILE_FORMATS = (
        ('csv', 'CSV'),
        ('xlsx', 'Excel'),
        ('json', 'JSON'),
    )

    export_type = models.CharField(max_length=30, choices=EXPORT_TYPES)
    exported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exported_at = models.DateTimeField(auto_now_add=True)

    # Configuration
    filters_applied = models.JSONField(null=True, blank=True)
    date_range_start = models.DateField(null=True, blank=True)
    date_range_end = models.DateField(null=True, blank=True)

    # File
    file_path = models.FileField(upload_to='analytics/exports/%Y/%m/', null=True, blank=True)
    file_format = models.CharField(max_length=10, choices=FILE_FORMATS)

    # Metadata
    record_count = models.IntegerField()
    anonymized = models.BooleanField(default=False)

    class Meta:
        ordering = ['-exported_at']
        indexes = [
            models.Index(fields=['-exported_at']),
            models.Index(fields=['exported_by', '-exported_at']),
        ]

    def __str__(self):
        return f"{self.get_export_type_display()} - {self.exported_at.strftime('%Y-%m-%d')}"
