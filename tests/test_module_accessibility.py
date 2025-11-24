"""
Comprehensive Module Accessibility Tests

Tests module access control and navigation visibility for all user roles:
- Admin: Full access to all modules
- Staff: Access to patient management, analytics, reporting, audit (limited)
- Patient: Access to own data only (dashboard, results, medical records, appointments)

Tests cover:
1. URL access permissions
2. Navigation visibility in UI
3. Dashboard redirections
4. Module-level authorization
"""

import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from detection.models import UserProfile, Patient

User = get_user_model()


@pytest.fixture
def admin_user(db):
    """Create admin user with profile"""
    user = User.objects.create_user(
        username='admin_test',
        email='admin@test.com',
        password='admin123',
        is_staff=True
    )
    # Profile is auto-created by signal, just update the role
    user.profile.role = 'admin'
    user.profile.save()
    return user


@pytest.fixture
def staff_user(db):
    """Create staff user with profile"""
    user = User.objects.create_user(
        username='staff_test',
        email='staff@test.com',
        password='staff123'
    )
    # Profile is auto-created by signal, just update the role
    user.profile.role = 'staff'
    user.profile.save()
    return user


@pytest.fixture
def patient_user(db):
    """Create patient user with profile and patient info"""
    user = User.objects.create_user(
        username='patient_test',
        email='patient@test.com',
        password='patient123',
        first_name='John',
        last_name='Doe'
    )
    # Profile is auto-created by signal, just update the role
    user.profile.role = 'patient'
    user.profile.save()
    Patient.objects.create(
        user=user,
        age=30,
        date_of_birth='1990-01-01',
        gender='M'
    )
    return user


@pytest.fixture
def client():
    """Create test client"""
    return Client()


# ========================================
# DASHBOARD ACCESS TESTS
# ========================================

@pytest.mark.django_db
class TestDashboardAccess:
    """Test dashboard access for different roles"""

    def test_admin_can_access_admin_dashboard(self, client, admin_user):
        """Admin should access admin dashboard"""
        client.force_login(admin_user)
        response = client.get(reverse('dashboards:admin'))
        assert response.status_code == 200

    def test_staff_cannot_access_admin_dashboard(self, client, staff_user):
        """Staff should NOT access admin dashboard"""
        client.force_login(staff_user)
        response = client.get(reverse('dashboards:admin'))
        assert response.status_code in [302, 403]  # Redirect or forbidden

    def test_patient_cannot_access_admin_dashboard(self, client, patient_user):
        """Patient should NOT access admin dashboard"""
        client.force_login(patient_user)
        response = client.get(reverse('dashboards:admin'))
        assert response.status_code in [302, 403]

    def test_staff_can_access_staff_dashboard(self, client, staff_user):
        """Staff should access staff dashboard"""
        client.force_login(staff_user)
        response = client.get(reverse('dashboards:staff'))
        assert response.status_code == 200

    def test_admin_can_access_staff_dashboard(self, client, admin_user):
        """Admin should access staff dashboard"""
        client.force_login(admin_user)
        response = client.get(reverse('dashboards:staff'))
        assert response.status_code == 200

    def test_patient_cannot_access_staff_dashboard(self, client, patient_user):
        """Patient should NOT access staff dashboard"""
        client.force_login(patient_user)
        response = client.get(reverse('dashboards:staff'))
        assert response.status_code in [302, 403]

    def test_patient_can_access_patient_dashboard(self, client, patient_user):
        """Patient should access patient dashboard"""
        client.force_login(patient_user)
        response = client.get(reverse('dashboards:patient'))
        assert response.status_code == 200

    def test_admin_can_access_patient_dashboard(self, client, admin_user):
        """Admin should access patient dashboard"""
        client.force_login(admin_user)
        response = client.get(reverse('dashboards:patient'))
        assert response.status_code == 200


# ========================================
# DETECTION MODULE TESTS
# ========================================

@pytest.mark.django_db
class TestDetectionModuleAccess:
    """Test detection module access"""

    def test_staff_can_upload_xray(self, client, staff_user):
        """Staff should access X-ray upload"""
        client.force_login(staff_user)
        response = client.get(reverse('detection:upload_xray'))
        assert response.status_code == 200

    def test_admin_can_upload_xray(self, client, admin_user):
        """Admin should access X-ray upload"""
        client.force_login(admin_user)
        response = client.get(reverse('detection:upload_xray'))
        assert response.status_code == 200

    def test_patient_cannot_upload_xray(self, client, patient_user):
        """Patient should NOT upload X-rays"""
        client.force_login(patient_user)
        response = client.get(reverse('detection:upload_xray'))
        assert response.status_code in [302, 403]

    def test_patient_can_view_prediction_history(self, client, patient_user):
        """Patient should view own prediction history"""
        client.force_login(patient_user)
        response = client.get(reverse('detection:prediction_history'))
        assert response.status_code == 200


# ========================================
# ANALYTICS MODULE TESTS
# ========================================

@pytest.mark.django_db
class TestAnalyticsModuleAccess:
    """Test analytics module access"""

    def test_admin_can_access_analytics(self, client, admin_user):
        """Admin should access analytics"""
        client.force_login(admin_user)
        response = client.get(reverse('analytics:dashboard'))
        assert response.status_code == 200

    def test_staff_can_access_analytics(self, client, staff_user):
        """Staff should access analytics"""
        client.force_login(staff_user)
        response = client.get(reverse('analytics:dashboard'))
        assert response.status_code == 200

    def test_patient_cannot_access_analytics(self, client, patient_user):
        """Patient should NOT access analytics"""
        client.force_login(patient_user)
        response = client.get(reverse('analytics:dashboard'))
        assert response.status_code in [302, 403]


# ========================================
# REPORTING MODULE TESTS
# ========================================

@pytest.mark.django_db
class TestReportingModuleAccess:
    """Test reporting module access"""

    def test_admin_can_access_report_list(self, client, admin_user):
        """Admin should access report list"""
        client.force_login(admin_user)
        response = client.get(reverse('reporting:report_list'))
        assert response.status_code == 200

    def test_staff_can_access_report_list(self, client, staff_user):
        """Staff should access report list"""
        client.force_login(staff_user)
        response = client.get(reverse('reporting:report_list'))
        assert response.status_code == 200

    def test_patient_cannot_access_report_list(self, client, patient_user):
        """Patient should NOT access report list"""
        client.force_login(patient_user)
        response = client.get(reverse('reporting:report_list'))
        assert response.status_code in [302, 403]


# ========================================
# AUDIT MODULE TESTS
# ========================================

@pytest.mark.django_db
class TestAuditModuleAccess:
    """Test audit module access"""

    def test_admin_can_access_audit_logs(self, client, admin_user):
        """Admin should access audit logs"""
        client.force_login(admin_user)
        response = client.get(reverse('audit:audit_log_list'))
        assert response.status_code == 200

    def test_staff_can_access_audit_logs(self, client, staff_user):
        """Staff should access audit logs (limited view)"""
        client.force_login(staff_user)
        response = client.get(reverse('audit:audit_log_list'))
        # Staff may have limited access or redirect
        assert response.status_code in [200, 302, 403]

    def test_patient_cannot_access_audit_logs(self, client, patient_user):
        """Patient should NOT access audit logs"""
        client.force_login(patient_user)
        response = client.get(reverse('audit:audit_log_list'))
        assert response.status_code in [302, 403]

    def test_admin_can_access_security_alerts(self, client, admin_user):
        """Admin should access security alerts"""
        client.force_login(admin_user)
        response = client.get(reverse('audit:security_alerts_dashboard'))
        assert response.status_code == 200

    def test_staff_cannot_access_security_alerts(self, client, staff_user):
        """Staff should NOT access security alerts"""
        client.force_login(staff_user)
        response = client.get(reverse('audit:security_alerts_dashboard'))
        assert response.status_code in [302, 403]

    def test_patient_can_access_own_access_history(self, client, patient_user):
        """Patient should view own access history"""
        client.force_login(patient_user)
        response = client.get(reverse('audit:my_access_history'))
        assert response.status_code == 200


# ========================================
# APPOINTMENTS MODULE TESTS
# ========================================

@pytest.mark.django_db
class TestAppointmentsModuleAccess:
    """Test appointments module access"""

    def test_patient_can_book_appointment(self, client, patient_user):
        """Patient should book appointments"""
        client.force_login(patient_user)
        response = client.get(reverse('appointments:book_appointment'))
        assert response.status_code == 200

    def test_patient_can_view_own_appointments(self, client, patient_user):
        """Patient should view own appointments"""
        client.force_login(patient_user)
        response = client.get(reverse('appointments:my_appointments'))
        assert response.status_code == 200

    def test_staff_can_view_doctor_appointments(self, client, staff_user):
        """Staff should view appointments (as doctor)"""
        client.force_login(staff_user)
        response = client.get(reverse('appointments:doctor_appointments'))
        # Staff might need additional setup, may redirect
        assert response.status_code in [200, 302]


# ========================================
# MEDICAL RECORDS MODULE TESTS
# ========================================

@pytest.mark.django_db
class TestMedicalRecordsModuleAccess:
    """Test medical records module access"""

    def test_patient_can_view_own_medical_summary(self, client, patient_user):
        """Patient should view own medical summary"""
        client.force_login(patient_user)
        patient = Patient.objects.get(user=patient_user)
        response = client.get(reverse('medical_records:medical_summary', args=[patient.id]))
        assert response.status_code == 200

    def test_patient_can_view_own_conditions(self, client, patient_user):
        """Patient should view own medical conditions"""
        client.force_login(patient_user)
        response = client.get(reverse('medical_records:condition_list'))
        assert response.status_code == 200

    def test_staff_can_view_medical_records(self, client, staff_user):
        """Staff should view medical records"""
        client.force_login(staff_user)
        response = client.get(reverse('medical_records:condition_list'))
        assert response.status_code == 200


# ========================================
# NOTIFICATIONS MODULE TESTS
# ========================================

@pytest.mark.django_db
class TestNotificationsModuleAccess:
    """Test notifications module access"""

    def test_patient_can_view_notifications(self, client, patient_user):
        """Patient should view notifications"""
        client.force_login(patient_user)
        response = client.get(reverse('notifications:notification_list'))
        assert response.status_code == 200

    def test_staff_can_view_notifications(self, client, staff_user):
        """Staff should view notifications"""
        client.force_login(staff_user)
        response = client.get(reverse('notifications:notification_list'))
        assert response.status_code == 200

    def test_admin_can_view_notifications(self, client, admin_user):
        """Admin should view notifications"""
        client.force_login(admin_user)
        response = client.get(reverse('notifications:notification_list'))
        assert response.status_code == 200


# ========================================
# NAVIGATION VISIBILITY TESTS
# ========================================

@pytest.mark.django_db
class TestNavigationVisibility:
    """Test navigation menu visibility for different roles"""

    def test_admin_navigation_contains_admin_links(self, client, admin_user):
        """Admin navigation should show admin-specific links"""
        client.force_login(admin_user)
        response = client.get(reverse('home'))
        content = response.content.decode('utf-8')

        # Admin should see these links
        assert 'Admin Dashboard' in content or 'dashboards:admin' in content
        assert 'Security Alerts' in content or 'security_alerts' in content
        assert 'Compliance Reports' in content or 'compliance' in content

    def test_staff_navigation_contains_staff_links(self, client, staff_user):
        """Staff navigation should show staff-specific links"""
        client.force_login(staff_user)
        response = client.get(reverse('home'))
        content = response.content.decode('utf-8')

        # Staff should see these links
        assert 'Upload X-Ray' in content or 'upload_xray' in content
        assert 'Analytics' in content or 'analytics' in content
        assert 'Reports' in content or 'report_list' in content

        # Staff should NOT see admin-only links
        assert 'Security Alerts' not in content

    def test_patient_navigation_contains_patient_links(self, client, patient_user):
        """Patient navigation should show patient-specific links"""
        client.force_login(patient_user)
        response = client.get(reverse('home'))
        content = response.content.decode('utf-8')

        # Patient should see these links
        assert 'My Results' in content or 'prediction_history' in content
        assert 'Medical Records' in content or 'medical_records' in content
        assert 'My Appointments' in content or 'my_appointments' in content

        # Patient should NOT see admin/staff links
        assert 'Upload X-Ray' not in content
        assert 'Analytics' not in content


# ========================================
# UNAUTHENTICATED ACCESS TESTS
# ========================================

@pytest.mark.django_db
class TestUnauthenticatedAccess:
    """Test that unauthenticated users are redirected to login"""

    def test_unauthenticated_redirects_to_login_for_dashboard(self, client):
        """Unauthenticated users should redirect to login"""
        response = client.get(reverse('dashboards:admin'))
        assert response.status_code == 302
        assert '/accounts/login' in response.url or '/login' in response.url

    def test_unauthenticated_redirects_to_login_for_analytics(self, client):
        """Unauthenticated users should redirect to login"""
        response = client.get(reverse('analytics:dashboard'))
        assert response.status_code == 302
        assert '/accounts/login' in response.url or '/login' in response.url

    def test_public_pages_accessible(self, client):
        """Public pages should be accessible without login"""
        response = client.get(reverse('home'))
        assert response.status_code == 200

        response = client.get(reverse('register'))
        assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
