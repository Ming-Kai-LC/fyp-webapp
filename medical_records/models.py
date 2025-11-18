from django.db import models
from django.conf import settings
from detection.models import Patient
from django.core.validators import FileExtensionValidator
import uuid


class MedicalCondition(models.Model):
    """
    Track patient's medical conditions and diagnoses
    """
    SEVERITY_CHOICES = (
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
    )

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('resolved', 'Resolved'),
        ('chronic', 'Chronic'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_conditions')
    condition_name = models.CharField(max_length=200)
    icd_code = models.CharField(max_length=20, blank=True, help_text="ICD-10 code")
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='mild')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Timeline
    diagnosed_date = models.DateField()
    resolved_date = models.DateField(null=True, blank=True)

    # Details
    description = models.TextField(blank=True)
    symptoms = models.TextField(blank=True)
    treatment = models.TextField(blank=True)

    # Risk assessment
    increases_covid_risk = models.BooleanField(
        default=False,
        help_text="Whether this condition increases COVID-19 risk"
    )

    # Metadata
    diagnosed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='diagnosed_conditions'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-diagnosed_date']

    def __str__(self):
        return f"{self.patient.user.get_full_name()} - {self.condition_name}"


class Allergy(models.Model):
    """
    Track patient allergies for safety
    """
    SEVERITY_CHOICES = (
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe/Anaphylaxis'),
    )

    ALLERGY_TYPES = (
        ('medication', 'Medication'),
        ('food', 'Food'),
        ('environmental', 'Environmental'),
        ('other', 'Other'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='allergies')
    allergen = models.CharField(max_length=200)
    allergy_type = models.CharField(max_length=20, choices=ALLERGY_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)

    # Reaction details
    reaction_description = models.TextField()
    onset_date = models.DateField(null=True, blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    verified_by_doctor = models.BooleanField(default=False)

    # Metadata
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-severity', 'allergen']
        verbose_name_plural = "Allergies"

    def __str__(self):
        return f"{self.patient.user.get_full_name()} - {self.allergen} ({self.severity})"


class Medication(models.Model):
    """
    Track current and past medications
    """
    STATUS_CHOICES = (
        ('current', 'Currently Taking'),
        ('discontinued', 'Discontinued'),
        ('completed', 'Course Completed'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medications')
    medication_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100, help_text="e.g., 'Twice daily', '3x per day'")
    route = models.CharField(
        max_length=50,
        default='oral',
        help_text="e.g., oral, injection, topical"
    )

    # Timeline
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='current')

    # Details
    purpose = models.CharField(max_length=200, help_text="Reason for taking medication")
    prescribing_doctor = models.CharField(max_length=200, blank=True)
    side_effects = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    # Metadata
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.medication_name} - {self.dosage}"


class Vaccination(models.Model):
    """
    Track vaccination records, especially COVID-19 vaccines
    """
    VACCINE_TYPES = (
        ('covid19_pfizer', 'COVID-19 Pfizer-BioNTech'),
        ('covid19_moderna', 'COVID-19 Moderna'),
        ('covid19_astrazeneca', 'COVID-19 AstraZeneca'),
        ('covid19_sinovac', 'COVID-19 Sinovac'),
        ('covid19_sinopharm', 'COVID-19 Sinopharm'),
        ('covid19_other', 'COVID-19 Other'),
        ('influenza', 'Influenza'),
        ('pneumococcal', 'Pneumococcal'),
        ('other', 'Other'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='vaccinations')
    vaccine_name = models.CharField(max_length=50, choices=VACCINE_TYPES)
    vaccine_brand = models.CharField(max_length=100, blank=True)
    dose_number = models.IntegerField(help_text="Which dose (1st, 2nd, 3rd, etc.)")
    lot_number = models.CharField(max_length=100, blank=True)

    # Administration
    administered_date = models.DateField()
    administered_by = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True, help_text="Clinic/hospital name")

    # Side effects
    side_effects = models.TextField(blank=True)
    adverse_reaction = models.BooleanField(default=False)

    # Verification
    verification_document = models.FileField(
        upload_to='medical_records/vaccination_certificates/%Y/%m/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])]
    )

    # Metadata
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-administered_date']

    def __str__(self):
        return f"{self.patient.user.get_full_name()} - {self.get_vaccine_name_display()} Dose {self.dose_number}"


class Surgery(models.Model):
    """
    Track surgical history
    """
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='surgeries')
    surgery_name = models.CharField(max_length=200)
    procedure_code = models.CharField(max_length=50, blank=True, help_text="CPT code")

    # Timeline
    surgery_date = models.DateField()

    # Details
    surgeon_name = models.CharField(max_length=200, blank=True)
    hospital = models.CharField(max_length=200, blank=True)
    reason = models.TextField()
    complications = models.TextField(blank=True)
    outcome = models.TextField(blank=True)

    # Metadata
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-surgery_date']
        verbose_name_plural = "Surgeries"

    def __str__(self):
        return f"{self.surgery_name} - {self.surgery_date}"


class FamilyHistory(models.Model):
    """
    Track family medical history for risk assessment
    """
    RELATIONSHIP_CHOICES = (
        ('mother', 'Mother'),
        ('father', 'Father'),
        ('sibling', 'Sibling'),
        ('grandparent', 'Grandparent'),
        ('child', 'Child'),
        ('other', 'Other'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='family_history')
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    condition = models.CharField(max_length=200)
    age_at_diagnosis = models.IntegerField(null=True, blank=True)
    is_deceased = models.BooleanField(default=False)
    cause_of_death = models.CharField(max_length=200, blank=True)

    # Details
    notes = models.TextField(blank=True)

    # Metadata
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Family Histories"

    def __str__(self):
        return f"{self.patient.user.get_full_name()} - {self.relationship}: {self.condition}"


class MedicalDocument(models.Model):
    """
    Store medical documents (lab results, prescriptions, etc.)
    """
    DOCUMENT_TYPES = (
        ('lab_result', 'Lab Result'),
        ('prescription', 'Prescription'),
        ('discharge_summary', 'Discharge Summary'),
        ('radiology', 'Radiology Report'),
        ('vaccination_cert', 'Vaccination Certificate'),
        ('insurance', 'Insurance Document'),
        ('consent_form', 'Consent Form'),
        ('other', 'Other'),
    )

    document_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_documents')
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # File
    file = models.FileField(
        upload_to='medical_records/documents/%Y/%m/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'])]
    )
    file_size = models.IntegerField(null=True, blank=True)

    # Metadata
    document_date = models.DateField(help_text="Date of the document (not upload date)")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_documents'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # OCR extracted text (for searchability)
    extracted_text = models.TextField(blank=True)

    # Access control
    is_sensitive = models.BooleanField(
        default=False,
        help_text="Requires additional authorization to view"
    )

    # Version control
    version = models.IntegerField(default=1)
    replaces = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replaced_by'
    )

    class Meta:
        ordering = ['-document_date']

    def __str__(self):
        return f"{self.title} - {self.document_date}"

    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)


class LifestyleInformation(models.Model):
    """
    Track lifestyle factors relevant to COVID-19 risk
    """
    SMOKING_STATUS = (
        ('never', 'Never Smoked'),
        ('former', 'Former Smoker'),
        ('current', 'Current Smoker'),
    )

    ALCOHOL_USE = (
        ('none', 'None'),
        ('occasional', 'Occasional'),
        ('moderate', 'Moderate'),
        ('heavy', 'Heavy'),
    )

    EXERCISE_LEVEL = (
        ('sedentary', 'Sedentary'),
        ('light', 'Light Activity'),
        ('moderate', 'Moderate Activity'),
        ('active', 'Very Active'),
    )

    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='lifestyle_info')

    # Smoking
    smoking_status = models.CharField(max_length=20, choices=SMOKING_STATUS, default='never')
    cigarettes_per_day = models.IntegerField(null=True, blank=True)
    years_smoked = models.IntegerField(null=True, blank=True)
    quit_date = models.DateField(null=True, blank=True)

    # Alcohol
    alcohol_use = models.CharField(max_length=20, choices=ALCOHOL_USE, default='none')
    drinks_per_week = models.IntegerField(null=True, blank=True)

    # Exercise
    exercise_level = models.CharField(max_length=20, choices=EXERCISE_LEVEL, default='sedentary')
    exercise_hours_per_week = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)

    # Other
    occupation = models.CharField(max_length=200, blank=True)
    occupational_exposure_risk = models.BooleanField(
        default=False,
        help_text="High risk of COVID-19 exposure at work"
    )

    # Metadata
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.patient.user.get_full_name()} - Lifestyle Information"


class COVIDRiskScore(models.Model):
    """
    Calculate and store COVID-19 risk scores based on patient history
    """
    RISK_LEVELS = (
        ('low', 'Low Risk'),
        ('moderate', 'Moderate Risk'),
        ('high', 'High Risk'),
        ('very_high', 'Very High Risk'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='risk_scores')
    calculated_at = models.DateTimeField(auto_now_add=True)
    calculated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Risk factors
    age_score = models.IntegerField(default=0)
    comorbidity_score = models.IntegerField(default=0)
    lifestyle_score = models.IntegerField(default=0)
    vaccination_score = models.IntegerField(default=0)

    # Total score and level
    total_score = models.IntegerField()
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS)

    # Factors breakdown (JSON)
    risk_factors = models.JSONField(help_text="Detailed breakdown of risk factors")

    # Recommendations
    recommendations = models.TextField()

    class Meta:
        ordering = ['-calculated_at']

    def __str__(self):
        return f"{self.patient.user.get_full_name()} - {self.get_risk_level_display()} ({self.total_score})"
