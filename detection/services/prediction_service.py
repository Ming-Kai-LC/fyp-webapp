"""
Prediction Service
Handles COVID-19 prediction workflow orchestration
"""

from typing import Optional, Dict, Any
from django.core.exceptions import ValidationError, PermissionDenied
from django.contrib.auth.models import User
from django.db.models import QuerySet
from detection.models import Prediction, Patient, XRayImage
from .xray_service import XRayService
from notifications.services import NotificationService
import logging

try:
    from detection.ml_engine import model_ensemble
except ImportError:
    from detection.ml_engine_stub import model_ensemble

logger = logging.getLogger(__name__)


class MLInferenceError(Exception):
    """Exception raised when ML inference fails"""
    pass


class PredictionService:
    """
    Core service for COVID-19 prediction workflow orchestration

    This service encapsulates the multi-step prediction process:
    1. Validate inputs and permissions
    2. Save X-ray image
    3. Apply preprocessing (CLAHE)
    4. Run 6 ML models
    5. Calculate consensus diagnosis
    6. Save prediction with all model results
    7. Send notification to patient
    """

    @staticmethod
    def create_prediction_from_xray(
        xray_image_file,
        patient: Patient,
        uploaded_by: User,
        notes: str = ""
    ) -> Prediction:
        """
        Complete prediction pipeline from uploaded X-ray image

        Args:
            xray_image_file: Django UploadedFile instance
            patient: Patient instance
            uploaded_by: User who uploaded the image (staff)
            notes: Optional clinical notes

        Returns:
            Prediction instance with all model results

        Raises:
            ValidationError: If validation fails
            MLInferenceError: If ML prediction fails
            PermissionDenied: If user doesn't have permission

        Example:
            >>> prediction = PredictionService.create_prediction_from_xray(
            ...     xray_image_file=request.FILES['image'],
            ...     patient=patient,
            ...     uploaded_by=request.user,
            ...     notes="Patient reports cough and fever"
            ... )
            >>> print(prediction.final_diagnosis)
            'COVID'
        """
        try:
            # Step 1: Validate inputs and permissions
            PredictionService._validate_prediction_request(patient, uploaded_by)

            # Step 2: Save X-ray image
            logger.info(f"Saving X-ray for patient {patient.user.username}")
            xray = XRayService.save_xray(
                image_file=xray_image_file,
                patient=patient,
                uploaded_by=uploaded_by,
                notes=notes
            )

            # Step 3: Apply preprocessing
            logger.info("Applying CLAHE preprocessing...")
            processed_path = XRayService.apply_preprocessing(xray)

            # Step 4: Run ML models
            logger.info("Running multi-model prediction ensemble...")
            ml_results = PredictionService._run_ml_inference(processed_path)

            # Step 5: Save prediction
            logger.info("Saving prediction results...")
            prediction = PredictionService._save_prediction(xray, ml_results)

            # Step 6: Send notification (don't fail workflow if notification fails)
            logger.info("Sending notification to patient...")
            try:
                NotificationService.send_prediction_notification(prediction)
                logger.info(f"Notification sent for prediction ID={prediction.id}")
            except Exception as e:
                logger.error(f"Failed to send notification: {e}")
                # Continue workflow even if notification fails

            logger.info(
                f" Prediction completed: ID={prediction.id}, "
                f"Diagnosis={prediction.final_diagnosis}, "
                f"Confidence={prediction.consensus_confidence:.1f}%"
            )

            return prediction

        except (ValidationError, PermissionDenied, MLInferenceError):
            # Re-raise expected exceptions
            raise
        except Exception as e:
            logger.error(f"Prediction workflow failed: {e}", exc_info=True)
            raise ValidationError(f"Prediction workflow failed: {str(e)}")

    @staticmethod
    def _validate_prediction_request(patient: Patient, uploaded_by: User):
        """
        Validate prediction request inputs and permissions

        Args:
            patient: Patient instance
            uploaded_by: User uploading the X-ray

        Raises:
            ValidationError: If validation fails
            PermissionDenied: If user doesn't have permission
        """
        if not patient:
            raise ValidationError("Patient is required")

        if not uploaded_by:
            raise ValidationError("Uploaded by user is required")

        if not hasattr(uploaded_by, 'profile'):
            raise ValidationError("User profile not found")

        # Only staff and admin can upload X-rays for predictions
        if not uploaded_by.profile.is_staff() and not uploaded_by.profile.is_admin():
            raise PermissionDenied("Only staff members can upload X-rays for predictions")

    @staticmethod
    def _run_ml_inference(processed_image_path: str) -> Dict[str, Any]:
        """
        Run ML model inference on preprocessed image

        Args:
            processed_image_path: Absolute path to preprocessed image

        Returns:
            Dictionary with structure:
            {
                'individual_results': {
                    'crossvit': {'prediction': str, 'confidence': float},
                    'resnet50': {...},
                    'densenet121': {...},
                    'efficientnet': {...},
                    'vit': {...},
                    'swin': {...}
                },
                'consensus_diagnosis': str,
                'best_confidence': float,
                'inference_time': float,
                'model_agreement': int
            }

        Raises:
            MLInferenceError: If ML inference fails
        """
        if model_ensemble is None:
            raise MLInferenceError("ML Engine not initialized. Please contact administrator.")

        try:
            logger.info(f"Running ensemble inference on: {processed_image_path}")
            results = model_ensemble.predict_all_models(processed_image_path)

            if not results or 'individual_results' not in results:
                raise MLInferenceError("Invalid ML results format")

            return results

        except Exception as e:
            logger.error(f"ML inference failed: {e}", exc_info=True)
            raise MLInferenceError(f"ML inference failed: {str(e)}")

    @staticmethod
    def _save_prediction(xray: XRayImage, ml_results: Dict[str, Any]) -> Prediction:
        """
        Save prediction with all 6 model results

        Args:
            xray: XRayImage instance
            ml_results: Dictionary with ML results from all models

        Returns:
            Saved Prediction instance
        """
        individual = ml_results['individual_results']

        prediction = Prediction.objects.create(
            xray=xray,
            # CrossViT
            crossvit_prediction=individual['crossvit']['prediction'],
            crossvit_confidence=individual['crossvit']['confidence'],
            # ResNet-50
            resnet50_prediction=individual['resnet50']['prediction'],
            resnet50_confidence=individual['resnet50']['confidence'],
            # DenseNet-121
            densenet121_prediction=individual['densenet121']['prediction'],
            densenet121_confidence=individual['densenet121']['confidence'],
            # EfficientNet-B0
            efficientnet_prediction=individual['efficientnet']['prediction'],
            efficientnet_confidence=individual['efficientnet']['confidence'],
            # ViT-Base
            vit_prediction=individual['vit']['prediction'],
            vit_confidence=individual['vit']['confidence'],
            # Swin-Tiny
            swin_prediction=individual['swin']['prediction'],
            swin_confidence=individual['swin']['confidence'],
            # Consensus
            final_diagnosis=ml_results['consensus_diagnosis'],
            consensus_confidence=ml_results['best_confidence'],
            inference_time=ml_results['inference_time'],
        )

        logger.info(f"Prediction saved: ID={prediction.id}")
        return prediction

    @staticmethod
    def get_predictions_for_user(
        user: User,
        filters: Optional[Dict[str, Any]] = None
    ) -> QuerySet:
        """
        Get predictions filtered by user permissions

        Args:
            user: Requesting user
            filters: Optional filters (diagnosis, date_range, etc.)

        Returns:
            QuerySet of Prediction objects

        Example:
            >>> # Get predictions for a patient (only their own)
            >>> predictions = PredictionService.get_predictions_for_user(
            ...     user=patient_user,
            ...     filters={'diagnosis': 'COVID'}
            ... )
            >>>
            >>> # Get all predictions for staff
            >>> predictions = PredictionService.get_predictions_for_user(
            ...     user=staff_user
            ... )
        """
        # Role-based filtering
        if user.profile.is_patient():
            if hasattr(user, 'patient_info'):
                queryset = Prediction.objects.filter(
                    xray__patient=user.patient_info
                )
            else:
                # Patient has no patient_info - return empty queryset
                queryset = Prediction.objects.none()
        else:
            # Staff and admin see all predictions
            queryset = Prediction.objects.all()

        # Apply filters if provided
        if filters:
            if filters.get('diagnosis'):
                queryset = queryset.filter(final_diagnosis=filters['diagnosis'])

            if filters.get('date_from'):
                queryset = queryset.filter(created_at__gte=filters['date_from'])

            if filters.get('date_to'):
                queryset = queryset.filter(created_at__lte=filters['date_to'])

            if filters.get('is_validated') is not None:
                queryset = queryset.filter(is_validated=filters['is_validated'])

        # Optimize query with select_related
        queryset = queryset.select_related(
            'xray__patient__user',
            'xray__uploaded_by'
        ).order_by('-created_at')

        return queryset

    @staticmethod
    def get_prediction_results(
        prediction_id: int,
        requesting_user: User
    ) -> Dict[str, Any]:
        """
        Get prediction results with permission checking and data preparation

        Args:
            prediction_id: Prediction ID
            requesting_user: User requesting the data

        Returns:
            Dictionary ready for template rendering with keys:
            - prediction: Prediction instance
            - model_results: List of model results sorted by confidence
            - best_model_name: Name of best performing model
            - best_confidence: Highest confidence score
            - agreement_count: Number of models in agreement
            - has_explainability: Whether explainability data exists

        Raises:
            Prediction.DoesNotExist: If prediction not found
            PermissionDenied: If user doesn't have access
        """
        try:
            prediction = Prediction.objects.select_related(
                'xray__patient__user'
            ).get(id=prediction_id)
        except Prediction.DoesNotExist:
            raise

        # Permission check
        if requesting_user.profile.is_patient():
            if prediction.xray.patient.user != requesting_user:
                raise PermissionDenied("Cannot view other patients' results")

        # Prepare data for template
        model_results = prediction.get_all_predictions()
        model_results_sorted = sorted(
            model_results,
            key=lambda x: x["confidence"],
            reverse=True
        )

        best_model_name, best_confidence = prediction.get_best_model()
        agreement_count = prediction.get_model_agreement()

        return {
            "prediction": prediction,
            "model_results": model_results_sorted,
            "best_model_name": best_model_name,
            "best_confidence": best_confidence,
            "agreement_count": agreement_count,
            "has_explainability": bool(prediction.gradcam_heatmap),
        }

    @staticmethod
    def get_pending_validations(limit: int = 10) -> QuerySet:
        """
        Get predictions pending validation

        Args:
            limit: Maximum number of predictions to return

        Returns:
            QuerySet of unvalidated predictions
        """
        return Prediction.objects.filter(
            is_validated=False
        ).select_related(
            'xray__patient__user'
        ).order_by('-created_at')[:limit]

    @staticmethod
    def get_recent_predictions(limit: int = 10) -> QuerySet:
        """
        Get recent predictions

        Args:
            limit: Maximum number of predictions to return

        Returns:
            QuerySet of recent predictions
        """
        return Prediction.objects.select_related(
            'xray__patient__user',
            'xray__uploaded_by'
        ).order_by('-created_at')[:limit]
