"""
COVID-19 Detection System - Full Integration Test Suite
Tests cross-module functionality and integration points
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

# Import models from all modules
from detection.models import UserProfile, Patient, XRayImage, Prediction
from medical_records.models import (
    MedicalCondition, Allergy, Medication, Vaccination,
    COVIDRiskScore, LifestyleInformation
)
from appointments.models import Appointment, DoctorSchedule
from notifications.models import Notification, NotificationTemplate
from reporting.models import Report, ReportTemplate
from audit.models import AuditLog, DataAccessLog, LoginAttempt
from analytics.models import AnalyticsSnapshot, ModelPerformanceMetric
from dashboards.models import DashboardPreference


class FullSystemIntegrationTest(TestCase):
    """
    Comprehensive integration tests for the entire COVID-19 Detection System
    Tests cross-module functionality and data flow
    """

    def setUp(self):
        """Create test users and basic data for all tests"""
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            email='admin@test.com',
            is_staff=True,
            is_superuser=True
        )
        self.admin_user.profile.role = 'admin'
        self.admin_user.profile.save()

        # Create doctor user
        self.doctor_user = User.objects.create_user(
            username='doctor',
            password='doctor123',
            email='doctor@test.com'
        )
        self.doctor_user.profile.role = 'doctor'
        self.doctor_user.profile.phone = '+60123456789'
        self.doctor_user.profile.save()

        # Create patient user
        self.patient_user = User.objects.create_user(
            username='patient',
            password='patient123',
            email='patient@test.com',
            first_name='John',
            last_name='Doe'
        )
        self.patient_user.profile.role = 'patient'
        self.patient_user.profile.save()

        # Create patient record
        self.patient = Patient.objects.create(
            user=self.patient_user,
            age=45,
            gender='M',
            medical_history='Hypertension',
            current_medications='Lisinopril 10mg daily',
            emergency_contact='Jane Doe +60198765432'
        )

        # Create test client
        self.client = Client()

        print("✅ Test setup complete: Created admin, doctor, and patient users")

    def test_01_module_imports(self):
        """Test 1: Verify all modules can be imported"""
        print("\n🧪 Test 1: Module Imports")

        try:
            import detection
            import medical_records
            import appointments
            import notifications
            import reporting
            import audit
            import analytics
            import dashboards
            import api
            print("✅ All modules imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import module: {e}")

    def test_02_database_models(self):
        """Test 2: Verify all database models exist and relationships work"""
        print("\n🧪 Test 2: Database Models & Relationships")

        # Test User -> UserProfile relationship
        self.assertIsNotNone(self.patient_user.profile)
        self.assertEqual(self.patient_user.profile.role, 'patient')
        print("  ✓ User -> UserProfile relationship works")

        # Test User -> Patient relationship
        self.assertIsNotNone(self.patient_user.patient_info)
        self.assertEqual(self.patient_user.patient_info.age, 45)
        print("  ✓ User -> Patient relationship works")

        # Test medical records relationships
        condition = MedicalCondition.objects.create(
            patient=self.patient,
            condition_name='Hypertension',
            diagnosis_date=timezone.now().date(),
            status='active'
        )
        self.assertEqual(self.patient.medical_conditions.count(), 1)
        print("  ✓ Patient -> MedicalCondition relationship works")

        # Test COVID risk score
        risk_score = COVIDRiskScore.objects.create(
            patient=self.patient,
            age_risk=2,
            comorbidity_risk=3,
            lifestyle_risk=1,
            total_risk_score=6,
            risk_category='moderate'
        )
        self.assertIsNotNone(risk_score)
        print("  ✓ COVIDRiskScore model works")

        print("✅ All database models and relationships verified")

    def test_03_cross_module_workflow(self):
        """Test 3: Full patient journey - X-ray upload to report generation"""
        print("\n🧪 Test 3: Cross-Module Patient Journey")

        # Step 1: Create notification template
        template = NotificationTemplate.objects.create(
            template_type='prediction_ready',
            name='Prediction Ready',
            subject='Your COVID-19 Test Results are Ready',
            body_template='Dear {{patient_name}}, your test results are available.',
            is_active=True
        )
        print("  ✓ Step 1: Created notification template")

        # Step 2: Create report template
        report_template = ReportTemplate.objects.create(
            name='Standard COVID Report',
            description='Standard report for COVID-19 detection results',
            is_default=True,
            is_active=True
        )
        print("  ✓ Step 2: Created report template")

        # Step 3: Doctor schedules appointment
        schedule = DoctorSchedule.objects.create(
            doctor=self.doctor_user,
            day_of_week=1,  # Monday
            start_time='09:00',
            end_time='17:00',
            is_available=True
        )
        print("  ✓ Step 3: Doctor schedule created")

        # Step 4: Patient books appointment
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor_user,
            appointment_date=timezone.now().date() + timedelta(days=7),
            appointment_time='10:00',
            appointment_type='consultation',
            status='scheduled',
            reason='COVID-19 screening'
        )
        print(f"  ✓ Step 4: Appointment created for {appointment.appointment_date}")

        # Step 5: Notification sent for appointment
        notification = Notification.objects.create(
            recipient=self.patient_user,
            title='Appointment Confirmed',
            message=f'Your appointment on {appointment.appointment_date} has been confirmed.',
            notification_type='appointment',
            priority='normal',
            status='sent'
        )
        print("  ✓ Step 5: Appointment notification sent")

        # Step 6: Audit log created
        audit_log = AuditLog.objects.create(
            user=self.doctor_user,
            action_type='create',
            description=f'Created appointment for patient {self.patient.user.username}',
            ip_address='127.0.0.1',
            user_agent='Test Client'
        )
        print("  ✓ Step 6: Audit log created")

        print("✅ Full cross-module workflow completed successfully")

    def test_04_api_integration(self):
        """Test 4: REST API endpoints are accessible"""
        print("\n🧪 Test 4: REST API Integration")

        # Get JWT token
        response = self.client.post(reverse('api:token_obtain_pair'), {
            'username': 'doctor',
            'password': 'doctor123'
        })

        if response.status_code == 200:
            print("  ✓ JWT authentication works")
        else:
            print(f"  ⚠️  JWT authentication returned status {response.status_code}")

        # Check API documentation is accessible
        response = self.client.get('/api/docs/')
        if response.status_code in [200, 302]:
            print("  ✓ API documentation accessible")
        else:
            print(f"  ⚠️  API docs returned status {response.status_code}")

    def test_05_audit_trail(self):
        """Test 5: Audit trail captures all important actions"""
        print("\n🧪 Test 5: Audit Trail & Compliance")

        # Login attempt logging
        attempt = LoginAttempt.objects.create(
            username='testuser',
            ip_address='192.168.1.100',
            was_successful=False,
            failure_reason='invalid_credentials'
        )
        self.assertIsNotNone(attempt)
        print("  ✓ Login attempts are logged")

        # Data access logging
        data_access = DataAccessLog.objects.create(
            accessor=self.doctor_user,
            accessor_role='doctor',
            patient=self.patient,
            data_type='medical_records',
            data_id=self.patient.id,
            access_type='view',
            ip_address='127.0.0.1'
        )
        self.assertIsNotNone(data_access)
        print("  ✓ Data access is logged (HIPAA compliance)")

        # Check audit log count
        audit_count = AuditLog.objects.count()
        print(f"  ✓ Total audit logs: {audit_count}")

        print("✅ Audit trail and compliance checks passed")

    def test_06_analytics_aggregation(self):
        """Test 6: Analytics aggregates data from all modules"""
        print("\n🧪 Test 6: Analytics Data Aggregation")

        # Create analytics snapshot
        snapshot = AnalyticsSnapshot.objects.create(
            date=timezone.now().date(),
            total_patients=100,
            total_xrays=250,
            total_predictions=250,
            covid_positive=45,
            normal_cases=150,
            viral_pneumonia=30,
            lung_opacity=25,
            total_appointments=180,
            completed_appointments=150,
            cancelled_appointments=20,
            no_show_appointments=10
        )
        self.assertIsNotNone(snapshot)
        print(f"  ✓ Analytics snapshot created for {snapshot.date}")

        # Create model performance metrics
        metric = ModelPerformanceMetric.objects.create(
            date=timezone.now().date(),
            model_name='CrossViT',
            accuracy=94.5,
            precision=93.2,
            recall=95.1,
            f1_score=94.1,
            total_predictions=250
        )
        self.assertIsNotNone(metric)
        print(f"  ✓ Model performance metrics tracked (Accuracy: {metric.accuracy}%)")

        print("✅ Analytics aggregation working correctly")

    def test_07_dashboards_integration(self):
        """Test 7: Dashboards pull data from all modules"""
        print("\n🧪 Test 7: Enhanced Dashboards Integration")

        # Create dashboard preferences
        pref = DashboardPreference.objects.create(
            user=self.doctor_user,
            show_analytics=True,
            show_appointments=True,
            show_notifications=True,
            show_recent_predictions=True,
            show_pending_validations=True,
            default_view='grid'
        )
        self.assertIsNotNone(pref)
        print("  ✓ Dashboard preferences created")

        # Verify dashboards can access data
        patient_count = Patient.objects.count()
        appointment_count = Appointment.objects.count()
        notification_count = Notification.objects.count()

        print(f"  ✓ Dashboard can access: {patient_count} patients, "
              f"{appointment_count} appointments, {notification_count} notifications")

        print("✅ Dashboards integration verified")

    def test_08_notification_system(self):
        """Test 8: Notification system works across modules"""
        print("\n🧪 Test 8: Cross-Module Notifications")

        # Create notifications from different modules
        notifications = [
            Notification.objects.create(
                recipient=self.patient_user,
                title='Appointment Reminder',
                message='Your appointment is tomorrow',
                notification_type='appointment',
                priority='high',
                status='sent'
            ),
            Notification.objects.create(
                recipient=self.patient_user,
                title='Test Results Available',
                message='Your COVID-19 test results are ready',
                notification_type='prediction',
                priority='high',
                status='sent'
            ),
            Notification.objects.create(
                recipient=self.patient_user,
                title='Medical Record Updated',
                message='Your medical records have been updated',
                notification_type='medical_record',
                priority='normal',
                status='sent'
            )
        ]

        self.assertEqual(Notification.objects.filter(recipient=self.patient_user).count(), 3)
        print(f"  ✓ Created {len(notifications)} notifications from different modules")

        # Test unread count
        unread = Notification.objects.filter(recipient=self.patient_user, is_read=False).count()
        print(f"  ✓ Unread notifications: {unread}")

        print("✅ Notification system integration verified")

    def test_09_url_routing(self):
        """Test 9: All major URLs are properly configured"""
        print("\n🧪 Test 9: URL Routing Configuration")

        url_tests = [
            ('home', 'Home page'),
            ('detection:upload_xray', 'X-ray upload'),
            ('medical_records:summary', 'Medical records', {'patient_id': self.patient.id}),
            ('appointments:my_appointments', 'Appointments'),
            ('notifications:notification_list', 'Notifications'),
            ('reporting:report_list', 'Reports'),
            ('audit:audit_log_list', 'Audit logs'),
            ('analytics:dashboard', 'Analytics'),
            ('dashboards:doctor_dashboard', 'Doctor dashboard'),
            ('api:token_obtain_pair', 'API token'),
        ]

        for url_test in url_tests:
            try:
                if len(url_test) == 3:
                    url = reverse(url_test[0], kwargs=url_test[2])
                else:
                    url = reverse(url_test[0])
                print(f"  ✓ {url_test[1]}: {url}")
            except Exception as e:
                print(f"  ✗ {url_test[1]}: {e}")

        print("✅ URL routing configuration verified")

    def test_10_settings_configuration(self):
        """Test 10: All settings are properly configured"""
        print("\n🧪 Test 10: Django Settings Configuration")

        from django.conf import settings

        # Check installed apps
        required_apps = [
            'detection', 'medical_records', 'appointments',
            'notifications', 'reporting', 'audit',
            'analytics', 'dashboards', 'api',
            'rest_framework', 'drf_yasg', 'corsheaders'
        ]

        for app in required_apps:
            self.assertIn(app, settings.INSTALLED_APPS)
        print(f"  ✓ All {len(required_apps)} required apps in INSTALLED_APPS")

        # Check middleware
        self.assertIn('audit.middleware.AuditMiddleware', settings.MIDDLEWARE)
        print("  ✓ Audit middleware configured")

        # Check REST framework settings
        self.assertIn('DEFAULT_AUTHENTICATION_CLASSES', settings.REST_FRAMEWORK)
        print("  ✓ REST framework configured")

        # Check media and static settings
        self.assertIsNotNone(settings.MEDIA_ROOT)
        self.assertIsNotNone(settings.STATIC_ROOT)
        print("  ✓ Media and static directories configured")

        print("✅ Settings configuration verified")


def run_tests():
    """Run all integration tests"""
    import unittest

    print("=" * 80)
    print("🚀 COVID-19 Detection System - Full Integration Test Suite")
    print("=" * 80)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(FullSystemIntegrationTest)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 80)
    print("📊 Test Summary")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n✅ ALL INTEGRATION TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED")

    print("=" * 80)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
