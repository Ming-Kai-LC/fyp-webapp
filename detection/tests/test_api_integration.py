"""
API Integration Tests
Tests API endpoints using service layer
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from detection.models import Patient, XRayImage, Prediction
from unittest.mock import patch, MagicMock


class PredictionAPIIntegrationTest(TestCase):
    """Test API endpoints integrate correctly with service layer"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        self.admin_user.profile.role = 'admin'
        self.admin_user.profile.save()

        # Create staff user
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@test.com',
            password='testpass123'
        )
        self.staff_user.profile.role = 'staff'
        self.staff_user.profile.save()

        # Create patient user
        self.patient_user = User.objects.create_user(
            username='patient',
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
            crossvit_confidence=95.0,
            resnet50_prediction="COVID",
            resnet50_confidence=94.0,
            densenet121_prediction="COVID",
            densenet121_confidence=96.0,
            efficientnet_prediction="COVID",
            efficientnet_confidence=93.0,
            vit_prediction="COVID",
            vit_confidence=95.0,
            swin_prediction="COVID",
            swin_confidence=94.0,
            final_diagnosis="COVID",
            consensus_confidence=94.5,
            inference_time=2.0
        )

        return prediction

    # ==================== Test GET /api/predictions/ ====================

    def test_list_predictions_staff_sees_all(self):
        """Test that staff can list all predictions"""
        # Create predictions
        pred1 = self.create_test_prediction()

        # Authenticate as staff
        self.client.force_authenticate(user=self.staff_user)

        # Make request
        response = self.client.get('/api/predictions/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_list_predictions_patient_sees_own_only(self):
        """Test that patients only see their own predictions"""
        # Create prediction for test patient
        pred1 = self.create_test_prediction(self.patient)

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

        pred2 = self.create_test_prediction(other_patient)

        # Authenticate as test patient
        self.client.force_authenticate(user=self.patient_user)

        # Make request
        response = self.client.get('/api/predictions/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], pred1.id)

    def test_list_predictions_unauthenticated(self):
        """Test that unauthenticated users cannot list predictions"""
        response = self.client.get('/api/predictions/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ==================== Test POST /api/predictions/upload/ ====================

    @patch('api.views.PredictionService.create_prediction_from_xray')
    def test_upload_xray_staff_success(self, mock_create):
        """Test successful X-ray upload by staff"""
        # Setup mock
        mock_prediction = self.create_test_prediction()
        mock_create.return_value = mock_prediction

        # Authenticate as staff
        self.client.force_authenticate(user=self.staff_user)

        # Prepare data
        image = self.create_test_image()
        data = {
            'patient_id': self.patient.id,
            'image': image,
            'notes': 'Test upload'
        }

        # Make request
        response = self.client.post('/api/predictions/upload/', data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('prediction', response.data)
        self.assertEqual(response.data['prediction']['id'], mock_prediction.id)

        # Verify service was called
        mock_create.assert_called_once()

    def test_upload_xray_patient_denied(self):
        """Test that patients cannot upload X-rays"""
        # Authenticate as patient
        self.client.force_authenticate(user=self.patient_user)

        # Prepare data
        image = self.create_test_image()
        data = {
            'patient_id': self.patient.id,
            'image': image,
            'notes': 'Test upload'
        }

        # Make request
        response = self.client.post('/api/predictions/upload/', data, format='multipart')

        # Should be forbidden (IsStaffOrAdmin permission)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_upload_xray_unauthenticated_denied(self):
        """Test that unauthenticated users cannot upload"""
        image = self.create_test_image()
        data = {
            'patient_id': self.patient.id,
            'image': image
        }

        response = self.client.post('/api/predictions/upload/', data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_upload_xray_missing_image(self):
        """Test upload fails without image"""
        # Authenticate as staff
        self.client.force_authenticate(user=self.staff_user)

        # Data without image
        data = {
            'patient_id': self.patient.id,
            'notes': 'Test upload'
        }

        response = self.client.post('/api/predictions/upload/', data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_upload_xray_invalid_patient(self):
        """Test upload fails with invalid patient ID"""
        # Authenticate as staff
        self.client.force_authenticate(user=self.staff_user)

        image = self.create_test_image()
        data = {
            'patient_id': 99999,  # Non-existent
            'image': image
        }

        response = self.client.post('/api/predictions/upload/', data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)

    # ==================== Test GET /api/predictions/{id}/ ====================

    def test_retrieve_prediction_staff(self):
        """Test staff can retrieve any prediction"""
        prediction = self.create_test_prediction()

        self.client.force_authenticate(user=self.staff_user)

        response = self.client.get(f'/api/predictions/{prediction.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], prediction.id)

    def test_retrieve_prediction_patient_own(self):
        """Test patient can retrieve their own prediction"""
        prediction = self.create_test_prediction(self.patient)

        self.client.force_authenticate(user=self.patient_user)

        response = self.client.get(f'/api/predictions/{prediction.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], prediction.id)

    def test_retrieve_prediction_patient_other_denied(self):
        """Test patient cannot retrieve other patient's prediction"""
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

        # Try to retrieve as test patient
        self.client.force_authenticate(user=self.patient_user)

        response = self.client.get(f'/api/predictions/{prediction.id}/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ==================== Test GET /api/predictions/{id}/explain/ ====================

    def test_explain_prediction(self):
        """Test getting explainability data"""
        prediction = self.create_test_prediction()

        self.client.force_authenticate(user=self.staff_user)

        response = self.client.get(f'/api/predictions/{prediction.id}/explain/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('gradcam_heatmap', response.data)
        self.assertIn('large_branch_attention', response.data)
        self.assertIn('small_branch_attention', response.data)

    # ==================== Test PATCH /api/predictions/{id}/validate/ ====================

    def test_validate_prediction_staff(self):
        """Test staff can validate predictions"""
        prediction = self.create_test_prediction()

        self.client.force_authenticate(user=self.staff_user)

        data = {'doctor_notes': 'Confirmed COVID-19'}

        response = self.client.patch(f'/api/predictions/{prediction.id}/validate/', data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

        # Verify prediction was validated
        prediction.refresh_from_db()
        self.assertTrue(prediction.is_validated)
        self.assertEqual(prediction.doctor_notes, 'Confirmed COVID-19')

    def test_validate_prediction_patient_denied(self):
        """Test patients cannot validate predictions"""
        prediction = self.create_test_prediction()

        self.client.force_authenticate(user=self.patient_user)

        data = {'doctor_notes': 'Test'}

        response = self.client.patch(f'/api/predictions/{prediction.id}/validate/', data)

        # Should be forbidden (IsStaffOrAdmin permission)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ==================== Test Service Integration ====================

    @patch('api.views.PredictionService.get_predictions_for_user')
    def test_api_uses_prediction_service(self, mock_get_predictions):
        """Test that API actually uses PredictionService"""
        # Setup mock
        mock_get_predictions.return_value = Prediction.objects.none()

        # Authenticate and make request
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get('/api/predictions/')

        # Verify service was called
        mock_get_predictions.assert_called_once_with(self.staff_user)

    def test_api_and_web_use_same_service(self):
        """Integration test: Verify API and web views produce same results"""
        # Create predictions
        pred1 = self.create_test_prediction(self.patient)

        # Get predictions via service (what web view uses)
        from detection.services import PredictionService
        service_results = list(PredictionService.get_predictions_for_user(self.patient_user))

        # Get predictions via API
        self.client.force_authenticate(user=self.patient_user)
        api_response = self.client.get('/api/predictions/')
        api_results_ids = [p['id'] for p in api_response.data]

        # Should match
        self.assertEqual(len(service_results), len(api_results_ids))
        self.assertIn(pred1.id, api_results_ids)
