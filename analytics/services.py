"""
Analytics Module - Service Layer
TAR UMT Bachelor of Data Science FYP
Author: Tan Ming Kai (24PMR12003)
"""

from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from detection.models import Prediction, Patient, XRayImage
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

        # Count patients
        patients_today = Patient.objects.filter(
            created_at__date=date
        )

        snapshot = AnalyticsSnapshot.objects.create(
            period_type='daily',
            snapshot_date=date,
            total_predictions=predictions.count(),
            covid_positive=predictions.filter(final_diagnosis='COVID').count(),
            normal_cases=predictions.filter(final_diagnosis='Normal').count(),
            viral_pneumonia=predictions.filter(final_diagnosis='Viral Pneumonia').count(),
            lung_opacity=predictions.filter(final_diagnosis='Lung Opacity').count(),
            total_patients=Patient.objects.count(),
            new_patients=patients_today.count(),
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
            'dates': [s.snapshot_date.strftime('%Y-%m-%d') for s in snapshots],
            'total_predictions': [s.total_predictions for s in snapshots],
            'covid_cases': [s.covid_positive for s in snapshots],
            'normal_cases': [s.normal_cases for s in snapshots],
            'viral_pneumonia': [s.viral_pneumonia for s in snapshots],
            'lung_opacity': [s.lung_opacity for s in snapshots],
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

            # Count predictions by this model
            comparison[model] = {
                'avg_confidence': round(stats['avg_confidence'] or 0, 2),
                'total_predictions': stats['total'],
            }

        return comparison

    @staticmethod
    def get_demographic_analysis():
        """
        Analyze predictions by patient demographics
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

        # Gender
        gender_stats = Prediction.objects.values('xray__patient__gender').annotate(
            count=Count('id')
        )
        for item in gender_stats:
            gender = item['xray__patient__gender']
            if gender:
                analysis['by_gender'][gender] = item['count']

        # Diagnosis distribution
        diagnosis_stats = Prediction.objects.values('final_diagnosis').annotate(
            count=Count('id')
        )
        for item in diagnosis_stats:
            diagnosis = item['final_diagnosis']
            if diagnosis:
                analysis['by_diagnosis'][diagnosis] = item['count']

        return analysis

    @staticmethod
    def export_to_dataframe(filters=None):
        """
        Export data to pandas DataFrame for research
        """
        predictions = Prediction.objects.select_related('xray__patient__user').all()

        if filters:
            # Apply filters (implement as needed)
            if 'start_date' in filters and filters['start_date']:
                predictions = predictions.filter(
                    xray__upload_date__date__gte=filters['start_date']
                )
            if 'end_date' in filters and filters['end_date']:
                predictions = predictions.filter(
                    xray__upload_date__date__lte=filters['end_date']
                )
            if 'diagnosis' in filters and filters['diagnosis']:
                predictions = predictions.filter(
                    final_diagnosis=filters['diagnosis']
                )

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
    def get_doctor_productivity():
        """
        Analyze doctor productivity metrics
        """
        from django.contrib.auth.models import User
        from detection.models import UserProfile

        # Get all doctors
        doctor_profiles = UserProfile.objects.filter(role='doctor')
        productivity = []

        for profile in doctor_profiles:
            doctor = profile.user

            # Count reviews
            reviewed_count = Prediction.objects.filter(
                reviewed_by=doctor,
                is_validated=True
            ).count()

            # Count uploads
            uploaded_count = XRayImage.objects.filter(
                uploaded_by=doctor
            ).count()

            productivity.append({
                'doctor_name': doctor.get_full_name() or doctor.username,
                'doctor_id': doctor.id,
                'predictions_reviewed': reviewed_count,
                'xrays_uploaded': uploaded_count,
                'total_activities': reviewed_count + uploaded_count,
            })

        return sorted(productivity, key=lambda x: x['total_activities'], reverse=True)

    @staticmethod
    def get_dashboard_stats():
        """
        Get summary statistics for dashboard
        """
        total_predictions = Prediction.objects.count()
        total_patients = Patient.objects.count()
        total_xrays = XRayImage.objects.count()

        # Recent predictions (last 7 days)
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_predictions = Prediction.objects.filter(
            created_at__gte=seven_days_ago
        ).count()

        # COVID positive rate
        covid_count = Prediction.objects.filter(final_diagnosis='COVID').count()
        covid_rate = (covid_count / total_predictions * 100) if total_predictions > 0 else 0

        # Average confidence
        avg_confidence = Prediction.objects.aggregate(
            avg_conf=Avg('consensus_confidence')
        )['avg_conf'] or 0

        return {
            'total_predictions': total_predictions,
            'total_patients': total_patients,
            'total_xrays': total_xrays,
            'recent_predictions': recent_predictions,
            'covid_positive_count': covid_count,
            'covid_positive_rate': round(covid_rate, 2),
            'avg_confidence': round(avg_confidence, 2),
        }
