from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date, timedelta
from detection.models import Patient
from .models import (
    MedicalCondition, Allergy, Medication, Vaccination,
    LifestyleInformation, COVIDRiskScore
)
from .services import RiskAssessmentService


class MedicalConditionModelTest(TestCase):
    """Tests for MedicalCondition model"""

    def setUp(self):
        self.user = User.objects.create_user(username='testpatient', password='testpass123')
        self.patient = Patient.objects.create(
            user=self.user,
            age=45,
            gender='M',
            date_of_birth=date(1978, 5, 15)
        )

    def test_create_medical_condition(self):
        """Test creating a medical condition"""
        condition = MedicalCondition.objects.create(
            patient=self.patient,
            condition_name='Diabetes Type 2',
            severity='moderate',
            status='chronic',
            diagnosed_date=date(2020, 1, 1),
            increases_covid_risk=True
        )
        self.assertEqual(condition.condition_name, 'Diabetes Type 2')
        self.assertTrue(condition.increases_covid_risk)
        self.assertEqual(condition.status, 'chronic')

    def test_condition_string_representation(self):
        """Test __str__ method of MedicalCondition"""
        condition = MedicalCondition.objects.create(
            patient=self.patient,
            condition_name='Hypertension',
            diagnosed_date=date(2020, 1, 1)
        )
        expected_str = f"{self.patient.user.get_full_name()} - Hypertension"
        self.assertEqual(str(condition), expected_str)


class AllergyModelTest(TestCase):
    """Tests for Allergy model"""

    def setUp(self):
        self.user = User.objects.create_user(username='testpatient', password='testpass123')
        self.patient = Patient.objects.create(
            user=self.user,
            age=30,
            gender='F',
            date_of_birth=date(1993, 3, 10)
        )

    def test_create_allergy(self):
        """Test creating an allergy"""
        allergy = Allergy.objects.create(
            patient=self.patient,
            allergen='Penicillin',
            allergy_type='medication',
            severity='severe',
            reaction_description='Anaphylaxis',
            is_active=True,
            verified_by_doctor=True
        )
        self.assertEqual(allergy.allergen, 'Penicillin')
        self.assertEqual(allergy.severity, 'severe')
        self.assertTrue(allergy.is_active)


class RiskAssessmentServiceTest(TestCase):
    """Tests for COVID-19 Risk Assessment Service"""

    def setUp(self):
        self.user = User.objects.create_user(username='testpatient', password='testpass123', first_name='John', last_name='Doe')
        self.patient = Patient.objects.create(
            user=self.user,
            age=65,
            gender='M',
            date_of_birth=date(1958, 1, 1)
        )

    def test_age_score_calculation(self):
        """Test age-based risk score calculation"""
        score, description = RiskAssessmentService.calculate_age_score(self.patient)
        self.assertGreater(score, 0)
        self.assertIn('Age', description)

    def test_comorbidity_score_high_risk(self):
        """Test comorbidity score with high-risk conditions"""
        # Create high-risk condition
        MedicalCondition.objects.create(
            patient=self.patient,
            condition_name='Diabetes',
            severity='severe',
            status='chronic',
            diagnosed_date=date(2020, 1, 1),
            increases_covid_risk=True
        )

        score, details = RiskAssessmentService.calculate_comorbidity_score(self.patient)
        self.assertGreater(score, 0)
        self.assertGreater(len(details['high_risk_conditions']), 0)

    def test_vaccination_score_protected(self):
        """Test vaccination score with COVID vaccines"""
        # Create vaccination records
        for i in range(3):
            Vaccination.objects.create(
                patient=self.patient,
                vaccine_name='covid19_pfizer',
                dose_number=i + 1,
                administered_date=date.today() - timedelta(days=60 * i)
            )

        score, details = RiskAssessmentService.calculate_vaccination_score(self.patient)
        self.assertLess(score, 0)  # Negative score means protection
        self.assertEqual(details['covid_doses'], 3)

    def test_vaccination_score_unvaccinated(self):
        """Test vaccination score for unvaccinated patient"""
        score, details = RiskAssessmentService.calculate_vaccination_score(self.patient)
        self.assertGreater(score, 0)  # Positive score means increased risk
        self.assertEqual(details['covid_doses'], 0)

    def test_lifestyle_score_smoking(self):
        """Test lifestyle score with smoking"""
        LifestyleInformation.objects.create(
            patient=self.patient,
            smoking_status='current',
            cigarettes_per_day=20,
            exercise_level='sedentary'
        )

        score, details = RiskAssessmentService.calculate_lifestyle_score(self.patient)
        self.assertGreater(score, 0)
        self.assertIn('Current smoker', details['smoking'])

    def test_complete_risk_assessment(self):
        """Test complete risk score calculation"""
        # Add some conditions
        MedicalCondition.objects.create(
            patient=self.patient,
            condition_name='Hypertension',
            severity='moderate',
            status='chronic',
            diagnosed_date=date(2018, 1, 1),
            increases_covid_risk=True
        )

        # Add lifestyle info
        LifestyleInformation.objects.create(
            patient=self.patient,
            smoking_status='never',
            exercise_level='moderate'
        )

        # Calculate risk
        risk_score = RiskAssessmentService.calculate_risk_score(self.patient, self.user)

        self.assertIsNotNone(risk_score)
        self.assertGreater(risk_score.total_score, 0)
        self.assertIn(risk_score.risk_level, ['low', 'moderate', 'high', 'very_high'])
        self.assertIsNotNone(risk_score.recommendations)


class MedicalRecordsViewsTest(TestCase):
    """Tests for medical records views"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testpatient', password='testpass123')
        self.patient = Patient.objects.create(
            user=self.user,
            age=40,
            gender='M',
            date_of_birth=date(1983, 6, 1)
        )
        self.client.login(username='testpatient', password='testpass123')

    def test_condition_list_view(self):
        """Test condition list view"""
        response = self.client.get(reverse('medical_records:condition_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'medical_records/condition_list.html')

    def test_allergy_list_view(self):
        """Test allergy list view"""
        response = self.client.get(reverse('medical_records:allergy_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'medical_records/allergy_list.html')

    def test_medication_list_view(self):
        """Test medication list view"""
        response = self.client.get(reverse('medical_records:medication_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'medical_records/medication_list.html')

    def test_vaccination_list_view(self):
        """Test vaccination list view"""
        response = self.client.get(reverse('medical_records:vaccination_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'medical_records/vaccination_list.html')

    def test_medical_summary_view(self):
        """Test medical summary view"""
        response = self.client.get(
            reverse('medical_records:medical_summary', kwargs={'patient_id': self.patient.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'medical_records/medical_summary.html')

    def test_unauthorized_access(self):
        """Test that logged-out users cannot access views"""
        self.client.logout()
        response = self.client.get(reverse('medical_records:condition_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
