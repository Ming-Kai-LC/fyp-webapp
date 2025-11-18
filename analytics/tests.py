# analytics/tests.py
"""
Comprehensive tests for Analytics module
Tests models, services, views, and API endpoints
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal

from .models import (
    AnalyticsSnapshot,
    ModelPerformanceMetric,
    CustomReport,
    DataExport
)
from .services import AnalyticsEngine
from detection.models import Patient, XRayImage, Prediction, UserProfile


class AnalyticsSnapshotModelTest(TestCase):
    """Test AnalyticsSnapshot model"""

    def setUp(self):
        """Set up test data"""
        self.snapshot = AnalyticsSnapshot.objects.create(
            period_type='daily',
            snapshot_date=timezone.now().date(),
            total_predictions=100,
            covid_positive=20,
            normal_cases=60,
            viral_pneumonia=10,
            lung_opacity=10,
            avg_inference_time=0.5,
            avg_confidence=85.5,
        )

    def test_snapshot_creation(self):
        """Test snapshot is created correctly"""
        self.assertEqual(self.snapshot.total_predictions, 100)
        self.assertEqual(self.snapshot.covid_positive, 20)
        self.assertEqual(self.snapshot.period_type, 'daily')

    def test_snapshot_str(self):
        """Test string representation"""
        self.assertIn('Daily Snapshot', str(self.snapshot))

    def test_unique_together_constraint(self):
        """Test unique constraint on period_type and snapshot_date"""
        with self.assertRaises(Exception):
            AnalyticsSnapshot.objects.create(
                period_type='daily',
                snapshot_date=self.snapshot.snapshot_date,
                total_predictions=50,
            )


class ModelPerformanceMetricModelTest(TestCase):
    """Test ModelPerformanceMetric model"""

    def setUp(self):
        """Set up test data"""
        self.metric = ModelPerformanceMetric.objects.create(
            model_name='crossvit',
            date=timezone.now().date(),
            total_predictions=100,
            avg_confidence=88.5,
            avg_inference_time=0.25,
            accuracy=92.0,
            precision=90.5,
            recall=91.2,
            f1_score=90.8,
        )

    def test_metric_creation(self):
        """Test metric is created correctly"""
        self.assertEqual(self.metric.model_name, 'crossvit')
        self.assertEqual(self.metric.total_predictions, 100)
        self.assertAlmostEqual(self.metric.avg_confidence, 88.5)

    def test_metric_str(self):
        """Test string representation"""
        self.assertIn('CrossViT', str(self.metric))


class CustomReportModelTest(TestCase):
    """Test CustomReport model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testdoctor',
            password='testpass123'
        )
        self.report = CustomReport.objects.create(
            name='Test Report',
            report_type='prediction_trends',
            description='Test description',
            filters={'days': 30},
            chart_type='line',
            created_by=self.user,
            is_public=False,
        )

    def test_report_creation(self):
        """Test report is created correctly"""
        self.assertEqual(self.report.name, 'Test Report')
        self.assertEqual(self.report.created_by, self.user)
        self.assertFalse(self.report.is_public)

    def test_report_str(self):
        """Test string representation"""
        self.assertEqual(str(self.report), 'Test Report')


class AnalyticsEngineTest(TestCase):
    """Test AnalyticsEngine service"""

    def setUp(self):
        """Set up test data"""
        # Create user and patient
        self.user = User.objects.create_user(
            username='testpatient',
            password='testpass123'
        )
        UserProfile.objects.filter(user=self.user).update(role='patient')

        self.patient = Patient.objects.create(
            user=self.user,
            age=35,
            gender='M'
        )

        # Create X-ray and prediction
        self.xray = XRayImage.objects.create(
            patient=self.patient,
            original_image='test.jpg',
        )

        self.prediction = Prediction.objects.create(
            xray=self.xray,
            crossvit_prediction='COVID',
            crossvit_confidence=92.5,
            resnet50_prediction='COVID',
            resnet50_confidence=88.0,
            densenet121_prediction='COVID',
            densenet121_confidence=90.0,
            efficientnet_prediction='COVID',
            efficientnet_confidence=89.5,
            vit_prediction='COVID',
            vit_confidence=91.0,
            swin_prediction='COVID',
            swin_confidence=87.5,
            final_diagnosis='COVID',
            consensus_confidence=89.75,
            inference_time=0.5,
        )

    def test_generate_daily_snapshot(self):
        """Test daily snapshot generation"""
        snapshot = AnalyticsEngine.generate_daily_snapshot(timezone.now().date())

        self.assertIsNotNone(snapshot)
        self.assertEqual(snapshot.period_type, 'daily')
        self.assertEqual(snapshot.total_predictions, 1)
        self.assertEqual(snapshot.covid_positive, 1)

    def test_get_trend_data(self):
        """Test trend data retrieval"""
        # Generate snapshot first
        AnalyticsEngine.generate_daily_snapshot(timezone.now().date())

        trend_data = AnalyticsEngine.get_trend_data(days=30)

        self.assertIn('dates', trend_data)
        self.assertIn('total_predictions', trend_data)
        self.assertIn('covid_cases', trend_data)

    def test_get_model_comparison(self):
        """Test model comparison"""
        comparison = AnalyticsEngine.get_model_comparison()

        self.assertIn('crossvit', comparison)
        self.assertIn('resnet50', comparison)
        self.assertEqual(comparison['crossvit']['total_predictions'], 1)

    def test_get_demographic_analysis(self):
        """Test demographic analysis"""
        analysis = AnalyticsEngine.get_demographic_analysis()

        self.assertIn('by_age_group', analysis)
        self.assertIn('by_gender', analysis)
        self.assertIn('by_diagnosis', analysis)

    def test_get_dashboard_summary(self):
        """Test dashboard summary"""
        summary = AnalyticsEngine.get_dashboard_summary()

        self.assertIn('total_predictions', summary)
        self.assertIn('covid_count', summary)
        self.assertEqual(summary['total_predictions'], 1)


class AnalyticsViewsTest(TestCase):
    """Test analytics views"""

    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testdoctor',
            password='testpass123'
        )
        UserProfile.objects.filter(user=self.user).update(role='doctor')
        self.client.login(username='testdoctor', password='testpass123')

    def test_analytics_dashboard_view(self):
        """Test analytics dashboard view"""
        response = self.client.get('/analytics/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/dashboard.html')

    def test_trend_analysis_view(self):
        """Test trend analysis view"""
        response = self.client.get('/analytics/trends/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/trends.html')

    def test_model_comparison_view(self):
        """Test model comparison view"""
        response = self.client.get('/analytics/models/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/model_comparison.html')

    def test_demographic_analysis_view(self):
        """Test demographic analysis view"""
        response = self.client.get('/analytics/demographics/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/demographics.html')

    def test_custom_reports_view(self):
        """Test custom reports view"""
        response = self.client.get('/analytics/reports/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/custom_reports.html')

    def test_create_custom_report_get(self):
        """Test create custom report GET"""
        response = self.client.get('/analytics/reports/create/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/create_custom_report.html')

    def test_create_custom_report_post(self):
        """Test create custom report POST"""
        data = {
            'name': 'Test Report',
            'report_type': 'prediction_trends',
            'description': 'Test description',
            'chart_type': 'line',
            'is_public': 'on',
        }
        response = self.client.post('/analytics/reports/create/', data)
        self.assertEqual(response.status_code, 302)  # Redirect after creation

        # Verify report was created
        report = CustomReport.objects.filter(name='Test Report').first()
        self.assertIsNotNone(report)
        self.assertEqual(report.created_by, self.user)

    def test_export_data_view(self):
        """Test export data view"""
        response = self.client.get('/analytics/export/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/export_data.html')

    def test_unauthorized_access(self):
        """Test unauthorized access redirects to login"""
        self.client.logout()
        response = self.client.get('/analytics/dashboard/')
        self.assertEqual(response.status_code, 302)  # Redirect to login


class ManagementCommandTest(TestCase):
    """Test management commands"""

    def test_generate_snapshots_command(self):
        """Test generate_snapshots command"""
        from django.core.management import call_command
        from io import StringIO

        out = StringIO()
        call_command('generate_snapshots', '--period=daily', stdout=out)

        # Check that command executed without errors
        self.assertIn('snapshot', out.getvalue().lower())


class APIEndpointsTest(TestCase):
    """Test API endpoints"""

    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

        # Create snapshot
        self.snapshot = AnalyticsSnapshot.objects.create(
            period_type='daily',
            snapshot_date=timezone.now().date(),
            total_predictions=100,
            covid_positive=20,
            avg_confidence=85.0,
        )

    def test_snapshot_api(self):
        """Test snapshot API endpoint"""
        date_str = timezone.now().date().isoformat()
        response = self.client.get(f'/analytics/api/snapshot/{date_str}/')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['total_predictions'], 100)
        self.assertEqual(data['covid_positive'], 20)

    def test_trends_api(self):
        """Test trends API endpoint"""
        response = self.client.get('/analytics/api/trends/30/')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('dates', data)
        self.assertIn('total_predictions', data)
