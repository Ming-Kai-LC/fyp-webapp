"""
Unit Tests for PredictionService
Tests prediction workflow, permission checking, and data retrieval
"""

from django.test import TestCase
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from detection.models import Patient, XRayImage, Prediction
from detection.services import PredictionService, MLInferenceError
from unittest.mock import patch, MagicMock


class PredictionServiceTest(TestCase):
    """Test suite for PredictionService"""

    def setUp(self):
        """Set up test data"""
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='testpass123'
        )
        self.admin_user.profile.role = 'admin'
        self.admin_user.profile.save()

        # Create staff user
        self.staff_user = User.objects.create_user(
            username='staff_test',
            email='staff@test.com',
            password='testpass123'
        )
        self.staff_user.profile.role = 'staff'
        self.staff_user.profile.save()

        # Create patient user
        self.patient_user = User.objects.create_user(
            username='patient_test',
            email='patient@test.com',
            password='testpass123'
        )
        self.patient_user.profile.role = 'patient'
        self.patient_user.profile.save()

        # Create patient
        self.patient = Patient.objects.create(
            user=self.patient_user,
            date_of_birth='1980-01-01',
            gender='M',
            phone_number='+1234567890',
            address='123 Test St'
        )

        # Link patient to user
        self.patient_user.patient_info = self.patient
        self.patient_user.save()

    def create_test_image(self):
        """Helper: Create test image file"""
        return SimpleUploadedFile(
            "test_xray.jpg",
            b"x" * 1024,
            content_type="image/jpeg"
        )

    def create_test_prediction(self, patient=None):
        """Helper: Create test prediction"""
        if patient is None:
            patient = self.patient

        xray = XRayImage.objects.create(
            patient=patient,
            uploaded_by=self.staff_user,
            notes="Test X-ray"
        )

        prediction = Prediction.objects.create(
            xray=xray,
            crossvit_prediction="COVID",
            crossvit_confidence=95.5,
            resnet50_prediction="COVID",
            resnet50_confidence=94.0,
            densenet121_prediction="COVID",
            densenet121_confidence=96.0,
            efficientnet_prediction="COVID",
            efficientnet_confidence=93.5,
            vit_prediction="COVID",
            vit_confidence=95.0,
            swin_prediction="COVID",
            swin_confidence=94.5,
            final_diagnosis="COVID",
            consensus_confidence=94.9,
            inference_time=2.5
        )

        return prediction

    # ==================== Test _validate_prediction_request() ====================

    def test_validate_prediction_staff_user(self):
        """Test validation passes for staff user"""
        try:
            PredictionService._validate_prediction_request(
                self.patient,
                self.staff_user
            )
        except Exception as e:
            self.fail(f"Validation should pass for staff: {e}")

    def test_validate_prediction_admin_user(self):
        """Test validation passes for admin user"""
        try:
            PredictionService._validate_prediction_request(
                self.patient,
                self.admin_user
            )
        except Exception as e:
            self.fail(f"Validation should pass for admin: {e}")

    def test_validate_prediction_patient_user_fails(self):
        """Test validation fails for patient user"""
        with self.assertRaises(PermissionDenied) as context:
            PredictionService._validate_prediction_request(
                self.patient,
                self.patient_user
            )

        self.assertIn('Only staff', str(context.exception))

    def test_validate_prediction_no_patient(self):
        """Test validation fails without patient"""
        with self.assertRaises(ValidationError) as context:
            PredictionService._validate_prediction_request(
                None,
                self.staff_user
            )

        self.assertIn('Patient is required', str(context.exception))

    def test_validate_prediction_no_user(self):
        """Test validation fails without user"""
        with self.assertRaises(ValidationError) as context:
            PredictionService._validate_prediction_request(
                self.patient,
                None
            )

        self.assertIn('Uploaded by user is required', str(context.exception))

    # ==================== Test create_prediction_from_xray() ====================

    @patch('detection.services.prediction_service.XRayService.save_xray')
    @patch('detection.services.prediction_service.XRayService.apply_preprocessing')
    @patch('detection.services.prediction_service.PredictionService._run_ml_inference')
    @patch('detection.services.prediction_service.NotificationService.send_prediction_notification')
    def test_create_prediction_success(self, mock_notify, mock_ml, mock_preprocess, mock_save):
        """Test successful prediction creation workflow"""
        # Setup mocks
        mock_xray = MagicMock()
        mock_xray.id = 1
        mock_save.return_value = mock_xray

        mock_preprocess.return_value = "/path/to/processed.jpg"

        mock_ml.return_value = {
            'individual_results': {
                'crossvit': {'prediction': 'COVID', 'confidence': 95.0},
                'resnet50': {'prediction': 'COVID', 'confidence': 94.0},
                'densenet121': {'prediction': 'COVID', 'confidence': 96.0},
                'efficientnet': {'prediction': 'COVID', 'confidence': 93.0},
                'vit': {'prediction': 'COVID', 'confidence': 95.0},
                'swin': {'prediction': 'COVID', 'confidence': 94.0}
            },
            'consensus_diagnosis': 'COVID',
            'best_confidence': 96.0,
            'inference_time': 2.5,
            'model_agreement': 6
        }

        image = self.create_test_image()

        # Execute
        prediction = PredictionService.create_prediction_from_xray(
            xray_image_file=image,
            patient=self.patient,
            uploaded_by=self.staff_user,
            notes="Test prediction"
        )

        # Verify
        self.assertIsNotNone(prediction)
        self.assertEqual(prediction.final_diagnosis, 'COVID')
        self.assertEqual(prediction.consensus_confidence, 96.0)
        self.assertEqual(prediction.xray, mock_xray)

        # Verify service calls
        mock_save.assert_called_once()
        mock_preprocess.assert_called_once()
        mock_ml.assert_called_once()
        mock_notify.assert_called_once()

    @patch('detection.services.prediction_service.XRayService.save_xray')
    def test_create_prediction_permission_denied(self, mock_save):
        """Test prediction creation fails for patient user"""
        image = self.create_test_image()

        with self.assertRaises(PermissionDenied):
            PredictionService.create_prediction_from_xray(
                xray_image_file=image,
                patient=self.patient,
                uploaded_by=self.patient_user,  # Patient trying to upload
                notes=""
            )

        # save_xray should not be called
        mock_save.assert_not_called()

    # ==================== Test get_predictions_for_user() ====================

    def test_get_predictions_patient_sees_own_only(self):
        """Test that patients only see their own predictions"""
        # Create prediction for test patient
        prediction1 = self.create_test_prediction(self.patient)

        # Create another patient and prediction
        other_user = User.objects.create_user('other', 'other@test.com', 'pass')
        other_user.profile.role = 'patient'
        other_user.profile.save()

        other_patient = Patient.objects.create(
            user=other_user,
            date_of_birth='1990-01-01',
            gender='F'
        )
        other_user.patient_info = other_patient
        other_user.save()

        prediction2 = self.create_test_prediction(other_patient)

        # Patient should only see their own
        queryset = PredictionService.get_predictions_for_user(self.patient_user)

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, prediction1.id)

    def test_get_predictions_staff_sees_all(self):
        """Test that staff see all predictions"""
        prediction1 = self.create_test_prediction()

        # Create another patient and prediction
        other_user = User.objects.create_user('other', 'other@test.com', 'pass')
        other_patient = Patient.objects.create(
            user=other_user,
            date_of_birth='1990-01-01',
            gender='F'
        )
        prediction2 = self.create_test_prediction(other_patient)

        # Staff should see all
        queryset = PredictionService.get_predictions_for_user(self.staff_user)

        self.assertEqual(queryset.count(), 2)

    def test_get_predictions_admin_sees_all(self):
        """Test that admin sees all predictions"""
        prediction1 = self.create_test_prediction()

        # Admin should see all
        queryset = PredictionService.get_predictions_for_user(self.admin_user)

        self.assertGreaterEqual(queryset.count(), 1)

    def test_get_predictions_with_diagnosis_filter(self):
        """Test filtering by diagnosis"""
        # Create COVID prediction
        covid_pred = self.create_test_prediction()

        # Create Normal prediction
        xray2 = XRayImage.objects.create(
            patient=self.patient,
            uploaded_by=self.staff_user,
            notes="Test"
        )
        normal_pred = Prediction.objects.create(
            xray=xray2,
            final_diagnosis="Normal",
            consensus_confidence=95.0,
            crossvit_prediction="Normal",
            crossvit_confidence=95.0,
            resnet50_prediction="Normal",
            resnet50_confidence=94.0,
            densenet121_prediction="Normal",
            densenet121_confidence=96.0,
            efficientnet_prediction="Normal",
            efficientnet_confidence=93.0,
            vit_prediction="Normal",
            vit_confidence=95.0,
            swin_prediction="Normal",
            swin_confidence=94.0,
            inference_time=2.0
        )

        # Filter for COVID only
        queryset = PredictionService.get_predictions_for_user(
            self.staff_user,
            filters={'diagnosis': 'COVID'}
        )

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().final_diagnosis, 'COVID')

    def test_get_predictions_optimized_query(self):
        """Test that queryset uses select_related for optimization"""
        prediction = self.create_test_prediction()

        # This should use select_related to prevent N+1 queries
        with self.assertNumQueries(1):
            queryset = PredictionService.get_predictions_for_user(self.staff_user)
            # Access related fields
            for pred in queryset:
                _ = pred.xray.patient.user.username
                _ = pred.xray.uploaded_by.username

    # ==================== Test get_prediction_results() ====================

    def test_get_prediction_results_success(self):
        """Test retrieving prediction results"""
        prediction = self.create_test_prediction()

        result = PredictionService.get_prediction_results(
            prediction_id=prediction.id,
            requesting_user=self.staff_user
        )

        self.assertIsNotNone(result)
        self.assertIn('prediction', result)
        self.assertIn('model_results', result)
        self.assertIn('best_model_name', result)
        self.assertIn('agreement_count', result)
        self.assertEqual(result['prediction'].id, prediction.id)

    def test_get_prediction_results_patient_own_prediction(self):
        """Test patient can view their own prediction"""
        prediction = self.create_test_prediction(self.patient)

        result = PredictionService.get_prediction_results(
            prediction_id=prediction.id,
            requesting_user=self.patient_user
        )

        self.assertIsNotNone(result)
        self.assertEqual(result['prediction'].id, prediction.id)

    def test_get_prediction_results_patient_other_prediction_denied(self):
        """Test patient cannot view other patient's prediction"""
        # Create another patient and prediction
        other_user = User.objects.create_user('other', 'other@test.com', 'pass')
        other_user.profile.role = 'patient'
        other_user.profile.save()

        other_patient = Patient.objects.create(
            user=other_user,
            date_of_birth='1990-01-01',
            gender='F'
        )

        prediction = self.create_test_prediction(other_patient)

        with self.assertRaises(PermissionDenied):
            PredictionService.get_prediction_results(
                prediction_id=prediction.id,
                requesting_user=self.patient_user  # Different patient
            )

    # ==================== Test get_pending_validations() ====================

    def test_get_pending_validations(self):
        """Test retrieving pending validations"""
        # Create validated prediction
        pred1 = self.create_test_prediction()
        pred1.is_validated = True
        pred1.save()

        # Create unvalidated prediction
        pred2 = self.create_test_prediction()
        pred2.is_validated = False
        pred2.save()

        pending = PredictionService.get_pending_validations()

        self.assertEqual(pending.count(), 1)
        self.assertEqual(pending.first().id, pred2.id)
        self.assertFalse(pending.first().is_validated)

    def test_get_pending_validations_limit(self):
        """Test limit parameter works"""
        # Create 15 unvalidated predictions
        for i in range(15):
            pred = self.create_test_prediction()
            pred.is_validated = False
            pred.save()

        # Request only 5
        pending = PredictionService.get_pending_validations(limit=5)

        self.assertEqual(pending.count(), 5)

    # ==================== Test get_recent_predictions() ====================

    def test_get_recent_predictions(self):
        """Test retrieving recent predictions"""
        # Create predictions
        pred1 = self.create_test_prediction()
        pred2 = self.create_test_prediction()

        recent = PredictionService.get_recent_predictions(limit=10)

        self.assertGreaterEqual(recent.count(), 2)
        # Should be ordered by created_at descending
        self.assertEqual(recent[0].id, pred2.id)

    def test_get_recent_predictions_limit(self):
        """Test limit parameter works"""
        # Create 15 predictions
        for i in range(15):
            self.create_test_prediction()

        # Request only 5
        recent = PredictionService.get_recent_predictions(limit=5)

        self.assertEqual(recent.count(), 5)
