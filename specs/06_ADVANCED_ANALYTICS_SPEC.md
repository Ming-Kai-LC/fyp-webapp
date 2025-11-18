# Advanced Analytics Module - Detailed Specification

## Module Information
- **Module Name:** analytics
- **Priority:** MEDIUM-HIGH (Phase 2)
- **Estimated Effort:** 2-3 days
- **Dependencies:** detection app, all other modules (for comprehensive analytics)

## Purpose
Data-driven insights for research, hospital management, and AI model improvement through advanced statistics, trend analysis, and predictive analytics.

## Features

### Core Features
1. Hospital-wide statistics dashboard
2. Disease trend analysis (COVID cases over time)
3. Model performance analytics and comparison
4. Doctor productivity metrics
5. Patient demographics analysis
6. Geographic heatmaps (by region/age/gender)
7. Export for research papers
8. Time-series analysis

### Advanced Features
9. Predictive analytics (outbreak predictions)
10. Machine learning model drift detection
11. Comparative analysis across time periods
12. Custom report builder
13. Data visualization library (charts, graphs, heatmaps)
14. Real-time analytics dashboard
15. Cohort analysis

---

## Database Models

### File: `analytics/models.py`

```python
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

    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    description = models.TextField(blank=True)

    # Configuration
    filters = models.JSONField(help_text="Report filters and parameters")
    chart_type = models.CharField(
        max_length=20,
        choices=[
            ('line', 'Line Chart'),
            ('bar', 'Bar Chart'),
            ('pie', 'Pie Chart'),
            ('heatmap', 'Heatmap'),
            ('table', 'Table'),
        ]
    )

    # Ownership
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

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

    export_type = models.CharField(max_length=30, choices=EXPORT_TYPES)
    exported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    exported_at = models.DateTimeField(auto_now_add=True)

    # Configuration
    filters_applied = models.JSONField(null=True, blank=True)
    date_range_start = models.DateField(null=True, blank=True)
    date_range_end = models.DateField(null=True, blank=True)

    # File
    file_path = models.FileField(upload_to='analytics/exports/%Y/%m/', null=True, blank=True)
    file_format = models.CharField(
        max_length=10,
        choices=[('csv', 'CSV'), ('xlsx', 'Excel'), ('json', 'JSON')]
    )

    # Metadata
    record_count = models.IntegerField()
    anonymized = models.BooleanField(default=False)

    class Meta:
        ordering = ['-exported_at']

    def __str__(self):
        return f"{self.get_export_type_display()} - {self.exported_at.strftime('%Y-%m-%d')}"
```

---

## Services

### File: `analytics/services.py`

```python
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from detection.models import Prediction
from .models import AnalyticsSnapshot, ModelPerformanceMetric
import pandas as pd


class AnalyticsEngine:
    """
    Core analytics computation engine
    """
    @staticmethod
    def generate_daily_snapshot(date=None):
        """
        Generate daily analytics snapshot
        """
        if date is None:
            date = timezone.now().date()

        # Get predictions for the day
        predictions = Prediction.objects.filter(
            xray__upload_date__date=date
        )

        snapshot = AnalyticsSnapshot.objects.create(
            period_type='daily',
            snapshot_date=date,
            total_predictions=predictions.count(),
            covid_positive=predictions.filter(final_diagnosis='COVID').count(),
            normal_cases=predictions.filter(final_diagnosis='Normal').count(),
            viral_pneumonia=predictions.filter(final_diagnosis='Viral Pneumonia').count(),
            lung_opacity=predictions.filter(final_diagnosis='Lung Opacity').count(),
            avg_inference_time=predictions.aggregate(Avg('inference_time'))['inference_time__avg'],
            avg_confidence=predictions.aggregate(Avg('consensus_confidence'))['consensus_confidence__avg'],
        )

        return snapshot

    @staticmethod
    def get_trend_data(days=30):
        """
        Get trend data for the last N days
        """
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)

        snapshots = AnalyticsSnapshot.objects.filter(
            period_type='daily',
            snapshot_date__range=[start_date, end_date]
        ).order_by('snapshot_date')

        return {
            'dates': [s.snapshot_date for s in snapshots],
            'total_predictions': [s.total_predictions for s in snapshots],
            'covid_cases': [s.covid_positive for s in snapshots],
            'normal_cases': [s.normal_cases for s in snapshots],
        }

    @staticmethod
    def get_model_comparison():
        """
        Compare performance of all AI models
        """
        models = ['crossvit', 'resnet50', 'densenet121', 'efficientnet', 'vit', 'swin']
        comparison = {}

        for model in models:
            field_confidence = f'{model}_confidence'
            field_prediction = f'{model}_prediction'

            stats = Prediction.objects.aggregate(
                avg_confidence=Avg(field_confidence),
                total=Count('id')
            )

            # Count how often this model was the best
            # (This is simplified; implement based on your needs)
            comparison[model] = {
                'avg_confidence': stats['avg_confidence'],
                'total_predictions': stats['total'],
            }

        return comparison

    @staticmethod
    def get_demographic_analysis():
        """
        Analyze predictions by patient demographics
        """
        from detection.models import Patient

        analysis = {
            'by_age_group': {},
            'by_gender': {},
            'by_diagnosis': {},
        }

        # Age groups
        age_groups = [
            (0, 18, '0-18'),
            (19, 35, '19-35'),
            (36, 50, '36-50'),
            (51, 65, '51-65'),
            (66, 120, '65+'),
        ]

        for min_age, max_age, label in age_groups:
            count = Prediction.objects.filter(
                xray__patient__age__gte=min_age,
                xray__patient__age__lte=max_age
            ).count()
            analysis['by_age_group'][label] = count

        # Gender
        analysis['by_gender'] = dict(
            Prediction.objects.values('xray__patient__gender').annotate(
                count=Count('id')
            ).values_list('xray__patient__gender', 'count')
        )

        # Diagnosis distribution
        analysis['by_diagnosis'] = dict(
            Prediction.objects.values('final_diagnosis').annotate(
                count=Count('id')
            ).values_list('final_diagnosis', 'count')
        )

        return analysis

    @staticmethod
    def export_to_dataframe(filters=None):
        """
        Export data to pandas DataFrame for research
        """
        predictions = Prediction.objects.select_related('xray__patient__user').all()

        if filters:
            # Apply filters (implement as needed)
            pass

        data = []
        for pred in predictions:
            data.append({
                'patient_id': pred.xray.patient.id,
                'patient_age': pred.xray.patient.age,
                'patient_gender': pred.xray.patient.gender,
                'upload_date': pred.xray.upload_date,
                'final_diagnosis': pred.final_diagnosis,
                'confidence': pred.consensus_confidence,
                'crossvit_pred': pred.crossvit_prediction,
                'crossvit_conf': pred.crossvit_confidence,
                'resnet50_pred': pred.resnet50_prediction,
                'resnet50_conf': pred.resnet50_confidence,
                'inference_time': pred.inference_time,
            })

        return pd.DataFrame(data)
```

---

## URL Configuration

### File: `analytics/urls.py`

```python
from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Main dashboard
    path('dashboard/', views.analytics_dashboard, name='dashboard'),

    # Specific analytics
    path('trends/', views.trend_analysis, name='trends'),
    path('models/', views.model_comparison, name='model_comparison'),
    path('demographics/', views.demographic_analysis, name='demographics'),
    path('predictions/', views.prediction_analytics, name='predictions'),

    # Custom reports
    path('reports/', views.custom_reports, name='custom_reports'),
    path('reports/create/', views.create_custom_report, name='create_custom_report'),
    path('reports/<int:report_id>/', views.view_custom_report, name='view_custom_report'),

    # Data export
    path('export/', views.export_data, name='export_data'),

    # API endpoints
    path('api/snapshot/<str:date>/', views.snapshot_api, name='snapshot_api'),
    path('api/trends/<int:days>/', views.trends_api, name='trends_api'),
]
```

---

## Integration Points

- Add analytics link to admin/doctor dashboards
- Integrate with reporting module for comprehensive reports
- Use audit module data for access analytics
- Visualizations using Chart.js or Plotly

---

## Dependencies

```
# Add to requirements.txt
pandas==2.1.3         # Already included
plotly==5.18.0        # For interactive charts
chart==1.4.0          # Alternative charting library
```

---

## Success Criteria

- ✅ Real-time dashboard shows key metrics
- ✅ Trend analysis reveals disease patterns
- ✅ Model comparison helps identify best performers
- ✅ Demographic insights support research
- ✅ Data export enables external analysis
- ✅ Custom reports provide flexibility
