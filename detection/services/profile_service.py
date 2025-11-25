# detection/services/profile_service.py
"""
Profile Service - Business logic for user profile management.

Provides a proper OOP service class with:
- Instance-based design for flexibility
- Centralized validation via common.validators
- Transaction management for data integrity
- Comprehensive error handling and logging

Follows three-tier architecture (skill #12) - separates business logic from views.

Usage:
    # Instance-based usage (recommended for flexibility)
    service = ProfileService(user)
    result = service.update_basic_info(first_name='John', last_name='Doe', email='john@example.com')

    # Class method usage (for simple operations)
    context = ProfileService.get_profile_context(user)
"""

import logging
from dataclasses import dataclass
from datetime import date
from typing import Dict, Any, Optional, List

from django.contrib.auth.models import User
from django.db import transaction
from django.core.files.uploadedfile import UploadedFile

from common.validators import ProfileValidator, FileValidator
from ..models import UserProfile, Patient
from ..constants import GenderChoices

logger = logging.getLogger(__name__)


class ProfileServiceError(Exception):
    """Base exception for profile service errors."""

    def __init__(self, message: str, errors: Optional[Dict[str, str]] = None):
        super().__init__(message)
        self.message = message
        self.errors = errors or {}


class ProfileValidationError(ProfileServiceError):
    """Raised when profile validation fails."""

    pass


@dataclass
class ServiceResult:
    """
    Standardized result object for service operations.

    Attributes:
        success: Whether the operation succeeded
        message: Human-readable message
        errors: Dict of field -> error message for validation errors
        data: Additional data returned by the operation
    """

    success: bool
    message: str
    errors: Dict[str, str]
    data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "success": self.success,
            "message": self.message,
            "errors": self.errors,
            "data": self.data,
        }


class ProfileService:
    """
    Service class for user profile management.

    Instance-based design allows:
        - Caching of user/profile lookups
        - Consistent user context across operations
        - Easy testing with dependency injection

    Usage:
        # Create service instance for a user
        service = ProfileService(user)

        # Perform operations
        result = service.update_basic_info(
            first_name='John',
            last_name='Doe',
            email='john@example.com'
        )

        if result.success:
            print(result.message)
        else:
            print(result.errors)
    """

    def __init__(self, user: User):
        """
        Initialize service with user context.

        Args:
            user: The Django User instance to operate on
        """
        self._user = user
        self._profile: Optional[UserProfile] = None
        self._patient: Optional[Patient] = None

    @property
    def user(self) -> User:
        """Get the user."""
        return self._user

    @property
    def profile(self) -> UserProfile:
        """Get or fetch the user's profile (cached)."""
        if self._profile is None:
            self._profile = self._user.profile
        return self._profile

    @property
    def patient(self) -> Optional[Patient]:
        """Get or fetch the patient record (cached, None if not a patient)."""
        if self._patient is None and self.profile.is_patient():
            try:
                self._patient = self._user.patient_info
            except Patient.DoesNotExist:
                self._patient = None
        return self._patient

    def _clear_cache(self) -> None:
        """Clear cached profile/patient data after updates."""
        self._profile = None
        self._patient = None

    @transaction.atomic
    def update_basic_info(
        self,
        first_name: str,
        last_name: str,
        email: str,
        phone: str = "",
    ) -> ServiceResult:
        """
        Update basic user information.

        Args:
            first_name: New first name
            last_name: New last name
            email: New email address
            phone: New phone number (optional)

        Returns:
            ServiceResult with success status and any errors
        """
        # Validate using centralized validator
        errors = ProfileValidator.validate_basic_info(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            user_id=self._user.id,
        )

        if errors:
            logger.warning(
                f"Profile validation failed for {self._user.username}: {errors}"
            )
            return ServiceResult(
                success=False,
                message="Please correct the errors below.",
                errors=errors,
            )

        try:
            # Update User model
            self._user.first_name = first_name.strip()
            self._user.last_name = last_name.strip()
            self._user.email = email.strip()
            self._user.save(update_fields=["first_name", "last_name", "email"])

            # Update UserProfile
            self.profile.phone = phone.strip() if phone else ""
            self.profile.save(update_fields=["phone", "updated_at"])

            self._clear_cache()

            logger.info(f"Basic info updated for user {self._user.username}")
            return ServiceResult(
                success=True,
                message="Profile updated successfully!",
                errors={},
            )

        except Exception as e:
            logger.error(f"Error updating basic info: {e}")
            raise ProfileServiceError(f"Failed to update profile: {str(e)}")

    @transaction.atomic
    def update_patient_info(
        self,
        age: int,
        gender: str,
        date_of_birth: Optional[date] = None,
        medical_history: str = "",
        current_medications: str = "",
        emergency_contact: str = "",
        address: str = "",
    ) -> ServiceResult:
        """
        Update patient medical information.

        Args:
            age: Patient age
            gender: Patient gender (M/F/O)
            date_of_birth: Date of birth (optional)
            medical_history: Medical history text
            current_medications: Current medications text
            emergency_contact: Emergency contact info
            address: Patient address

        Returns:
            ServiceResult with success status and any errors
        """
        if not self.profile.is_patient():
            return ServiceResult(
                success=False,
                message="Only patients can update medical information.",
                errors={"__all__": "Permission denied"},
            )

        # Get valid genders from constants
        valid_genders = [choice[0] for choice in GenderChoices.CHOICES]

        # Validate using centralized validator
        errors = ProfileValidator.validate_patient_info(
            age=age,
            gender=gender,
            date_of_birth=date_of_birth,
            emergency_contact=emergency_contact,
            valid_genders=valid_genders,
        )

        if errors:
            return ServiceResult(
                success=False,
                message="Please correct the errors below.",
                errors=errors,
            )

        try:
            # Get or create patient record
            patient, created = Patient.objects.get_or_create(
                user=self._user,
                defaults={"age": 18, "gender": GenderChoices.OTHER},
            )

            # Update fields
            patient.age = age
            patient.gender = gender
            patient.date_of_birth = date_of_birth
            patient.medical_history = medical_history.strip()
            patient.current_medications = current_medications.strip()
            patient.emergency_contact = emergency_contact.strip()
            patient.address = address.strip()
            patient.save()

            self._clear_cache()

            logger.info(f"Patient info updated for user {self._user.username}")
            return ServiceResult(
                success=True,
                message="Medical information updated successfully!",
                errors={},
            )

        except Exception as e:
            logger.error(f"Error updating patient info: {e}")
            raise ProfileServiceError(f"Failed to update patient info: {str(e)}")

    @transaction.atomic
    def update_profile_picture(self, picture_file: UploadedFile) -> ServiceResult:
        """
        Update user profile picture.

        Args:
            picture_file: The uploaded image file

        Returns:
            ServiceResult with success status and any errors
        """
        if not picture_file:
            return ServiceResult(
                success=False,
                message="No file selected.",
                errors={"profile_picture": "Please select an image."},
            )

        # Validate using centralized validator
        error = FileValidator.validate_image(
            picture_file,
            max_size_mb=5,
            allowed_extensions=[".jpg", ".jpeg", ".png"],
            raise_exception=False,
        )

        if error:
            return ServiceResult(
                success=False,
                message="Invalid image file.",
                errors={"profile_picture": error},
            )

        try:
            self.profile.profile_picture = picture_file
            self.profile.save(update_fields=["profile_picture", "updated_at"])

            self._clear_cache()

            logger.info(f"Profile picture updated for user {self._user.username}")
            return ServiceResult(
                success=True,
                message="Profile picture updated successfully!",
                errors={},
            )

        except Exception as e:
            logger.error(f"Error updating profile picture: {e}")
            raise ProfileServiceError(f"Failed to update profile picture: {str(e)}")

    def get_completion_status(self) -> Dict[str, Any]:
        """
        Calculate profile completion percentage and missing fields.

        Returns:
            Dict with:
                - percentage: int (0-100)
                - missing_fields: list of field names
                - is_complete: bool (True if >= 80%)
                - completed_fields: count of completed fields
                - total_fields: total number of fields
        """
        missing_fields: List[str] = []
        total_fields = 0
        completed_fields = 0

        # Basic info fields (required for all users)
        basic_fields = [
            ("first_name", self._user.first_name),
            ("last_name", self._user.last_name),
            ("email", self._user.email),
            ("phone", self.profile.phone),
        ]

        for field_name, value in basic_fields:
            total_fields += 1
            if value and str(value).strip():
                completed_fields += 1
            else:
                missing_fields.append(field_name)

        # Profile picture (optional but counts toward completion)
        total_fields += 1
        if self.profile.profile_picture:
            completed_fields += 1
        else:
            missing_fields.append("profile_picture")

        # Patient-specific fields
        if self.profile.is_patient():
            patient = self.patient
            if patient:
                patient_fields = [
                    ("date_of_birth", patient.date_of_birth),
                    ("emergency_contact", patient.emergency_contact),
                    ("address", patient.address),
                ]

                for field_name, value in patient_fields:
                    total_fields += 1
                    if value and str(value).strip():
                        completed_fields += 1
                    else:
                        missing_fields.append(field_name)
            else:
                # No patient record yet
                missing_fields.extend(["date_of_birth", "emergency_contact", "address"])
                total_fields += 3

        percentage = int((completed_fields / total_fields) * 100) if total_fields > 0 else 0

        return {
            "percentage": percentage,
            "missing_fields": missing_fields,
            "is_complete": percentage >= 80,
            "completed_fields": completed_fields,
            "total_fields": total_fields,
        }

    # =========================================================================
    # Class Methods (for operations that don't need instance state)
    # =========================================================================

    @classmethod
    def get_profile_context(cls, user: User) -> Dict[str, Any]:
        """
        Get all profile-related context for rendering views.

        This is a class method for convenience when you just need context
        without performing updates.

        Args:
            user: The user to get context for

        Returns:
            Dict with profile context data
        """
        service = cls(user)

        context = {
            "user": user,
            "profile": service.profile,
            "is_patient": service.profile.is_patient(),
            "is_staff": service.profile.is_staff(),
            "is_admin": service.profile.is_admin(),
            "completion": service.get_completion_status(),
        }

        # Add patient-specific data
        if service.profile.is_patient():
            patient = service.patient
            if patient:
                context["patient"] = patient
                context["total_xrays"] = patient.get_total_xrays()
                context["covid_positive_count"] = patient.get_covid_positive_count()
            else:
                context["patient"] = None
                context["total_xrays"] = 0
                context["covid_positive_count"] = 0

        return context

    @classmethod
    def get_profile_completion(cls, user: User) -> Dict[str, Any]:
        """
        Convenience class method for getting completion status.

        Args:
            user: The user to check

        Returns:
            Dict with completion data
        """
        service = cls(user)
        return service.get_completion_status()
