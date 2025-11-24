"""
Unit Tests for StatisticsService
Tests dashboard statistics and data aggregation
"""

from django.test import TestCase
from django.contrib.auth.models import User
from detection.models import Patient, XRayImage, Prediction
from detection.services import StatisticsService


class StatisticsServiceTest(TestCase):
    """Test suite for StatisticsService"""

    def setUp(self):
        """Set up test data"""
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

    def create_test_prediction(self, diagnosis='COVID', is_validated=False):
        """Helper: Create test prediction"""
        xray = XRayImage.objects.create(
            patient=self.patient,
            uploaded_by=self.staff_user,
            notes="Test X-ray"
        )

        prediction = Prediction.objects.create(
            xray=xray,
            crossvit_prediction=diagnosis,
            crossvit_confidence=95.0,
            resnet50_prediction=diagnosis,
            resnet50_confidence=94.0,
            densenet121_prediction=diagnosis,
            densenet121_confidence=96.0,
            efficientnet_prediction=diagnosis,
            efficientnet_confidence=93.0,
            vit_prediction=diagnosis,
            vit_confidence=95.0,
            swin_prediction=diagnosis,
            swin_confidence=94.0,
            final_diagnosis=diagnosis,
            consensus_confidence=94.5,
            inference_time=2.0,
            is_validated=is_validated
        )

        return prediction

    # ==================== Test get_staff_dashboard_stats() ====================

    def test_get_staff_dashboard_stats_basic(self):
        """Test basic staff dashboard statistics"""
        # Create test data
        self.create_test_prediction('COVID')
        self.create_test_prediction('Normal')
        self.create_test_prediction('COVID', is_validated=False)

        stats = StatisticsService.get_staff_dashboard_stats(self.staff_user)

        self.assertIn('total_predictions', stats)
        self.assertIn('covid_cases', stats)
        self.assertIn('normal_cases', stats)
        self.assertIn('pending_validation', stats)
        self.assertIn('recent_predictions', stats)

        self.assertEqual(stats['total_predictions'], 3)
        self.assertEqual(stats['covid_cases'], 2)
        self.assertEqual(stats['normal_cases'], 1)
        self.assertEqual(stats['pending_validation'], 1)

    def test_get_staff_dashboard_stats_empty(self):
        """Test stats with no predictions"""
        stats = StatisticsService.get_staff_dashboard_stats(self.staff_user)

        self.assertEqual(stats['total_predictions'], 0)
        self.assertEqual(stats['covid_cases'], 0)
        self.assertEqual(stats['normal_cases'], 0)
        self.assertEqual(stats['pending_validation'], 0)
        self.assertEqual(len(stats['recent_predictions']), 0)

    def test_get_staff_dashboard_stats_recent_limit(self):
        """Test that recent predictions are limited to 10"""
        # Create 15 predictions
        for i in range(15):
            self.create_test_prediction('COVID')

        stats = StatisticsService.get_staff_dashboard_stats(self.staff_user)

        self.assertEqual(stats['total_predictions'], 15)
        self.assertEqual(len(stats['recent_predictions']), 10)  # Should be limited

    def test_get_staff_dashboard_stats_optimized_query(self):
        """Test that recent predictions query is optimized"""
        self.create_test_prediction('COVID')

        # Should use select_related to prevent N+1 queries
        with self.assertNumQueries(5):  # 5 separate counts + 1 optimized recent query
            stats = StatisticsService.get_staff_dashboard_stats(self.staff_user)
            # Access related fields
            for pred in stats['recent_predictions']:
                _ = pred.xray.patient.user.username

    # ==================== Test get_patient_dashboard_stats() ====================

    def test_get_patient_dashboard_stats_basic(self):
        """Test basic patient dashboard statistics"""
        # Create predictions for patient
        self.create_test_prediction('COVID')
        self.create_test_prediction('Normal')
        self.create_test_prediction('COVID')

        stats = StatisticsService.get_patient_dashboard_stats(self.patient)

        self.assertIn('total_xrays', stats)
        self.assertIn('covid_positive', stats)
        self.assertIn('normal_results', stats)
        self.assertIn('latest_prediction', stats)

        self.assertEqual(stats['total_xrays'], 3)
        self.assertEqual(stats['covid_positive'], 2)
        self.assertEqual(stats['normal_results'], 1)
        self.assertIsNotNone(stats['latest_prediction'])

    def test_get_patient_dashboard_stats_empty(self):
        """Test patient stats with no predictions"""
        stats = StatisticsService.get_patient_dashboard_stats(self.patient)

        self.assertEqual(stats['total_xrays'], 0)
        self.assertEqual(stats['covid_positive'], 0)
        self.assertEqual(stats['normal_results'], 0)
        self.assertIsNone(stats['latest_prediction'])

    def test_get_patient_dashboard_stats_only_their_own(self):
        """Test patient stats only include their own predictions"""
        # Create predictions for test patient
        self.create_test_prediction('COVID')

        # Create another patient with predictions
        other_user = User.objects.create_user('other', 'other@test.com', 'pass')
        other_patient = Patient.objects.create(
            user=other_user,
            date_of_birth='1990-01-01',
            gender='F'
        )

        # Create prediction for other patient
        xray = XRayImage.objects.create(
            patient=other_patient,
            uploaded_by=self.staff_user
        )
        Prediction.objects.create(
            xray=xray,
            final_diagnosis='COVID',
            consensus_confidence=95.0,
            crossvit_prediction='COVID',
            crossvit_confidence=95.0,
            resnet50_prediction='COVID',
            resnet50_confidence=94.0,
            densenet121_prediction='COVID',
            densenet121_confidence=96.0,
            efficientnet_prediction='COVID',
            efficientnet_confidence=93.0,
            vit_prediction='COVID',
            vit_confidence=95.0,
            swin_prediction='COVID',
            swin_confidence=94.0,
            inference_time=2.0
        )

        # Test patient should only see their own
        stats = StatisticsService.get_patient_dashboard_stats(self.patient)
        self.assertEqual(stats['total_xrays'], 1)

    # ==================== Test get_global_statistics() ====================

    def test_get_global_statistics_basic(self):
        """Test global statistics"""
        # Create test data
        self.create_test_prediction('COVID', is_validated=True)
        self.create_test_prediction('Normal', is_validated=False)

        stats = StatisticsService.get_global_statistics()

        self.assertIn('total_predictions', stats)
        self.assertIn('total_patients', stats)
        self.assertIn('total_xrays', stats)
        self.assertIn('validated_predictions', stats)
        self.assertIn('unvalidated_predictions', stats)
        self.assertIn('predictions_by_diagnosis', stats)

        self.assertEqual(stats['total_predictions'], 2)
        self.assertEqual(stats['total_patients'], 1)
        self.assertEqual(stats['total_xrays'], 2)
        self.assertEqual(stats['validated_predictions'], 1)
        self.assertEqual(stats['unvalidated_predictions'], 1)

    def test_get_global_statistics_empty(self):
        """Test global stats with no data"""
        stats = StatisticsService.get_global_statistics()

        self.assertEqual(stats['total_predictions'], 0)
        self.assertEqual(stats['total_xrays'], 0)
        self.assertEqual(stats['validated_predictions'], 0)

    # ==================== Test get_diagnosis_breakdown() ====================

    def test_get_diagnosis_breakdown(self):
        """Test diagnosis breakdown"""
        # Create predictions with different diagnoses
        self.create_test_prediction('COVID')
        self.create_test_prediction('COVID')
        self.create_test_prediction('Normal')
        self.create_test_prediction('Viral Pneumonia')

        breakdown = StatisticsService.get_diagnosis_breakdown()

        self.assertIsInstance(breakdown, dict)
        self.assertEqual(breakdown['COVID'], 2)
        self.assertEqual(breakdown['Normal'], 1)
        self.assertEqual(breakdown['Viral Pneumonia'], 1)

    def test_get_diagnosis_breakdown_empty(self):
        """Test diagnosis breakdown with no data"""
        breakdown = StatisticsService.get_diagnosis_breakdown()

        self.assertIsInstance(breakdown, dict)
        self.assertEqual(len(breakdown), 0)

    # ==================== Test get_model_performance_stats() ====================

    def test_get_model_performance_stats(self):
        """Test model performance statistics"""
        # Create predictions
        self.create_test_prediction('COVID')
        self.create_test_prediction('Normal')

        stats = StatisticsService.get_model_performance_stats()

        self.assertIn('crossvit', stats)
        self.assertIn('resnet50', stats)
        self.assertIn('densenet121', stats)
        self.assertIn('efficientnet', stats)
        self.assertIn('vit', stats)
        self.assertIn('swin', stats)

        # Check structure
        for model_name in ['crossvit', 'resnet50', 'densenet121', 'efficientnet', 'vit', 'swin']:
            self.assertIn('covid_count', stats[model_name])
            self.assertIn('covid_percentage', stats[model_name])

        # With 2 total predictions and 1 COVID, should be 50%
        self.assertEqual(stats['crossvit']['covid_count'], 1)
        self.assertEqual(stats['crossvit']['covid_percentage'], 50.0)

    def test_get_model_performance_stats_empty(self):
        """Test model performance stats with no data"""
        stats = StatisticsService.get_model_performance_stats()

        # Should return structure with zeros
        for model_name in ['crossvit', 'resnet50', 'densenet121', 'efficientnet', 'vit', 'swin']:
            self.assertEqual(stats[model_name]['covid_count'], 0)
            self.assertEqual(stats[model_name]['covid_percentage'], 0)

    def test_get_model_performance_stats_all_covid(self):
        """Test model performance with all COVID predictions"""
        # Create 5 COVID predictions
        for i in range(5):
            self.create_test_prediction('COVID')

        stats = StatisticsService.get_model_performance_stats()

        # All models should show 100% COVID
        for model_name in ['crossvit', 'resnet50', 'densenet121', 'efficientnet', 'vit', 'swin']:
            self.assertEqual(stats[model_name]['covid_count'], 5)
            self.assertEqual(stats[model_name]['covid_percentage'], 100.0)
