# detection/forms.py
"""
Django Forms for COVID-19 Detection System

Implements dual-layer validation (client-side + server-side) as per skill #8.
Uses foundation components (common/widgets.py) for UI consistency.
"""

from datetime import date
from typing import Optional

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile

from common.widgets import (
    BootstrapTextInput,
    BootstrapEmailInput,
    BootstrapPasswordInput,
    BootstrapTextarea,
    BootstrapFileInput,
    BootstrapNumberInput,
    BootstrapSelect,
    BootstrapDateInput,
)
from .models import XRayImage, Patient, UserProfile


class XRayUploadForm(forms.ModelForm):
    """Form for uploading X-ray images"""

    class Meta:
        model = XRayImage
        fields = ["original_image", "notes"]
        widgets = {
            "original_image": BootstrapFileInput(attrs={
                "accept": "image/*",
                "required": True
            }),
            "notes": BootstrapTextarea(attrs={
                "rows": 3,
                "placeholder": "Optional clinical notes or observations...",
            }),
        }
        labels = {
            "original_image": "Chest X-ray Image",
            "notes": "Clinical Notes (Optional)",
        }


class UserRegistrationForm(UserCreationForm):
    """
    Patient registration form for public self-registration.

    Security Policy (user-role-permissions skill):
    - Public registration creates PATIENT accounts ONLY
    - Staff/Admin accounts must be created through admin panel
    - Role is hardcoded to 'patient' - no user input accepted

    Validation Strategy (dual-layer-validation skill):
    - Server-side: Django validation (clean methods, validators)
    - Client-side: HTML5 attributes + JavaScript (in template)
    - Both layers required for security + UX
    """

    email = forms.EmailField(
        required=True,
        widget=BootstrapEmailInput(attrs={
            "placeholder": "yourname@example.com",
            "autocomplete": "email",
            "maxlength": "254"
        }),
        help_text="Enter a valid email address (e.g., john@gmail.com). We'll use this for important health notifications.",
        error_messages={
            'required': 'Email address is required.',
            'invalid': 'Please enter a valid email address (e.g., yourname@example.com).',
        }
    )

    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=BootstrapTextInput(attrs={
            "placeholder": "e.g., John or Wei Ming",
            "autocomplete": "given-name",
            "minlength": "2",
            "maxlength": "150",
            "pattern": r"[a-zA-Z\s'\-]+",
            "title": "Only letters, spaces, hyphens, and apostrophes allowed"
        }),
        help_text="Your legal first name (letters only, at least 2 characters)",
        error_messages={
            'required': 'First name is required.',
        }
    )

    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=BootstrapTextInput(attrs={
            "placeholder": "e.g., Doe or Abdullah",
            "autocomplete": "family-name",
            "minlength": "2",
            "maxlength": "150",
            "pattern": r"[a-zA-Z\s'\-]+",
            "title": "Only letters, spaces, hyphens, and apostrophes allowed"
        }),
        help_text="Your legal last name (letters only, at least 2 characters)",
        error_messages={
            'required': 'Last name is required.',
        }
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Customize username field
        self.fields["username"].widget = BootstrapTextInput(attrs={
            "placeholder": "e.g., john_doe or user2024",
            "autocomplete": "username",
            "minlength": "3",
            "maxlength": "150",
            "pattern": "[a-zA-Z0-9@.+_-]+",
            "title": "Only letters, digits, and symbols @ . + - _ are allowed"
        })
        self.fields["username"].help_text = "3-150 characters. Use letters (a-z), digits (0-9), and symbols: @ . + - _ only."
        self.fields["username"].label = "Username"
        self.fields["username"].error_messages = {
            'required': 'Username is required. Please choose a unique username.',
            'invalid': 'Enter a valid username.',
            'unique': 'This username is already taken.',
        }

        # Customize password1 field
        self.fields["password1"].widget = BootstrapPasswordInput(attrs={
            "placeholder": "e.g., MyPass123 or SecurePass2024",
            "autocomplete": "new-password",
            "minlength": "8"
        })
        self.fields["password1"].help_text = (
            "Create a strong password: At least 8 characters, include letters and numbers (e.g., 'MyPass123')."
        )
        self.fields["password1"].label = "Password"
        self.fields["password1"].error_messages = {
            'required': 'Password is required.',
        }

        # Customize password2 field
        self.fields["password2"].widget = BootstrapPasswordInput(attrs={
            "placeholder": "Re-type your password",
            "autocomplete": "new-password",
            "minlength": "8"
        })
        self.fields["password2"].help_text = "Type the same password again to confirm"
        self.fields["password2"].label = "Confirm Password"
        self.fields["password2"].error_messages = {
            'required': 'Please confirm your password by typing it again.',
        }

    def clean_email(self):
        """
        Server-side validation: Ensure email is unique.

        Normalization:
            - Strip leading/trailing whitespace
            - Convert to lowercase (emails are case-insensitive per RFC 5321)

        Raises:
            ValidationError: If email already exists
        """
        email = self.cleaned_data.get('email', '').strip().lower()

        if not email:
            raise ValidationError(
                "Email address is required. Please enter a valid email (e.g., 'yourname@example.com' or 'user@gmail.com').",
                code='required'
            )

        # Case-insensitive uniqueness check
        if email and User.objects.filter(email__iexact=email).exists():
            raise ValidationError(
                "The email '{}' is already registered. Please use a different email address or login to your existing account at the login page.".format(email),
                code='duplicate'
            )
        return email

    def clean_username(self):
        """
        Server-side validation: Username requirements.

        Normalization:
            - Strip leading/trailing whitespace
            - Convert to lowercase (usernames are case-insensitive)

        Raises:
            ValidationError: If username is invalid or already exists
        """
        username = self.cleaned_data.get('username', '').strip().lower()

        # Length validation
        if len(username) < 3:
            raise ValidationError(
                "Username is too short. Please use at least 3 characters (e.g., 'john_doe' or 'user123').",
                code='too_short'
            )

        if len(username) > 150:
            raise ValidationError(
                "Username is too long. Please use 150 characters or less.",
                code='too_long'
            )

        # Pattern validation (alphanumeric + @/./+/-/_)
        import re
        if not re.match(r'^[a-zA-Z0-9@.+_-]+$', username):
            raise ValidationError(
                "Username contains invalid characters. Only letters (a-z, A-Z), digits (0-9), and these symbols are allowed: @ . + - _  (Example: 'john.doe' or 'user_2024')",
                code='invalid_pattern'
            )

        # Case-insensitive uniqueness validation
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError(
                "This username '{}' is already taken. Please try a different one (e.g., '{}_2', '{}24', or a completely different name).".format(
                    username, username, username
                ),
                code='duplicate'
            )

        return username

    def clean_first_name(self):
        """
        Server-side validation: First name requirements.

        Normalization:
            - Strip leading/trailing whitespace
            - Convert to title case (e.g., 'john' -> 'John', 'wei ming' -> 'Wei Ming')
        """
        import re

        first_name = self.cleaned_data.get('first_name', '').strip()

        if not first_name:
            raise ValidationError(
                "First name is required. Please enter your legal first name (e.g., 'John', 'Wei Ming').",
                code='required'
            )

        if len(first_name) < 2:
            raise ValidationError(
                "First name is too short. Please use at least 2 characters (e.g., 'Li', 'John', 'Wei').",
                code='too_short'
            )

        # Only allow letters, spaces, hyphens, and apostrophes (for names like O'Brien, Lee-Ann, Tan Ming Kai)
        if not re.match(r"^[a-zA-Z\s'-]+$", first_name):
            raise ValidationError(
                "First name can only contain letters, spaces, hyphens, and apostrophes. Numbers and special characters are not allowed. (e.g., 'Ahmad', 'Wei Ming', 'O\'Brien', 'Lee-Ann')",
                code='invalid_characters'
            )

        # Normalize to title case
        return first_name.title()

    def clean_last_name(self):
        """
        Server-side validation: Last name requirements.

        Normalization:
            - Strip leading/trailing whitespace
            - Convert to title case (e.g., 'doe' -> 'Doe', 'bin ahmad' -> 'Bin Ahmad')
        """
        import re

        last_name = self.cleaned_data.get('last_name', '').strip()

        if not last_name:
            raise ValidationError(
                "Last name is required. Please enter your legal last name (e.g., 'Doe', 'Tan', 'Abdullah').",
                code='required'
            )

        if len(last_name) < 2:
            raise ValidationError(
                "Last name is too short. Please use at least 2 characters (e.g., 'Ng', 'Lee', 'Tan').",
                code='too_short'
            )

        # Only allow letters, spaces, hyphens, and apostrophes (for names like O'Brien, Abdullah bin Ahmad)
        if not re.match(r"^[a-zA-Z\s'-]+$", last_name):
            raise ValidationError(
                "Last name can only contain letters, spaces, hyphens, and apostrophes. Numbers and special characters are not allowed. (e.g., 'Tan', 'bin Ahmad', 'O\'Connor', 'Lee-Smith')",
                code='invalid_characters'
            )

        # Normalize to title case
        return last_name.title()

    def clean_password1(self):
        """
        Server-side validation: Password strength requirements.

        Raises:
            ValidationError: If password doesn't meet requirements
        """
        password = self.cleaned_data.get('password1')

        # Minimum length
        if len(password) < 8:
            raise ValidationError(
                "Password is too short. Please use at least 8 characters. Example: 'MyPass123' (8 characters) or 'SecurePassword2024' (18 characters).",
                code='password_too_short'
            )

        # Cannot be entirely numeric
        if password.isdigit():
            raise ValidationError(
                "Password cannot be all numbers. Please add letters. For example, instead of '12345678', try 'Pass12345' or 'MyPass123'.",
                code='password_entirely_numeric'
            )

        # Must contain at least one letter
        if not any(c.isalpha() for c in password):
            raise ValidationError(
                "Password must include at least one letter (a-z or A-Z). For example: 'Pass123!@#' or 'MySecure2024'.",
                code='password_no_letter'
            )

        return password

    def clean(self):
        """
        Server-side validation: Cross-field validation.

        Raises:
            ValidationError: If passwords don't match
        """
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError({
                'password2': "Passwords do not match. Please make sure both password fields contain exactly the same text."
            })

        return cleaned_data


class NormalizedAuthenticationForm(AuthenticationForm):
    """
    Custom authentication form with input normalization.

    Normalization:
        - Username: Strip whitespace, convert to lowercase
        - Password: No normalization (case-sensitive)

    This ensures users can log in regardless of how they type their username
    (e.g., 'JohnDoe', 'johndoe', '  JOHNDOE  ' all work).

    Follows dual-layer-validation skill:
        - Server-side: Normalization in clean_username()
        - Client-side: JavaScript normalization on blur (in template)
    """

    def clean_username(self) -> str:
        """
        Normalize username before authentication.

        Returns:
            str: Normalized username (stripped and lowercased).
        """
        username = self.cleaned_data.get('username', '')
        # Strip whitespace and convert to lowercase
        return username.strip().lower()


class PatientProfileForm(forms.ModelForm):
    """
    Form for patient medical information with enhanced dual-layer validation.

    Server-side validation:
        - Date of birth must be in the past
        - Age must be between 0-120 years
        - Emergency contact must have valid format if provided

    Client-side validation (via widget attrs):
        - Required fields marked
        - Min/max constraints on numeric fields
        - Pattern validation on text fields
    """

    class Meta:
        model = Patient
        fields = [
            "age",
            "gender",
            "date_of_birth",
            "medical_history",
            "current_medications",
            "emergency_contact",
            "address",
        ]
        widgets = {
            "age": BootstrapNumberInput(attrs={
                "min": 0,
                "max": 120,
                "required": True,
                "aria-describedby": "age-help",
            }),
            "gender": BootstrapSelect(attrs={
                "required": True,
                "aria-describedby": "gender-help",
            }),
            "date_of_birth": BootstrapDateInput(attrs={
                "aria-describedby": "dob-help",
            }),
            "medical_history": BootstrapTextarea(attrs={
                "rows": 3,
                "placeholder": "Enter relevant medical history (allergies, chronic conditions, surgeries...)",
                "maxlength": 2000,
                "aria-describedby": "medical-history-help",
            }),
            "current_medications": BootstrapTextarea(attrs={
                "rows": 3,
                "placeholder": "List current medications and dosages...",
                "maxlength": 1000,
                "aria-describedby": "medications-help",
            }),
            "emergency_contact": BootstrapTextInput(attrs={
                "placeholder": "e.g., Ahmad Bin Ali - 012-345-6789",
                "minlength": 5,
                "maxlength": 100,
                "aria-describedby": "emergency-contact-help",
            }),
            "address": BootstrapTextarea(attrs={
                "rows": 2,
                "placeholder": "Full address including postcode and state",
                "maxlength": 500,
                "aria-describedby": "address-help",
            }),
        }

    def clean_date_of_birth(self) -> Optional[date]:
        """
        Validate date of birth is in the past and results in valid age.

        Returns:
            Optional[date]: The validated date of birth or None.

        Raises:
            ValidationError: If date is in future or age is out of range.
        """
        dob = self.cleaned_data.get("date_of_birth")
        if dob:
            today = date.today()
            if dob > today:
                raise ValidationError("Date of birth cannot be in the future.")

            # Calculate age
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 0 or age > 120:
                raise ValidationError("Age must be between 0 and 120 years.")

        return dob

    def clean_emergency_contact(self) -> str:
        """
        Validate emergency contact format if provided.

        Returns:
            str: The validated emergency contact string.

        Raises:
            ValidationError: If contact is too short when provided.
        """
        contact = self.cleaned_data.get("emergency_contact", "")
        if contact and len(contact.strip()) < 5:
            raise ValidationError(
                "Please provide a valid emergency contact with name and phone number "
                "(e.g., 'Ahmad Bin Ali - 012-345-6789')."
            )
        return contact

    def clean_age(self) -> int:
        """
        Validate age is within acceptable range.

        Returns:
            int: The validated age.

        Raises:
            ValidationError: If age is out of valid range.
        """
        age = self.cleaned_data.get("age")
        if age is not None:
            if age < 0:
                raise ValidationError("Age cannot be negative.")
            if age > 120:
                raise ValidationError("Age cannot exceed 120 years.")
        return age


class UserBasicInfoForm(forms.ModelForm):
    """
    Form for editing basic user information (all roles can use this).

    Includes User model fields (first_name, last_name, email) and UserProfile fields (phone).
    Implements dual-layer validation with both server-side and client-side validation.

    Server-side validation:
        - Email uniqueness check (excluding current user)
        - Malaysian phone number format validation

    Client-side validation (via widget attrs):
        - Required fields marked
        - Pattern validation on phone
        - Minlength/maxlength constraints
    """

    # Fields from User model
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=BootstrapTextInput(attrs={
            "placeholder": "e.g., John or Wei Ming",
            "required": True,
            "minlength": 2,
            "maxlength": 150,
            "aria-describedby": "first-name-help",
        }),
        help_text="Your legal first name (at least 2 characters)"
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=BootstrapTextInput(attrs={
            "placeholder": "e.g., Doe or Abdullah",
            "required": True,
            "minlength": 2,
            "maxlength": 150,
            "aria-describedby": "last-name-help",
        }),
        help_text="Your legal last name (at least 2 characters)"
    )
    email = forms.EmailField(
        required=True,
        widget=BootstrapEmailInput(attrs={
            "placeholder": "yourname@example.com",
            "required": True,
            "maxlength": 254,
            "aria-describedby": "email-help",
        }),
        help_text="Your primary email address (for login and notifications)"
    )

    # Field from UserProfile model
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=BootstrapTextInput(attrs={
            "placeholder": "012-3456-7890",
            "pattern": r"^(\+?6?01)[0-9]-?[0-9]{3,4}-?[0-9]{4}$",
            "title": "Malaysian phone number format: 012-3456-7890 or +6012-3456-7890",
            "aria-describedby": "phone-help",
        }),
        help_text="Malaysian phone number (e.g., 012-3456-7890)"
    )

    class Meta:
        model = UserProfile
        fields = ["phone"]

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize form with User model data.

        Args:
            user: Optional User instance to populate initial values.
        """
        self.user: Optional[User] = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Populate User fields if user provided
        if self.user:
            self.fields["first_name"].initial = self.user.first_name
            self.fields["last_name"].initial = self.user.last_name
            self.fields["email"].initial = self.user.email

    def clean_email(self) -> str:
        """
        Validate email format and uniqueness.

        Returns:
            str: The validated email address.

        Raises:
            ValidationError: If email is already registered to another user.
        """
        email = self.cleaned_data.get("email", "")

        # Check if email is already taken by another user
        if self.user:
            existing = User.objects.filter(email=email).exclude(id=self.user.id)
            if existing.exists():
                raise ValidationError(
                    "This email address is already registered. "
                    "Please use a different email or login to your existing account."
                )

        return email

    def clean_phone(self) -> str:
        """
        Validate phone number format (Malaysian).

        Returns:
            str: The validated phone number or empty string.

        Raises:
            ValidationError: If phone format is invalid.
        """
        from common.utils import validate_phone

        phone = self.cleaned_data.get("phone", "")
        if phone:
            try:
                validate_phone(phone)
            except ValidationError:
                raise ValidationError(
                    "Invalid phone number format. Please use Malaysian format "
                    "(e.g., 012-3456-7890 or +6012-3456-7890)"
                )
        return phone

    def clean_first_name(self) -> str:
        """
        Validate first name format.

        Returns:
            str: The validated first name.

        Raises:
            ValidationError: If first name is too short.
        """
        first_name = self.cleaned_data.get("first_name", "").strip()
        if len(first_name) < 2:
            raise ValidationError("First name must be at least 2 characters.")
        return first_name

    def clean_last_name(self) -> str:
        """
        Validate last name format.

        Returns:
            str: The validated last name.

        Raises:
            ValidationError: If last name is too short.
        """
        last_name = self.cleaned_data.get("last_name", "").strip()
        if len(last_name) < 2:
            raise ValidationError("Last name must be at least 2 characters.")
        return last_name

    def save(self, commit: bool = True) -> UserProfile:
        """
        Save both User and UserProfile data.

        Args:
            commit: Whether to save to database immediately.

        Returns:
            UserProfile: The saved profile instance.
        """
        # Save UserProfile data
        profile = super().save(commit=False)

        # Update User model fields
        if self.user:
            self.user.first_name = self.cleaned_data.get("first_name", "")
            self.user.last_name = self.cleaned_data.get("last_name", "")
            self.user.email = self.cleaned_data.get("email", "")
            if commit:
                self.user.save()

        if commit:
            profile.save()

        return profile


class ProfilePictureForm(forms.ModelForm):
    """
    Form for uploading profile pictures with dual-layer validation.

    Server-side validation:
        - File type validation (JPEG, PNG only)
        - File size validation (max 5MB)
        - Security checks via common.utils.validate_image_file

    Client-side validation (via widget attrs):
        - Accept attribute for file type filtering
        - JavaScript file size preview (in template)
    """

    profile_picture = forms.ImageField(
        required=False,
        widget=BootstrapFileInput(attrs={
            "accept": "image/jpeg,image/png,image/jpg",
            "aria-describedby": "profile-picture-help",
            "data-max-size": "5242880",  # 5MB in bytes for JS validation
        }),
        help_text="Upload a profile picture (max 5MB, JPEG/PNG format, square images work best)"
    )

    class Meta:
        model = UserProfile
        fields = ["profile_picture"]

    def clean_profile_picture(self) -> Optional[UploadedFile]:
        """
        Validate profile picture file.

        Performs server-side validation for:
            - File type (JPEG, PNG)
            - File size (max 5MB)

        Returns:
            Optional[UploadedFile]: The validated image file or None.

        Raises:
            ValidationError: If image validation fails.
        """
        from common.utils import validate_image_file

        image = self.cleaned_data.get("profile_picture")

        if image:
            # Validate using common utility (checks file type, size)
            try:
                validate_image_file(image, max_size_mb=5)
            except ValidationError as e:
                raise ValidationError(
                    f"Invalid image file: {str(e)}. "
                    "Please upload a JPEG or PNG image under 5MB."
                )

        return image


class DoctorNotesForm(forms.Form):
    """Form for doctors to add notes to predictions"""

    notes = forms.CharField(
        widget=BootstrapTextarea(attrs={
            "rows": 4,
            "placeholder": "Enter your clinical assessment and recommendations...",
        }),
        label="Doctor Notes",
        required=True,
    )
    is_validated = forms.BooleanField(
        required=False,
        label="Mark as validated",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
