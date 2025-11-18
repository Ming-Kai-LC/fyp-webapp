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
        fields = ['original_image', 'notes']
        widgets = {
            'original_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'required': True
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional clinical notes or observations...'
            })
        }
        labels = {
            'original_image': 'Chest X-ray Image',
            'notes': 'Clinical Notes (Optional)'
        }


class UserRegistrationForm(UserCreationForm):
    """Extended user registration form with role selection"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    role = forms.ChoiceField(
        choices=[('patient', 'Patient'), ('doctor', 'Doctor/Staff')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 
                 'password1', 'password2', 'role']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})


class PatientProfileForm(forms.ModelForm):
    """Form for patient medical information"""
    
    class Meta:
        model = Patient
        fields = ['age', 'gender', 'date_of_birth', 'medical_history', 
                 'current_medications', 'emergency_contact', 'address']
        widgets = {
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 120}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'medical_history': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'current_medications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class DoctorNotesForm(forms.Form):
    """Form for doctors to add notes to predictions"""
    
    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Enter your clinical assessment and recommendations...'
        }),
        label='Doctor Notes',
        required=True
    )
    is_validated = forms.BooleanField(
        required=False,
        label='Mark as validated',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
