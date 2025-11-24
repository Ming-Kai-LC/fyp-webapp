"""
Test patient-only registration according to user-role-permissions skill.

This test verifies that:
1. Public registration only creates patient accounts
2. Role field is not in the registration form
3. Role is hardcoded to 'patient' regardless of any input
4. Patient profile is always created for new registrations
"""

import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from detection.models import UserProfile, Patient
from detection.forms import UserRegistrationForm


class PatientOnlyRegistrationTest(TestCase):
    """Test cases for patient-only public registration"""

    def setUp(self):
        """Set up test client and data"""
        self.client = Client()
        self.register_url = reverse("register")
        self.valid_user_data = {
            "username": "testpatient",
            "first_name": "Test",
            "last_name": "Patient",
            "email": "test@patient.com",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!",
        }

    def test_registration_form_has_no_role_field(self):
        """Verify role field is not present in public registration form"""
        form = UserRegistrationForm()
        self.assertNotIn("role", form.fields)

    def test_successful_registration_creates_patient_only(self):
        """Verify registration always creates patient account"""
        # Submit registration
        response = self.client.post(self.register_url, self.valid_user_data)

        # User should be created
        self.assertTrue(User.objects.filter(username="testpatient").exists())
        user = User.objects.get(username="testpatient")

        # Role should be patient
        self.assertEqual(user.profile.role, "patient")
        self.assertTrue(user.profile.is_patient())
        self.assertFalse(user.profile.is_staff())
        self.assertFalse(user.profile.is_admin())

    def test_patient_profile_automatically_created(self):
        """Verify Patient object is created during registration"""
        # Submit registration
        response = self.client.post(self.register_url, self.valid_user_data)

        # Patient profile should exist
        user = User.objects.get(username="testpatient")
        self.assertTrue(Patient.objects.filter(user=user).exists())

    def test_registration_redirects_to_patient_dashboard(self):
        """Verify successful registration redirects to patient dashboard"""
        response = self.client.post(self.register_url, self.valid_user_data)

        # Should redirect to patient dashboard
        self.assertRedirects(
            response,
            reverse("detection:patient_dashboard"),
            fetch_redirect_response=False
        )

    def test_cannot_register_as_staff_via_form_manipulation(self):
        """Verify attempting to inject staff role fails"""
        # Try to inject staff role via form manipulation
        malicious_data = self.valid_user_data.copy()
        malicious_data["role"] = "staff"  # Attempt to bypass

        response = self.client.post(self.register_url, malicious_data)

        # User should still be patient, not staff
        user = User.objects.get(username="testpatient")
        self.assertEqual(user.profile.role, "patient")
        self.assertFalse(user.profile.is_staff())

    def test_registration_creates_user_with_correct_details(self):
        """Verify user details are saved correctly"""
        response = self.client.post(self.register_url, self.valid_user_data)

        user = User.objects.get(username="testpatient")
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "Patient")
        self.assertEqual(user.email, "test@patient.com")

    def test_registration_form_validation(self):
        """Verify form validates required fields"""
        # Missing email
        invalid_data = self.valid_user_data.copy()
        invalid_data["email"] = ""

        form = UserRegistrationForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_user_logged_in_after_registration(self):
        """Verify user is automatically logged in after registration"""
        response = self.client.post(self.register_url, self.valid_user_data)

        # User should be logged in
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.username, "testpatient")


@pytest.mark.django_db
class TestUserRolePermissionsCompliance:
    """Verify compliance with user-role-permissions skill"""

    def test_skill_rule_1_only_admin_creates_staff(self):
        """Only admin can create staff users (not public registration)"""
        client = Client()
        register_url = reverse("register")

        # Attempt to register
        data = {
            "username": "staffwannabe",
            "first_name": "Staff",
            "last_name": "Wannabe",
            "email": "staff@test.com",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!",
        }
        client.post(register_url, data)

        user = User.objects.get(username="staffwannabe")
        # Should NOT be staff
        assert user.profile.role == "patient"
        assert not user.profile.is_staff()

    def test_skill_rule_2_public_registration_patient_only(self):
        """Public can only register as patients"""
        client = Client()
        register_url = reverse("register")

        data = {
            "username": "publicuser",
            "first_name": "Public",
            "last_name": "User",
            "email": "public@test.com",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!",
        }
        client.post(register_url, data)

        user = User.objects.get(username="publicuser")
        assert user.profile.role == "patient"
        assert user.profile.is_patient()

    def test_skill_rule_5_patient_self_service(self):
        """Patients can register and have patient profile"""
        client = Client()
        register_url = reverse("register")

        data = {
            "username": "selfservice",
            "first_name": "Self",
            "last_name": "Service",
            "email": "self@test.com",
            "password1": "SecurePass123!",
            "password2": "SecurePass123!",
        }
        client.post(register_url, data)

        user = User.objects.get(username="selfservice")

        # Should have patient role
        assert user.profile.role == "patient"

        # Should have Patient object
        assert Patient.objects.filter(user=user).exists()

        # Verify user can authenticate (password is set correctly)
        assert user.check_password("SecurePass123!")
