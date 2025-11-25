# detection/constants.py
"""
Constants and choices for the Detection module.

Centralizes all magic strings, choice tuples, and configuration values
to ensure consistency and easy maintenance across the module.

Usage:
    from detection.constants import GenderChoices, RoleChoices, DiagnosisChoices

    class Patient(models.Model):
        gender = models.CharField(max_length=1, choices=GenderChoices.CHOICES)
"""

from typing import List, Tuple


class GenderChoices:
    """
    Gender choices for patient profiles.

    Usage in models:
        gender = models.CharField(max_length=1, choices=GenderChoices.CHOICES)

    Usage in forms:
        gender = forms.ChoiceField(choices=GenderChoices.CHOICES)

    Usage in views/templates:
        GenderChoices.get_display(patient.gender)
    """
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"

    CHOICES: List[Tuple[str, str]] = [
        (MALE, "Male"),
        (FEMALE, "Female"),
        (OTHER, "Other"),
    ]

    @classmethod
    def get_display(cls, value: str) -> str:
        """Get display name for a gender value."""
        choice_dict = dict(cls.CHOICES)
        return choice_dict.get(value, "Unknown")


class RoleChoices:
    """
    User role choices for access control.

    Usage in models:
        role = models.CharField(max_length=20, choices=RoleChoices.CHOICES)
    """
    ADMIN = "admin"
    STAFF = "staff"
    PATIENT = "patient"

    CHOICES: List[Tuple[str, str]] = [
        (ADMIN, "Administrator"),
        (STAFF, "Staff"),
        (PATIENT, "Patient"),
    ]

    @classmethod
    def get_display(cls, value: str) -> str:
        """Get display name for a role value."""
        choice_dict = dict(cls.CHOICES)
        return choice_dict.get(value, "Unknown")


class DiagnosisChoices:
    """
    Diagnosis choices for predictions.

    Usage in models:
        final_diagnosis = models.CharField(max_length=50, choices=DiagnosisChoices.CHOICES)
    """
    COVID = "COVID"
    NORMAL = "Normal"
    VIRAL_PNEUMONIA = "Viral Pneumonia"
    LUNG_OPACITY = "Lung Opacity"

    CHOICES: List[Tuple[str, str]] = [
        (COVID, "COVID-19"),
        (NORMAL, "Normal"),
        (VIRAL_PNEUMONIA, "Viral Pneumonia"),
        (LUNG_OPACITY, "Lung Opacity"),
    ]

    # Badge colors for UI display
    BADGE_COLORS = {
        COVID: "danger",
        NORMAL: "success",
        VIRAL_PNEUMONIA: "warning",
        LUNG_OPACITY: "info",
    }

    @classmethod
    def get_display(cls, value: str) -> str:
        """Get display name for a diagnosis value."""
        choice_dict = dict(cls.CHOICES)
        return choice_dict.get(value, "Unknown")

    @classmethod
    def get_badge_color(cls, value: str) -> str:
        """Get Bootstrap badge color for a diagnosis value."""
        return cls.BADGE_COLORS.get(value, "secondary")


class PredictionStatus:
    """
    Status choices for predictions workflow.
    """
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    VALIDATED = "validated"

    CHOICES: List[Tuple[str, str]] = [
        (PENDING, "Pending"),
        (PROCESSING, "Processing"),
        (COMPLETED, "Completed"),
        (FAILED, "Failed"),
        (VALIDATED, "Validated"),
    ]


# Validation constants
class ValidationLimits:
    """
    Validation limits and constraints.
    """
    # Age limits
    MIN_AGE = 0
    MAX_AGE = 120

    # File size limits (in MB)
    MAX_PROFILE_PICTURE_SIZE_MB = 5
    MAX_XRAY_SIZE_MB = 10

    # Text field limits
    MAX_MEDICAL_HISTORY_LENGTH = 2000
    MAX_MEDICATIONS_LENGTH = 1000
    MAX_ADDRESS_LENGTH = 500
    MAX_EMERGENCY_CONTACT_LENGTH = 100

    # Name limits
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 150


# Profile field display names for UI
class ProfileFieldDisplayNames:
    """
    Human-readable display names for profile fields.

    Used in profile completion banner, validation messages, and forms.

    Usage:
        from detection.constants import ProfileFieldDisplayNames

        display_name = ProfileFieldDisplayNames.get_display('date_of_birth')
        # Returns: 'Date of Birth'
    """
    # Field name to display name mapping
    FIELD_NAMES = {
        # User model fields
        'email': 'Email',
        'first_name': 'First Name',
        'last_name': 'Last Name',
        'username': 'Username',
        # Patient model fields
        'date_of_birth': 'Date of Birth',
        'emergency_contact': 'Emergency Contact',
        'gender': 'Gender',
        'phone': 'Phone Number',
        'address': 'Address',
        'age': 'Age',
        'medical_history': 'Medical History',
        'current_medications': 'Current Medications',
        # UserProfile fields
        'profile_picture': 'Profile Picture',
        'bio': 'Bio',
    }

    @classmethod
    def get_display(cls, field_name: str) -> str:
        """
        Get human-readable display name for a field.

        Args:
            field_name: The model field name (e.g., 'date_of_birth')

        Returns:
            Human-readable name (e.g., 'Date of Birth')
            Falls back to title-cased field name if not found.
        """
        return cls.FIELD_NAMES.get(
            field_name,
            field_name.replace('_', ' ').title()
        )


# Model names for ML predictions
class ModelNames:
    """
    ML model names for prediction display.
    """
    CROSSVIT = "CrossViT"
    RESNET50 = "ResNet-50"
    DENSENET121 = "DenseNet-121"
    EFFICIENTNET = "EfficientNet-B0"
    VIT = "ViT-Base"
    SWIN = "Swin-Tiny"

    ALL_MODELS: List[str] = [
        CROSSVIT,
        RESNET50,
        DENSENET121,
        EFFICIENTNET,
        VIT,
        SWIN,
    ]
