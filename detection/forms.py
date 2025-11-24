# detection/forms.py
"""
Django Forms for COVID-19 Detection System
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import XRayImage, Patient, UserProfile


class XRayUploadForm(forms.ModelForm):
    """Form for uploading X-ray images"""

    class Meta:
        model = XRayImage
        fields = ["original_image", "notes"]
        widgets = {
            "original_image": forms.FileInput(
                attrs={"class": "form-control", "accept": "image/*", "required": True}
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Optional clinical notes or observations...",
                }
            ),
        }
        labels = {
            "original_image": "Chest X-ray Image",
            "notes": "Clinical Notes (Optional)",
        }


class UserRegistrationForm(UserCreationForm):
    """
    Patient registration form for public self-registration.

    Security Note: This form is for PUBLIC registration and only creates patient accounts.
    Staff users must be created by administrators through the admin panel.
    This enforces the user-role-permissions skill: "Public registration is patient-only"
    """

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "patient@example.com",
            "autocomplete": "email"
        }),
        help_text="We'll use this for important health notifications"
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "John",
            "autocomplete": "given-name"
        }),
        help_text="Your legal first name"
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Doe",
            "autocomplete": "family-name"
        }),
        help_text="Your legal last name"
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

        # Username field
        self.fields["username"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "username",
            "autocomplete": "username",
            "minlength": "3",
            "maxlength": "150"
        })
        self.fields["username"].help_text = "3-150 characters. Letters, digits and @/./+/-/_ only."

        # Password fields
        self.fields["password1"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Enter password",
            "autocomplete": "new-password"
        })
        self.fields["password1"].help_text = (
            "Your password must contain at least 8 characters and "
            "can't be entirely numeric."
        )

        self.fields["password2"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Confirm password",
            "autocomplete": "new-password"
        })
        self.fields["password2"].help_text = "Enter the same password for confirmation"

        # Add labels
        self.fields["username"].label = "Username"
        self.fields["first_name"].label = "First Name"
        self.fields["last_name"].label = "Last Name"
        self.fields["email"].label = "Email Address"
        self.fields["password1"].label = "Password"
        self.fields["password2"].label = "Confirm Password"

    def clean_email(self):
        """Validate email is unique"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "This email address is already registered. Please use a different email or login to your existing account."
            )
        return email

    def clean_username(self):
        """Validate username with better error messages"""
        username = self.cleaned_data.get('username')

        # Check length
        if len(username) < 3:
            raise forms.ValidationError("Username must be at least 3 characters long.")

        # Check if exists
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "This username is already taken. Please choose a different username."
            )

        return username

    def clean_password1(self):
        """Validate password strength"""
        password = self.cleaned_data.get('password1')

        # Check minimum length
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")

        # Check not entirely numeric
        if password.isdigit():
            raise forms.ValidationError("Password cannot be entirely numeric.")

        return password

    def clean(self):
        """Validate passwords match"""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError({
                'password2': "The two password fields didn't match."
            })

        return cleaned_data


class PatientProfileForm(forms.ModelForm):
    """Form for patient medical information"""

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
            "age": forms.NumberInput(
                attrs={"class": "form-control", "min": 0, "max": 120}
            ),
            "gender": forms.Select(attrs={"class": "form-control"}),
            "date_of_birth": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "medical_history": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "current_medications": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "emergency_contact": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }


class DoctorNotesForm(forms.Form):
    """Form for doctors to add notes to predictions"""

    notes = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Enter your clinical assessment and recommendations...",
            }
        ),
        label="Doctor Notes",
        required=True,
    )
    is_validated = forms.BooleanField(
        required=False,
        label="Mark as validated",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
