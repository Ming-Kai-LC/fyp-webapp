from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from detection.models import Patient, UserProfile
from .models import (
    AuditLog, DataAccessLog, LoginAttempt, DataChange,
    ComplianceReport, DataRetentionPolicy, SecurityAlert
)
from .services import ComplianceReportGenerator, AuditExporter, SecurityMonitor
from .forms import AuditLogFilterForm, ComplianceReportForm


class AuditLogModelTest(TestCase):
    """Test AuditLog model"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_audit_log_creation(self):
        """Test creating an audit log entry"""
        log = AuditLog.log(
            user=self.user,
            action_type='login',
            description='User logged in',
            severity='info',
            ip_address='127.0.0.1'
        )
        self.assertEqual(log.username, 'testuser')
        self.assertEqual(log.action_type, 'login')
        self.assertTrue(log.success)

    def test_audit_log_str(self):
        """Test string representation"""
        log = AuditLog.log(
            user=self.user,
            action_type='login',
            description='User logged in'
        )
        self.assertIn('testuser', str(log))
        self.assertIn('login', str(log))


class DataAccessLogModelTest(TestCase):
    """Test DataAccessLog model"""

    def setUp(self):
        self.user = User.objects.create_user(username='doctor', password='testpass')
        self.patient_user = User.objects.create_user(username='patient', password='testpass')
        self.profile = UserProfile.objects.get(user=self.user)
        self.profile.role = 'doctor'
        self.profile.save()
        self.patient_profile = UserProfile.objects.get(user=self.patient_user)
        self.patient_profile.role = 'patient'
        self.patient_profile.save()
        self.patient = Patient.objects.create(
            user=self.patient_user,
            age=30,
            gender='M'
        )

    def test_data_access_log_creation(self):
        """Test creating a data access log"""
        log = DataAccessLog.objects.create(
            accessor=self.user,
            accessor_role='doctor',
            patient=self.patient,
            data_type='medical_history',
            data_id=1,
            access_type='view',
            ip_address='127.0.0.1'
        )
        self.assertEqual(log.accessor, self.user)
        self.assertEqual(log.patient, self.patient)
        self.assertFalse(log.flagged_for_review)


class LoginAttemptModelTest(TestCase):
    """Test LoginAttempt model"""

    def test_successful_login_attempt(self):
        """Test recording successful login"""
        attempt = LoginAttempt.objects.create(
            username='testuser',
            success=True,
            ip_address='127.0.0.1',
            user_agent='Mozilla/5.0'
        )
        self.assertTrue(attempt.success)
        self.assertFalse(attempt.is_suspicious)

    def test_failed_login_attempt(self):
        """Test recording failed login"""
        attempt = LoginAttempt.objects.create(
            username='testuser',
            success=False,
            ip_address='127.0.0.1',
            failure_reason='Invalid credentials'
        )
        self.assertFalse(attempt.success)
        self.assertEqual(attempt.failure_reason, 'Invalid credentials')


class SecurityAlertModelTest(TestCase):
    """Test SecurityAlert model"""

    def test_security_alert_creation(self):
        """Test creating a security alert"""
        alert = SecurityAlert.objects.create(
            alert_type='failed_login',
            severity='high',
            description='Multiple failed login attempts',
            ip_address='192.168.1.1'
        )
        self.assertFalse(alert.acknowledged)
        self.assertEqual(alert.severity, 'high')

    def test_alert_acknowledgement(self):
        """Test acknowledging an alert"""
        user = User.objects.create_user(username='admin', password='testpass')
        alert = SecurityAlert.objects.create(
            alert_type='failed_login',
            severity='high',
            description='Test alert'
        )
        alert.acknowledged = True
        alert.acknowledged_by = user
        alert.acknowledged_at = timezone.now()
        alert.save()
        self.assertTrue(alert.acknowledged)
        self.assertEqual(alert.acknowledged_by, user)


class ComplianceReportGeneratorTest(TestCase):
    """Test ComplianceReportGenerator service"""

    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='testpass')
        self.start_date = timezone.now() - timedelta(days=30)
        self.end_date = timezone.now()

    def test_hipaa_report_generation(self):
        """Test generating HIPAA compliance report"""
        generator = ComplianceReportGenerator(
            report_type='hipaa_audit',
            start_date=self.start_date,
            end_date=self.end_date
        )
        report = generator.generate(generated_by=self.user)
        self.assertIsNotNone(report)
        self.assertEqual(report.report_type, 'hipaa_audit')
        self.assertEqual(report.generated_by, self.user)

    def test_security_audit_report(self):
        """Test generating security audit report"""
        generator = ComplianceReportGenerator(
            report_type='security_audit',
            start_date=self.start_date,
            end_date=self.end_date
        )
        report = generator.generate(generated_by=self.user)
        self.assertEqual(report.report_type, 'security_audit')


class SecurityMonitorTest(TestCase):
    """Test SecurityMonitor service"""

    def test_failed_login_detection(self):
        """Test detection of multiple failed logins"""
        username = 'testuser'
        ip_address = '192.168.1.1'

        # Create 5 failed login attempts within the last hour
        for i in range(5):
            LoginAttempt.objects.create(
                username=username,
                success=False,
                ip_address=ip_address,
                timestamp=timezone.now()
            )

        # Check if alert is triggered
        result = SecurityMonitor.check_failed_login_attempts(username, ip_address)
        self.assertTrue(result)

        # Verify alert was created
        alerts = SecurityAlert.objects.filter(
            alert_type='failed_login',
            ip_address=ip_address
        )
        self.assertTrue(alerts.exists())


class AuditFormsTest(TestCase):
    """Test audit forms"""

    def test_audit_log_filter_form_valid(self):
        """Test valid audit log filter form"""
        form_data = {
            'action_type': 'login',
            'severity': 'info',
            'search': 'test'
        }
        form = AuditLogFilterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_compliance_report_form_valid(self):
        """Test valid compliance report form"""
        start_date = timezone.now() - timedelta(days=30)
        end_date = timezone.now()
        form_data = {
            'report_type': 'hipaa_audit',
            'start_date': start_date,
            'end_date': end_date
        }
        form = ComplianceReportForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_compliance_report_form_invalid_dates(self):
        """Test form validation for invalid date range"""
        start_date = timezone.now()
        end_date = timezone.now() - timedelta(days=30)
        form_data = {
            'report_type': 'hipaa_audit',
            'start_date': start_date,
            'end_date': end_date
        }
        form = ComplianceReportForm(data=form_data)
        self.assertFalse(form.is_valid())


class AuditViewsTest(TestCase):
    """Test audit views"""

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin',
            password='testpass'
        )
        self.admin_profile = UserProfile.objects.get(user=self.admin_user)
        self.admin_profile.role = 'admin'
        self.admin_profile.save()

    def test_audit_log_list_requires_login(self):
        """Test that audit log list requires login"""
        response = self.client.get('/audit/logs/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_audit_log_list_requires_admin(self):
        """Test that audit log list requires admin role"""
        # Create regular user
        user = User.objects.create_user(username='user', password='testpass')
        self.client.login(username='user', password='testpass')
        response = self.client.get('/audit/logs/')
        self.assertEqual(response.status_code, 302)  # Redirect due to lack of permissions

    def test_audit_log_list_access_for_admin(self):
        """Test that admin can access audit log list"""
        self.client.login(username='admin', password='testpass')
        response = self.client.get('/audit/logs/')
        self.assertEqual(response.status_code, 200)

    def test_my_access_history_view(self):
        """Test user can view their own access history"""
        user = User.objects.create_user(username='user', password='testpass')
        self.client.login(username='user', password='testpass')
        response = self.client.get('/audit/my-history/')
        self.assertEqual(response.status_code, 200)


class AuditExporterTest(TestCase):
    """Test AuditExporter service"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        # Create some audit logs
        for i in range(5):
            AuditLog.log(
                user=self.user,
                action_type='login',
                description=f'Test log {i}',
                severity='info'
            )

    def test_csv_export(self):
        """Test exporting audit logs to CSV"""
        exporter = AuditExporter()
        csv_buffer = exporter.export_to_csv()
        csv_content = csv_buffer.getvalue()
        self.assertIn('Timestamp', csv_content)
        self.assertIn('testuser', csv_content)
        self.assertIn('login', csv_content)


class DataRetentionPolicyTest(TestCase):
    """Test DataRetentionPolicy model"""

    def test_policy_creation(self):
        """Test creating a data retention policy"""
        policy = DataRetentionPolicy.objects.create(
            data_type='audit_logs',
            retention_days=365,
            description='Retain audit logs for 1 year',
            is_active=True,
            auto_delete=False
        )
        self.assertEqual(policy.retention_days, 365)
        self.assertTrue(policy.is_active)


class DataChangeModelTest(TestCase):
    """Test DataChange model"""

    def test_data_change_tracking(self):
        """Test tracking data changes"""
        user = User.objects.create_user(username='admin', password='testpass')
        from django.contrib.contenttypes.models import ContentType

        patient_user = User.objects.create_user(username='patient', password='testpass')
        patient = Patient.objects.create(user=patient_user, age=30, gender='M')
        content_type = ContentType.objects.get_for_model(Patient)

        change = DataChange.objects.create(
            content_type=content_type,
            object_id=patient.id,
            changed_by=user,
            field_name='age',
            old_value='30',
            new_value='31'
        )
        self.assertEqual(change.field_name, 'age')
        self.assertEqual(change.old_value, '30')
        self.assertEqual(change.new_value, '31')


class IntegrationTest(TestCase):
    """Integration tests for audit module"""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            password='testpass'
        )
        self.admin_profile = UserProfile.objects.get(user=self.admin_user)
        self.admin_profile.role = 'admin'
        self.admin_profile.save()

        self.patient_user = User.objects.create_user(
            username='patient',
            password='testpass'
        )
        self.patient_profile = UserProfile.objects.get(user=self.patient_user)
        self.patient_profile.role = 'patient'
        self.patient_profile.save()
        self.patient = Patient.objects.create(
            user=self.patient_user,
            age=25,
            gender='F'
        )

    def test_full_audit_workflow(self):
        """Test complete audit workflow"""
        # 1. Create audit log
        log = AuditLog.log(
            user=self.admin_user,
            action_type='read',
            description='Viewed patient record',
            severity='info'
        )
        self.assertIsNotNone(log)

        # 2. Create data access log
        access_log = DataAccessLog.objects.create(
            accessor=self.admin_user,
            accessor_role='admin',
            patient=self.patient,
            data_type='medical_history',
            data_id=self.patient.id,
            access_type='view'
        )
        self.assertIsNotNone(access_log)

        # 3. Generate compliance report
        generator = ComplianceReportGenerator(
            report_type='access_review',
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now()
        )
        report = generator.generate(generated_by=self.admin_user)
        self.assertIsNotNone(report)

        # 4. Verify report contains data
        self.assertIn('total_accesses', report.summary)
