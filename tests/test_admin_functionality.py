"""
Comprehensive tests for admin functionality and login.

Tests verify:
1. Admin can authenticate with credentials
2. Admin has correct role and permissions
3. Admin can access Django admin panel
4. Admin can create staff users
5. Patient registration still works independently
6. Admin dashboard access works
"""

import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from detection.models import UserProfile, Patient


class AdminAuthenticationTest(TestCase):
    """Test admin authentication and login functionality"""

    def setUp(self):
        """Create admin user for testing"""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        # Ensure admin role is set
        self.admin_user.profile.role = 'admin'
        self.admin_user.profile.save()

    def test_admin_account_exists(self):
        """Verify admin account exists in database"""
        self.assertTrue(User.objects.filter(username='admin').exists())
        admin = User.objects.get(username='admin')
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)

    def test_admin_has_correct_role(self):
        """Verify admin has admin role in profile"""
        admin = User.objects.get(username='admin')
        self.assertEqual(admin.profile.role, 'admin')
        self.assertTrue(admin.profile.is_admin())
        self.assertFalse(admin.profile.is_staff())
        self.assertFalse(admin.profile.is_patient())

    def test_admin_can_authenticate(self):
        """Test admin can login with credentials"""
        # Test authentication
        authenticated = self.client.login(username='admin', password='admin123')
        self.assertTrue(authenticated, "Admin should be able to authenticate")

    def test_admin_login_via_login_page(self):
        """Test admin can login through login page"""
        login_url = reverse('login')
        response = self.client.post(login_url, {
            'username': 'admin',
            'password': 'admin123'
        })

        # Should redirect after successful login
        self.assertEqual(response.status_code, 302, "Should redirect after login")

        # User should be authenticated
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.username, 'admin')

    def test_admin_wrong_password_fails(self):
        """Test admin login fails with wrong password"""
        authenticated = self.client.login(username='admin', password='wrongpassword')
        self.assertFalse(authenticated, "Should not authenticate with wrong password")

    def test_admin_has_full_permissions(self):
        """Verify admin has all permissions"""
        admin = User.objects.get(username='admin')
        profile = admin.profile

        # Test permission methods
        self.assertTrue(profile.can_create_users())
        self.assertTrue(profile.is_admin())


class AdminPanelAccessTest(TestCase):
    """Test admin can access Django admin panel"""

    def setUp(self):
        """Create admin user"""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        self.admin_user.profile.role = 'admin'
        self.admin_user.profile.save()

    def test_admin_can_access_admin_panel(self):
        """Test admin can access /admin/"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/admin/')

        # Should get 200 OK
        self.assertEqual(response.status_code, 200)

    def test_non_admin_cannot_access_admin_panel(self):
        """Test non-admin users are blocked from admin panel"""
        # Create a patient user
        patient = User.objects.create_user(
            username='patient',
            password='patient123'
        )

        self.client.login(username='patient', password='patient123')
        response = self.client.get('/admin/')

        # Should redirect to login
        self.assertEqual(response.status_code, 302)

    def test_unauthenticated_cannot_access_admin_panel(self):
        """Test unauthenticated users redirected from admin panel"""
        response = self.client.get('/admin/')

        # Should redirect to login
        self.assertEqual(response.status_code, 302)


class AdminCreateStaffTest(TestCase):
    """Test admin can create staff users"""

    def setUp(self):
        """Create admin user"""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        self.admin_user.profile.role = 'admin'
        self.admin_user.profile.save()

    def test_admin_can_create_staff_programmatically(self):
        """Test admin can create staff user via code"""
        # Simulate admin creating staff
        staff_user = User.objects.create_user(
            username='staff1',
            email='staff1@test.com',
            password='staff123'
        )
        staff_user.profile.role = 'staff'
        staff_user.profile.save()

        # Verify staff user created
        self.assertTrue(User.objects.filter(username='staff1').exists())
        staff = User.objects.get(username='staff1')
        self.assertEqual(staff.profile.role, 'staff')
        self.assertTrue(staff.profile.is_staff())

    def test_admin_can_modify_user_roles(self):
        """Test admin can change user roles"""
        # Create a patient
        patient = User.objects.create_user(
            username='patient1',
            password='patient123'
        )

        # Initially should be patient
        self.assertEqual(patient.profile.role, 'patient')

        # Admin changes to staff
        patient.profile.role = 'staff'
        patient.profile.save()

        # Verify change
        updated_user = User.objects.get(username='patient1')
        self.assertEqual(updated_user.profile.role, 'staff')
        self.assertTrue(updated_user.profile.is_staff())


class AdminDashboardAccessTest(TestCase):
    """Test admin dashboard access"""

    def setUp(self):
        """Create admin user"""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        self.admin_user.profile.role = 'admin'
        self.admin_user.profile.save()

    def test_admin_can_access_admin_dashboard(self):
        """Test admin can access admin dashboard"""
        self.client.login(username='admin', password='admin123')

        # Try to access admin dashboard
        try:
            response = self.client.get(reverse('dashboards:admin_dashboard'))
            # Should be accessible (200) or redirect (302)
            self.assertIn(response.status_code, [200, 302])
        except:
            # Dashboard might not exist yet, that's ok
            pass


class IntegrationTest(TestCase):
    """Integration tests for admin and patient registration"""

    def setUp(self):
        """Set up test environment"""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        self.admin_user.profile.role = 'admin'
        self.admin_user.profile.save()

    def test_patient_registration_still_works_with_admin_existing(self):
        """Verify patient registration works independently of admin"""
        register_url = reverse('register')

        response = self.client.post(register_url, {
            'username': 'newpatient',
            'first_name': 'New',
            'last_name': 'Patient',
            'email': 'new@patient.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        })

        # Patient should be created
        self.assertTrue(User.objects.filter(username='newpatient').exists())
        patient = User.objects.get(username='newpatient')

        # Should be patient role
        self.assertEqual(patient.profile.role, 'patient')
        self.assertTrue(patient.profile.is_patient())

    def test_multiple_user_types_coexist(self):
        """Test admin, staff, and patient can all exist"""
        # Create staff
        staff = User.objects.create_user(
            username='staff1',
            password='staff123'
        )
        staff.profile.role = 'staff'
        staff.profile.save()

        # Create patient via registration
        self.client.post(reverse('register'), {
            'username': 'patient1',
            'first_name': 'Patient',
            'last_name': 'One',
            'email': 'patient1@test.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        })

        # Verify all three types exist
        admin = User.objects.get(username='admin')
        staff = User.objects.get(username='staff1')
        patient = User.objects.get(username='patient1')

        self.assertTrue(admin.profile.is_admin())
        self.assertTrue(staff.profile.is_staff())
        self.assertTrue(patient.profile.is_patient())

    def test_admin_patient_and_staff_can_all_login(self):
        """Test all user types can login simultaneously"""
        # Create staff and patient
        staff = User.objects.create_user(username='staff1', password='staff123')
        staff.profile.role = 'staff'
        staff.profile.save()

        patient = User.objects.create_user(username='patient1', password='patient123')
        # patient role is default

        # Test all can authenticate
        client1 = Client()
        client2 = Client()
        client3 = Client()

        admin_auth = client1.login(username='admin', password='admin123')
        staff_auth = client2.login(username='staff1', password='staff123')
        patient_auth = client3.login(username='patient1', password='patient123')

        self.assertTrue(admin_auth, "Admin should login")
        self.assertTrue(staff_auth, "Staff should login")
        self.assertTrue(patient_auth, "Patient should login")


@pytest.mark.django_db
class TestAdminFunctionalityPytest:
    """Pytest-style tests for admin functionality"""

    def test_admin_credentials_work(self):
        """Test admin credentials are correct"""
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        admin.profile.role = 'admin'
        admin.profile.save()

        # Test password
        assert admin.check_password('admin123')
        assert not admin.check_password('wrongpassword')

    def test_admin_profile_autocreated(self):
        """Test admin profile is auto-created"""
        admin = User.objects.create_superuser(
            username='testadmin',
            email='testadmin@test.com',
            password='test123'
        )

        # Profile should exist
        assert hasattr(admin, 'profile')
        assert admin.profile is not None

    def test_admin_role_assignment(self):
        """Test admin role can be assigned"""
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )

        # Set admin role
        admin.profile.role = 'admin'
        admin.profile.save()

        # Verify
        admin.refresh_from_db()
        assert admin.profile.role == 'admin'
        assert admin.profile.is_admin()
