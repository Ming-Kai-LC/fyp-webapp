# analytics/services.py
"""
Analytics computation engine for data-driven insights
Provides snapshot generation, trend analysis, model comparison, and demographics
"""
from typing import Dict, List, Any, Optional
from django.db.models import Count, Avg, Q, F
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta, date
from detection.models import Prediction, Patient, XRayImage
from .models import AnalyticsSnapshot, ModelPerformanceMetric


class AnalyticsEngine:
    """
    Core analytics computation engine
    """

    @staticmethod
    def generate_daily_snapshot(target_date: Optional[date] = None) -> AnalyticsSnapshot:
        """
        Generate daily analytics snapshot

        Args:
            target_date: Date for snapshot (defaults to today)

        Returns:
            AnalyticsSnapshot object
        """
        if target_date is None:
            target_date = timezone.now().date()

        # Get predictions for the day
        predictions = Prediction.objects.filter(
            created_at__date=target_date
        )

        # Count patients
        total_patients = Patient.objects.filter(
            created_at__date__lte=target_date
        ).count()

        new_patients = Patient.objects.filter(
            created_at__date=target_date
        ).count()

        # Count active doctors (users with doctor role who uploaded xrays on this day)
        from detection.models import UserProfile
        active_doctors = User.objects.filter(
            profile__role='doctor',
            uploaded_xrays__upload_date__date=target_date
        ).distinct().count()

        # Create or update snapshot
        snapshot, created = AnalyticsSnapshot.objects.update_or_create(
            period_type='daily',
            snapshot_date=target_date,
            defaults={
                'total_predictions': predictions.count(),
                'covid_positive': predictions.filter(final_diagnosis='COVID').count(),
                'normal_cases': predictions.filter(final_diagnosis='Normal').count(),
                'viral_pneumonia': predictions.filter(final_diagnosis='Viral Pneumonia').count(),
                'lung_opacity': predictions.filter(final_diagnosis='Lung Opacity').count(),
                'total_patients': total_patients,
                'new_patients': new_patients,
                'active_doctors': active_doctors,
                'avg_inference_time': predictions.aggregate(Avg('inference_time'))['inference_time__avg'],
                'avg_confidence': predictions.aggregate(Avg('consensus_confidence'))['consensus_confidence__avg'],
            }
        )

        return snapshot

    @staticmethod
    def generate_weekly_snapshot(target_date: Optional[date] = None) -> AnalyticsSnapshot:
        """
        Generate weekly analytics snapshot

        Args:
            target_date: End date of week (defaults to today)

        Returns:
            AnalyticsSnapshot object
        """
        if target_date is None:
            target_date = timezone.now().date()

        # Get start of week (Monday)
        start_date = target_date - timedelta(days=target_date.weekday())
        end_date = start_date + timedelta(days=6)

        predictions = Prediction.objects.filter(
            created_at__date__range=[start_date, end_date]
        )

        snapshot, created = AnalyticsSnapshot.objects.update_or_create(
            period_type='weekly',
            snapshot_date=end_date,
            defaults={
                'total_predictions': predictions.count(),
                'covid_positive': predictions.filter(final_diagnosis='COVID').count(),
                'normal_cases': predictions.filter(final_diagnosis='Normal').count(),
                'viral_pneumonia': predictions.filter(final_diagnosis='Viral Pneumonia').count(),
                'lung_opacity': predictions.filter(final_diagnosis='Lung Opacity').count(),
                'avg_inference_time': predictions.aggregate(Avg('inference_time'))['inference_time__avg'],
                'avg_confidence': predictions.aggregate(Avg('consensus_confidence'))['consensus_confidence__avg'],
            }
        )

        return snapshot

    @staticmethod
    def get_trend_data(days: int = 30) -> Dict[str, List]:
        """
        Get trend data for the last N days

        Args:
            days: Number of days to look back

        Returns:
            Dictionary with trend data arrays
        """
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)

        snapshots = AnalyticsSnapshot.objects.filter(
            period_type='daily',
            snapshot_date__range=[start_date, end_date]
        ).order_by('snapshot_date')

        return {
            'dates': [s.snapshot_date.isoformat() for s in snapshots],
            'total_predictions': [s.total_predictions for s in snapshots],
            'covid_cases': [s.covid_positive for s in snapshots],
            'normal_cases': [s.normal_cases for s in snapshots],
            'viral_pneumonia': [s.viral_pneumonia for s in snapshots],
            'lung_opacity': [s.lung_opacity for s in snapshots],
            'avg_confidence': [s.avg_confidence for s in snapshots],
        }

    @staticmethod
    def get_model_comparison() -> Dict[str, Dict[str, Any]]:
        """
        Compare performance of all AI models

        Returns:
            Dictionary with model comparison data
        """
        models = ['crossvit', 'resnet50', 'densenet121', 'efficientnet', 'vit', 'swin']
        comparison = {}

        for model in models:
            field_confidence = f'{model}_confidence'
            field_prediction = f'{model}_prediction'

            # Get aggregate statistics
            stats = Prediction.objects.aggregate(
                avg_confidence=Avg(field_confidence),
                total=Count('id')
            )

            # Count predictions by diagnosis for this model
            diagnoses = {}
            for diagnosis in ['COVID', 'Normal', 'Viral Pneumonia', 'Lung Opacity']:
                count = Prediction.objects.filter(**{field_prediction: diagnosis}).count()
                diagnoses[diagnosis] = count

            comparison[model] = {
                'avg_confidence': round(stats['avg_confidence'], 2) if stats['avg_confidence'] else 0,
                'total_predictions': stats['total'],
                'diagnoses': diagnoses,
            }

        return comparison

    @staticmethod
    def get_demographic_analysis() -> Dict[str, Dict]:
        """
        Analyze predictions by patient demographics

        Returns:
            Dictionary with demographic analysis data
        """
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

        # Gender distribution
        gender_data = Prediction.objects.values('xray__patient__gender').annotate(
            count=Count('id')
        )

        for item in gender_data:
            gender = item['xray__patient__gender']
            analysis['by_gender'][gender] = item['count']

        # Diagnosis distribution
        diagnosis_data = Prediction.objects.values('final_diagnosis').annotate(
            count=Count('id')
        )

        for item in diagnosis_data:
            diagnosis = item['final_diagnosis']
            analysis['by_diagnosis'][diagnosis] = item['count']

        return analysis

    @staticmethod
    def get_doctor_productivity(days: int = 30) -> List[Dict[str, Any]]:
        """
        Analyze doctor productivity metrics

        Args:
            days: Number of days to analyze

        Returns:
            List of doctor productivity data
        """
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)

        from detection.models import UserProfile

        doctors = User.objects.filter(
            profile__role='doctor',
            uploaded_xrays__upload_date__date__range=[start_date, end_date]
        ).annotate(
            total_xrays=Count('uploaded_xrays'),
            validated_predictions=Count(
                'reviewed_predictions',
                filter=Q(reviewed_predictions__is_validated=True)
            )
        ).order_by('-total_xrays')

        productivity = []
        for doctor in doctors:
            productivity.append({
                'name': doctor.get_full_name() or doctor.username,
                'username': doctor.username,
                'total_xrays': doctor.total_xrays,
                'validated_predictions': doctor.validated_predictions,
            })

        return productivity

    @staticmethod
    def export_to_dataframe(filters: Optional[Dict] = None):
        """
        Export data to pandas DataFrame for research

        Args:
            filters: Optional filters to apply

        Returns:
            pandas DataFrame
        """
        import pandas as pd

        predictions = Prediction.objects.select_related(
            'xray__patient__user'
        ).all()

        if filters:
            # Apply date range filter
            if 'date_start' in filters and filters['date_start']:
                predictions = predictions.filter(created_at__date__gte=filters['date_start'])
            if 'date_end' in filters and filters['date_end']:
                predictions = predictions.filter(created_at__date__lte=filters['date_end'])

            # Apply diagnosis filter
            if 'diagnosis' in filters and filters['diagnosis']:
                predictions = predictions.filter(final_diagnosis=filters['diagnosis'])

        data = []
        for pred in predictions:
            data.append({
                'patient_id': pred.xray.patient.id,
                'patient_age': pred.xray.patient.age,
                'patient_gender': pred.xray.patient.gender,
                'upload_date': pred.xray.upload_date,
                'prediction_date': pred.created_at,
                'final_diagnosis': pred.final_diagnosis,
                'consensus_confidence': pred.consensus_confidence,
                'crossvit_pred': pred.crossvit_prediction,
                'crossvit_conf': pred.crossvit_confidence,
                'resnet50_pred': pred.resnet50_prediction,
                'resnet50_conf': pred.resnet50_confidence,
                'densenet121_pred': pred.densenet121_prediction,
                'densenet121_conf': pred.densenet121_confidence,
                'efficientnet_pred': pred.efficientnet_prediction,
                'efficientnet_conf': pred.efficientnet_confidence,
                'vit_pred': pred.vit_prediction,
                'vit_conf': pred.vit_confidence,
                'swin_pred': pred.swin_prediction,
                'swin_conf': pred.swin_confidence,
                'inference_time': pred.inference_time,
                'is_validated': pred.is_validated,
            })

        return pd.DataFrame(data)

    @staticmethod
    def get_dashboard_summary() -> Dict[str, Any]:
        """
        Get summary statistics for main dashboard

        Returns:
            Dictionary with summary statistics
        """
        # Get today's data
        today = timezone.now().date()

        # Total predictions
        total_predictions = Prediction.objects.count()
        today_predictions = Prediction.objects.filter(created_at__date=today).count()

        # Diagnosis breakdown
        covid_count = Prediction.objects.filter(final_diagnosis='COVID').count()
        normal_count = Prediction.objects.filter(final_diagnosis='Normal').count()

        # Patient stats
        total_patients = Patient.objects.count()

        # Average confidence
        avg_confidence = Prediction.objects.aggregate(
            Avg('consensus_confidence')
        )['consensus_confidence__avg']

        return {
            'total_predictions': total_predictions,
            'today_predictions': today_predictions,
            'covid_count': covid_count,
            'normal_count': normal_count,
            'total_patients': total_patients,
            'avg_confidence': round(avg_confidence, 2) if avg_confidence else 0,
        }
