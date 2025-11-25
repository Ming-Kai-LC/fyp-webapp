# common/validators.py
"""
Centralized validation classes for the COVID-19 Detection application.

Provides reusable, class-based validators that can be used in:
- Django forms (as form validators)
- Django models (as model validators)
- Django REST Framework serializers
- Service layer validation

Usage:
    from common.validators import ProfileValidator, FileValidator

    # In forms
    class MyForm(forms.Form):
        email = forms.EmailField(validators=[ProfileValidator.validate_email])

    # In services
    errors = ProfileValidator.validate_basic_info(first_name, last_name, email)
"""

import re
from datetime import date
from typing import Dict, List, Any, Optional

from django.core.exceptions import ValidationError
from django.core.validators import validate_email as django_validate_email
from django.contrib.auth.models import User


class BaseValidator:
    """
    Base class for all validators.

    Provides common validation patterns and error formatting.
    """

    @classmethod
    def create_error(cls, field: str, message: str) -> Dict[str, str]:
        """Create a standardized error dict."""
        return {field: message}

    @classmethod
    def merge_errors(cls, *error_dicts: Dict[str, str]) -> Dict[str, str]:
        """Merge multiple error dicts into one."""
        merged = {}
        for error_dict in error_dicts:
            if error_dict:
                merged.update(error_dict)
        return merged


class ProfileValidator(BaseValidator):
    """
    Validator for user profile fields.

    Provides validation for:
        - Names (first_name, last_name)
        - Email (format and uniqueness)
        - Phone (Malaysian format)
        - Age (range validation)
        - Date of birth (past date validation)

    Usage:
        # Validate single field
        ProfileValidator.validate_first_name("John")

        # Validate multiple fields at once
        errors = ProfileValidator.validate_basic_info(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            user_id=1  # For uniqueness check
        )
        if errors:
            raise ValidationError(errors)
    """

    # Validation constants
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 150
    MIN_AGE = 0
    MAX_AGE = 120
    MAX_EMAIL_LENGTH = 254

    # Malaysian phone patterns
    PHONE_PATTERNS = [
        r"^\+60\d{9,10}$",  # +60123456789
        r"^0\d{9,10}$",  # 0123456789
        r"^60\d{9,10}$",  # 60123456789
    ]

    # Name pattern (letters, spaces, hyphens, apostrophes)
    NAME_PATTERN = r"^[a-zA-Z\s'-]+$"

    @classmethod
    def validate_first_name(cls, value: str, raise_exception: bool = True) -> Optional[str]:
        """
        Validate first name.

        Args:
            value: First name to validate
            raise_exception: If True, raises ValidationError on failure

        Returns:
            Error message if invalid and raise_exception=False, None if valid

        Raises:
            ValidationError: If invalid and raise_exception=True
        """
        if not value or not value.strip():
            error = "First name is required."
            if raise_exception:
                raise ValidationError(error)
            return error

        value = value.strip()

        if len(value) < cls.MIN_NAME_LENGTH:
            error = f"First name must be at least {cls.MIN_NAME_LENGTH} characters."
            if raise_exception:
                raise ValidationError(error)
            return error

        if len(value) > cls.MAX_NAME_LENGTH:
            error = f"First name cannot exceed {cls.MAX_NAME_LENGTH} characters."
            if raise_exception:
                raise ValidationError(error)
            return error

        if not re.match(cls.NAME_PATTERN, value):
            error = "First name can only contain letters, spaces, hyphens, and apostrophes."
            if raise_exception:
                raise ValidationError(error)
            return error

        return None

    @classmethod
    def validate_last_name(cls, value: str, raise_exception: bool = True) -> Optional[str]:
        """
        Validate last name.

        Args:
            value: Last name to validate
            raise_exception: If True, raises ValidationError on failure

        Returns:
            Error message if invalid and raise_exception=False, None if valid
        """
        if not value or not value.strip():
            error = "Last name is required."
            if raise_exception:
                raise ValidationError(error)
            return error

        value = value.strip()

        if len(value) < cls.MIN_NAME_LENGTH:
            error = f"Last name must be at least {cls.MIN_NAME_LENGTH} characters."
            if raise_exception:
                raise ValidationError(error)
            return error

        if len(value) > cls.MAX_NAME_LENGTH:
            error = f"Last name cannot exceed {cls.MAX_NAME_LENGTH} characters."
            if raise_exception:
                raise ValidationError(error)
            return error

        if not re.match(cls.NAME_PATTERN, value):
            error = "Last name can only contain letters, spaces, hyphens, and apostrophes."
            if raise_exception:
                raise ValidationError(error)
            return error

        return None

    @classmethod
    def validate_email(
        cls,
        value: str,
        user_id: Optional[int] = None,
        raise_exception: bool = True,
    ) -> Optional[str]:
        """
        Validate email format and uniqueness.

        Args:
            value: Email to validate
            user_id: Current user's ID (for uniqueness check, excludes self)
            raise_exception: If True, raises ValidationError on failure

        Returns:
            Error message if invalid and raise_exception=False, None if valid
        """
        if not value or not value.strip():
            error = "Email is required."
            if raise_exception:
                raise ValidationError(error)
            return error

        value = value.strip()

        # Check format
        try:
            django_validate_email(value)
        except ValidationError:
            error = "Enter a valid email address."
            if raise_exception:
                raise ValidationError(error)
            return error

        # Check length
        if len(value) > cls.MAX_EMAIL_LENGTH:
            error = f"Email cannot exceed {cls.MAX_EMAIL_LENGTH} characters."
            if raise_exception:
                raise ValidationError(error)
            return error

        # Check uniqueness
        query = User.objects.filter(email=value)
        if user_id:
            query = query.exclude(id=user_id)

        if query.exists():
            error = "This email is already registered."
            if raise_exception:
                raise ValidationError(error)
            return error

        return None

    @classmethod
    def validate_phone(cls, value: str, raise_exception: bool = True) -> Optional[str]:
        """
        Validate Malaysian phone number format.

        Args:
            value: Phone number to validate
            raise_exception: If True, raises ValidationError on failure

        Returns:
            Error message if invalid and raise_exception=False, None if valid
        """
        if not value or not value.strip():
            return None  # Phone is optional

        # Remove spaces and dashes for validation
        cleaned = re.sub(r"[\s-]", "", value)

        for pattern in cls.PHONE_PATTERNS:
            if re.match(pattern, cleaned):
                return None

        error = "Invalid phone format. Use Malaysian format (e.g., 012-3456-7890)."
        if raise_exception:
            raise ValidationError(error)
        return error

    @classmethod
    def validate_age(cls, value: int, raise_exception: bool = True) -> Optional[str]:
        """
        Validate age is within acceptable range.

        Args:
            value: Age to validate
            raise_exception: If True, raises ValidationError on failure

        Returns:
            Error message if invalid and raise_exception=False, None if valid
        """
        if value is None:
            error = "Age is required."
            if raise_exception:
                raise ValidationError(error)
            return error

        if value < cls.MIN_AGE:
            error = "Age cannot be negative."
            if raise_exception:
                raise ValidationError(error)
            return error

        if value > cls.MAX_AGE:
            error = f"Age cannot exceed {cls.MAX_AGE}."
            if raise_exception:
                raise ValidationError(error)
            return error

        return None

    @classmethod
    def validate_date_of_birth(
        cls,
        value: date,
        raise_exception: bool = True,
    ) -> Optional[str]:
        """
        Validate date of birth is in the past.

        Args:
            value: Date of birth to validate
            raise_exception: If True, raises ValidationError on failure

        Returns:
            Error message if invalid and raise_exception=False, None if valid
        """
        if not value:
            return None  # DOB is optional

        if value > date.today():
            error = "Date of birth cannot be in the future."
            if raise_exception:
                raise ValidationError(error)
            return error

        # Check if age is reasonable
        age = (date.today() - value).days // 365
        if age > cls.MAX_AGE:
            error = f"Date of birth results in age over {cls.MAX_AGE}."
            if raise_exception:
                raise ValidationError(error)
            return error

        return None

    @classmethod
    def validate_emergency_contact(
        cls,
        value: str,
        raise_exception: bool = True,
    ) -> Optional[str]:
        """
        Validate emergency contact format.

        Args:
            value: Emergency contact to validate
            raise_exception: If True, raises ValidationError on failure

        Returns:
            Error message if invalid and raise_exception=False, None if valid
        """
        if not value or not value.strip():
            return None  # Emergency contact is optional

        if len(value.strip()) < 5:
            error = "Emergency contact must include name and phone number."
            if raise_exception:
                raise ValidationError(error)
            return error

        return None

    @classmethod
    def validate_basic_info(
        cls,
        first_name: str,
        last_name: str,
        email: str,
        phone: str = "",
        user_id: Optional[int] = None,
    ) -> Dict[str, str]:
        """
        Validate all basic info fields at once.

        Args:
            first_name: First name
            last_name: Last name
            email: Email address
            phone: Phone number (optional)
            user_id: Current user's ID for uniqueness check

        Returns:
            Dict of field -> error message for any invalid fields
        """
        errors = {}

        error = cls.validate_first_name(first_name, raise_exception=False)
        if error:
            errors["first_name"] = error

        error = cls.validate_last_name(last_name, raise_exception=False)
        if error:
            errors["last_name"] = error

        error = cls.validate_email(email, user_id=user_id, raise_exception=False)
        if error:
            errors["email"] = error

        error = cls.validate_phone(phone, raise_exception=False)
        if error:
            errors["phone"] = error

        return errors

    @classmethod
    def validate_patient_info(
        cls,
        age: int,
        gender: str,
        date_of_birth: Optional[date] = None,
        emergency_contact: str = "",
        valid_genders: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """
        Validate all patient info fields at once.

        Args:
            age: Patient age
            gender: Patient gender
            date_of_birth: Date of birth (optional)
            emergency_contact: Emergency contact (optional)
            valid_genders: List of valid gender values

        Returns:
            Dict of field -> error message for any invalid fields
        """
        errors = {}

        error = cls.validate_age(age, raise_exception=False)
        if error:
            errors["age"] = error

        # Validate gender
        if valid_genders is None:
            valid_genders = ["M", "F", "O"]

        if gender not in valid_genders:
            errors["gender"] = "Invalid gender selection."

        error = cls.validate_date_of_birth(date_of_birth, raise_exception=False)
        if error:
            errors["date_of_birth"] = error

        error = cls.validate_emergency_contact(emergency_contact, raise_exception=False)
        if error:
            errors["emergency_contact"] = error

        return errors


class FileValidator(BaseValidator):
    """
    Validator for file uploads.

    Provides validation for:
        - File size
        - File type/extension
        - Image dimensions

    Usage:
        # Validate image file
        FileValidator.validate_image(uploaded_file, max_size_mb=5)

        # Validate with custom extensions
        FileValidator.validate_file(
            file,
            max_size_mb=10,
            allowed_extensions=['.pdf', '.doc', '.docx']
        )
    """

    # Common image extensions
    IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]

    # Common document extensions
    DOCUMENT_EXTENSIONS = [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt"]

    # Image MIME types
    IMAGE_MIME_TYPES = [
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/bmp",
        "image/webp",
    ]

    @classmethod
    def validate_file_size(
        cls,
        file: Any,
        max_size_mb: int = 10,
        raise_exception: bool = True,
    ) -> Optional[str]:
        """
        Validate file size.

        Args:
            file: Uploaded file object
            max_size_mb: Maximum size in megabytes
            raise_exception: If True, raises ValidationError on failure

        Returns:
            Error message if invalid and raise_exception=False, None if valid
        """
        if not file:
            return None

        max_size_bytes = max_size_mb * 1024 * 1024

        if file.size > max_size_bytes:
            error = f"File too large. Maximum size: {max_size_mb}MB."
            if raise_exception:
                raise ValidationError(error)
            return error

        return None

    @classmethod
    def validate_file_extension(
        cls,
        file: Any,
        allowed_extensions: List[str],
        raise_exception: bool = True,
    ) -> Optional[str]:
        """
        Validate file extension.

        Args:
            file: Uploaded file object
            allowed_extensions: List of allowed extensions (e.g., ['.jpg', '.png'])
            raise_exception: If True, raises ValidationError on failure

        Returns:
            Error message if invalid and raise_exception=False, None if valid
        """
        if not file:
            return None

        import os

        ext = os.path.splitext(file.name)[1].lower()

        if ext not in [e.lower() for e in allowed_extensions]:
            error = f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            if raise_exception:
                raise ValidationError(error)
            return error

        return None

    @classmethod
    def validate_image(
        cls,
        file: Any,
        max_size_mb: int = 5,
        allowed_extensions: Optional[List[str]] = None,
        raise_exception: bool = True,
    ) -> Optional[str]:
        """
        Validate image file (size and type).

        Args:
            file: Uploaded image file
            max_size_mb: Maximum size in megabytes
            allowed_extensions: Allowed extensions (defaults to IMAGE_EXTENSIONS)
            raise_exception: If True, raises ValidationError on failure

        Returns:
            Error message if invalid and raise_exception=False, None if valid
        """
        if not file:
            return None

        if allowed_extensions is None:
            allowed_extensions = cls.IMAGE_EXTENSIONS

        # Check extension
        error = cls.validate_file_extension(file, allowed_extensions, raise_exception=False)
        if error:
            if raise_exception:
                raise ValidationError(error)
            return error

        # Check size
        error = cls.validate_file_size(file, max_size_mb, raise_exception=False)
        if error:
            if raise_exception:
                raise ValidationError(error)
            return error

        return None

    @classmethod
    def validate_xray_image(
        cls,
        file: Any,
        max_size_mb: int = 10,
        raise_exception: bool = True,
    ) -> Optional[str]:
        """
        Validate X-ray image file.

        Args:
            file: Uploaded X-ray image
            max_size_mb: Maximum size in megabytes
            raise_exception: If True, raises ValidationError on failure

        Returns:
            Error message if invalid and raise_exception=False, None if valid
        """
        # X-rays typically only in JPEG or PNG
        allowed = [".jpg", ".jpeg", ".png"]
        return cls.validate_image(file, max_size_mb, allowed, raise_exception)


class NRICValidator(BaseValidator):
    """
    Validator for Malaysian NRIC numbers.

    NRIC format: YYMMDD-PB-###G (12 digits)

    Usage:
        NRICValidator.validate("901231-01-1234")
    """

    @classmethod
    def validate(cls, value: str, raise_exception: bool = True) -> Optional[str]:
        """
        Validate Malaysian NRIC format.

        Args:
            value: NRIC number to validate
            raise_exception: If True, raises ValidationError on failure

        Returns:
            Error message if invalid and raise_exception=False, None if valid
        """
        if not value or not value.strip():
            error = "NRIC is required."
            if raise_exception:
                raise ValidationError(error)
            return error

        # Remove dashes
        cleaned = value.replace("-", "")

        # Must be 12 digits
        if not re.match(r"^\d{12}$", cleaned):
            error = "Invalid NRIC format. Use YYMMDD-PB-####."
            if raise_exception:
                raise ValidationError(error)
            return error

        # Validate date components
        try:
            month = int(cleaned[2:4])
            day = int(cleaned[4:6])

            if not (1 <= month <= 12):
                raise ValueError("Invalid month")
            if not (1 <= day <= 31):
                raise ValueError("Invalid day")

        except ValueError:
            error = "Invalid date in NRIC."
            if raise_exception:
                raise ValidationError(error)
            return error

        return None
