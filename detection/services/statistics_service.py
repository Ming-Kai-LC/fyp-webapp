"""
Statistics Service
Handles dashboard statistics and data aggregation
"""

from typing import Dict, Any
from django.contrib.auth.models import User
from django.db.models import Count, Q
from detection.models import Prediction, Patient, XRayImage
import logging

logger = logging.getLogger(__name__)


class StatisticsService:
    """
    Service for dashboard statistics aggregation

    Responsibilities:
    - Calculate prediction statistics
    - Aggregate patient data
    - Provide dashboard metrics
    """

    @staticmethod
    def get_staff_dashboard_stats(user: User) -> Dict[str, Any]:
        """
        Get statistics for staff dashboard

        Args:
            user: Staff user

        Returns:
            Dictionary with statistics:
            - total_predictions: Total number of predictions
            - covid_cases: Number of COVID-positive cases
            - normal_cases: Number of normal cases
            - pending_validation: Number of unvalidated predictions
            - today_predictions: Predictions created today
            - recent_predictions: Last 10 predictions

        Example:
            >>> stats = StatisticsService.get_staff_dashboard_stats(staff_user)
            >>> print(stats['total_predictions'])
            150
        """
        # Basic counts
        total_predictions = Prediction.objects.count()
        covid_cases = Prediction.objects.filter(final_diagnosis="COVID").count()
        normal_cases = Prediction.objects.filter(final_diagnosis="Normal").count()
        pending_validation = Prediction.objects.filter(is_validated=False).count()

        # Recent predictions (optimized query)
        recent_predictions = Prediction.objects.select_related(
            'xray__patient__user'
        ).order_by('-created_at')[:10]

        logger.info(f"Staff dashboard stats calculated for user {user.username}")

        return {
            'total_predictions': total_predictions,
            'covid_cases': covid_cases,
            'normal_cases': normal_cases,
            'pending_validation': pending_validation,
            'recent_predictions': recent_predictions,
        }

    @staticmethod
    def get_patient_dashboard_stats(patient) -> Dict[str, Any]:
        """
        Get statistics for patient dashboard

        Args:
            patient: Patient instance

        Returns:
            Dictionary with patient-specific statistics
        """
        # Get predictions for this patient
        predictions = Prediction.objects.filter(xray__patient=patient)

        total_xrays = predictions.count()
        covid_positive = predictions.filter(final_diagnosis="COVID").count()
        normal_results = predictions.filter(final_diagnosis="Normal").count()

        # Most recent prediction
        latest_prediction = predictions.order_by('-created_at').first()

        return {
            'total_xrays': total_xrays,
            'covid_positive': covid_positive,
            'normal_results': normal_results,
            'latest_prediction': latest_prediction,
        }

    @staticmethod
    def get_global_statistics() -> Dict[str, Any]:
        """
        Get global system statistics (admin dashboard)

        Returns:
            Dictionary with global statistics
        """
        # Predictions
        total_predictions = Prediction.objects.count()
        predictions_by_diagnosis = Prediction.objects.values('final_diagnosis').annotate(
            count=Count('id')
        )

        # Patients
        total_patients = Patient.objects.count()

        # X-rays
        total_xrays = XRayImage.objects.count()

        # Validation stats
        validated_predictions = Prediction.objects.filter(is_validated=True).count()
        unvalidated_predictions = Prediction.objects.filter(is_validated=False).count()

        return {
            'total_predictions': total_predictions,
            'total_patients': total_patients,
            'total_xrays': total_xrays,
            'validated_predictions': validated_predictions,
            'unvalidated_predictions': unvalidated_predictions,
            'predictions_by_diagnosis': list(predictions_by_diagnosis),
        }

    @staticmethod
    def get_diagnosis_breakdown() -> Dict[str, int]:
        """
        Get breakdown of predictions by diagnosis

        Returns:
            Dictionary mapping diagnosis to count
        """
        diagnoses = Prediction.objects.values('final_diagnosis').annotate(
            count=Count('id')
        )

        return {d['final_diagnosis']: d['count'] for d in diagnoses}

    @staticmethod
    def get_model_performance_stats() -> Dict[str, Any]:
        """
        Get statistics about individual model performance

        Returns:
            Dictionary with model performance metrics
        """
        # Count predictions by each model
        crossvit_covid = Prediction.objects.filter(crossvit_prediction="COVID").count()
        resnet50_covid = Prediction.objects.filter(resnet50_prediction="COVID").count()
        densenet_covid = Prediction.objects.filter(densenet121_prediction="COVID").count()
        efficientnet_covid = Prediction.objects.filter(efficientnet_prediction="COVID").count()
        vit_covid = Prediction.objects.filter(vit_prediction="COVID").count()
        swin_covid = Prediction.objects.filter(swin_prediction="COVID").count()

        total = Prediction.objects.count()

        return {
            'crossvit': {
                'covid_count': crossvit_covid,
                'covid_percentage': (crossvit_covid / total * 100) if total > 0 else 0
            },
            'resnet50': {
                'covid_count': resnet50_covid,
                'covid_percentage': (resnet50_covid / total * 100) if total > 0 else 0
            },
            'densenet121': {
                'covid_count': densenet_covid,
                'covid_percentage': (densenet_covid / total * 100) if total > 0 else 0
            },
            'efficientnet': {
                'covid_count': efficientnet_covid,
                'covid_percentage': (efficientnet_covid / total * 100) if total > 0 else 0
            },
            'vit': {
                'covid_count': vit_covid,
                'covid_percentage': (vit_covid / total * 100) if total > 0 else 0
            },
            'swin': {
                'covid_count': swin_covid,
                'covid_percentage': (swin_covid / total * 100) if total > 0 else 0
            },
        }
