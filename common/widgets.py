"""
Bootstrap 5 form widgets for consistent UI/UX across the application.

These widgets automatically apply Bootstrap 5 classes to form fields,
ensuring a consistent look and feel without repeating code.

Usage:
    from common.widgets import BootstrapTextInput, BootstrapSelect

    class MyForm(forms.ModelForm):
        class Meta:
            widgets = {
                'name': BootstrapTextInput(),
                'status': BootstrapSelect(),
            }
"""

from django import forms


class BootstrapTextInput(forms.TextInput):
    """
    Text input with Bootstrap 5 form-control class.

    Example:
        'first_name': BootstrapTextInput(attrs={'placeholder': 'Enter first name'})
    """
    def __init__(self, attrs=None, **kwargs):
        default_attrs = {'class': 'form-control'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, **kwargs)


class BootstrapEmailInput(forms.EmailInput):
    """
    Email input with Bootstrap 5 form-control class and email validation.

    Example:
        'email': BootstrapEmailInput(attrs={'placeholder': 'user@example.com'})
    """
    def __init__(self, attrs=None, **kwargs):
        default_attrs = {'class': 'form-control', 'type': 'email'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, **kwargs)


class BootstrapPasswordInput(forms.PasswordInput):
    """
    Password input with Bootstrap 5 form-control class.

    Example:
        'password': BootstrapPasswordInput()
    """
    def __init__(self, attrs=None, **kwargs):
        default_attrs = {'class': 'form-control'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, **kwargs)


class BootstrapNumberInput(forms.NumberInput):
    """
    Number input with Bootstrap 5 form-control class.

    Example:
        'age': BootstrapNumberInput(attrs={'min': 0, 'max': 120})
    """
    def __init__(self, attrs=None, **kwargs):
        default_attrs = {'class': 'form-control'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, **kwargs)


class BootstrapTextarea(forms.Textarea):
    """
    Textarea with Bootstrap 5 form-control class.

    Example:
        'notes': BootstrapTextarea(attrs={'rows': 5, 'placeholder': 'Enter notes'})
    """
    def __init__(self, attrs=None, **kwargs):
        default_attrs = {'class': 'form-control', 'rows': 3}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, **kwargs)


class BootstrapSelect(forms.Select):
    """
    Select dropdown with Bootstrap 5 form-select class.

    Example:
        'status': BootstrapSelect(choices=STATUS_CHOICES)
    """
    def __init__(self, attrs=None, choices=(), **kwargs):
        default_attrs = {'class': 'form-select'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, choices=choices, **kwargs)


class BootstrapSelectMultiple(forms.SelectMultiple):
    """
    Multiple select dropdown with Bootstrap 5 form-select class.

    Example:
        'tags': BootstrapSelectMultiple(choices=TAG_CHOICES)
    """
    def __init__(self, attrs=None, choices=(), **kwargs):
        default_attrs = {'class': 'form-select', 'multiple': True}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, choices=choices, **kwargs)


class BootstrapCheckboxInput(forms.CheckboxInput):
    """
    Checkbox with Bootstrap 5 form-check-input class.

    Example:
        'agree_terms': BootstrapCheckboxInput()
    """
    def __init__(self, attrs=None, **kwargs):
        default_attrs = {'class': 'form-check-input'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, **kwargs)


class BootstrapRadioSelect(forms.RadioSelect):
    """
    Radio buttons with Bootstrap 5 form-check-input class.

    Example:
        'gender': BootstrapRadioSelect(choices=GENDER_CHOICES)
    """
    def __init__(self, attrs=None, choices=(), **kwargs):
        default_attrs = {'class': 'form-check-input'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, choices=choices, **kwargs)


class BootstrapFileInput(forms.FileInput):
    """
    File input with Bootstrap 5 form-control class.

    Example:
        'profile_picture': BootstrapFileInput(attrs={'accept': 'image/*'})
        'xray_image': BootstrapFileInput(attrs={'accept': 'image/png,image/jpeg'})
    """
    def __init__(self, attrs=None, **kwargs):
        default_attrs = {'class': 'form-control'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, **kwargs)


class BootstrapDateInput(forms.DateInput):
    """
    Date input with Bootstrap 5 form-control class and HTML5 date picker.

    Example:
        'date_of_birth': BootstrapDateInput()
    """
    def __init__(self, attrs=None, **kwargs):
        default_attrs = {'class': 'form-control', 'type': 'date'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, **kwargs)


class BootstrapTimeInput(forms.TimeInput):
    """
    Time input with Bootstrap 5 form-control class and HTML5 time picker.

    Example:
        'appointment_time': BootstrapTimeInput()
    """
    def __init__(self, attrs=None, **kwargs):
        default_attrs = {'class': 'form-control', 'type': 'time'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, **kwargs)


class BootstrapDateTimeInput(forms.DateTimeInput):
    """
    DateTime input with Bootstrap 5 form-control class and HTML5 datetime-local picker.

    Example:
        'scheduled_date': BootstrapDateTimeInput()
    """
    def __init__(self, attrs=None, **kwargs):
        default_attrs = {'class': 'form-control', 'type': 'datetime-local'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, format='%Y-%m-%dT%H:%M', **kwargs)


class BootstrapURLInput(forms.URLInput):
    """
    URL input with Bootstrap 5 form-control class and URL validation.

    Example:
        'website': BootstrapURLInput(attrs={'placeholder': 'https://example.com'})
    """
    def __init__(self, attrs=None, **kwargs):
        default_attrs = {'class': 'form-control', 'type': 'url'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, **kwargs)


class BootstrapTelInput(forms.TextInput):
    """
    Telephone input with Bootstrap 5 form-control class.

    Example:
        'phone': BootstrapTelInput(attrs={'placeholder': '+60123456789'})
    """
    def __init__(self, attrs=None, **kwargs):
        default_attrs = {'class': 'form-control', 'type': 'tel'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, **kwargs)


class BootstrapSearchInput(forms.TextInput):
    """
    Search input with Bootstrap 5 form-control class.

    Example:
        'search': BootstrapSearchInput(attrs={'placeholder': 'Search patients...'})
    """
    def __init__(self, attrs=None, **kwargs):
        default_attrs = {'class': 'form-control', 'type': 'search'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, **kwargs)


class BootstrapColorInput(forms.TextInput):
    """
    Color picker input with Bootstrap 5 form-control class.

    Example:
        'theme_color': BootstrapColorInput()
    """
    def __init__(self, attrs=None, **kwargs):
        default_attrs = {'class': 'form-control form-control-color', 'type': 'color'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, **kwargs)


class BootstrapRangeInput(forms.NumberInput):
    """
    Range slider with Bootstrap 5 form-range class.

    Example:
        'severity': BootstrapRangeInput(attrs={'min': 0, 'max': 10, 'step': 1})
    """
    def __init__(self, attrs=None, **kwargs):
        default_attrs = {'class': 'form-range', 'type': 'range'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, **kwargs)


# Form field size variations
class BootstrapTextInputLarge(BootstrapTextInput):
    """Large text input (form-control-lg)."""
    def __init__(self, attrs=None, **kwargs):
        attrs = attrs or {}
        attrs['class'] = 'form-control form-control-lg'
        super().__init__(attrs=attrs, **kwargs)


class BootstrapTextInputSmall(BootstrapTextInput):
    """Small text input (form-control-sm)."""
    def __init__(self, attrs=None, **kwargs):
        attrs = attrs or {}
        attrs['class'] = 'form-control form-control-sm'
        super().__init__(attrs=attrs, **kwargs)


class BootstrapSelectLarge(BootstrapSelect):
    """Large select dropdown (form-select-lg)."""
    def __init__(self, attrs=None, choices=(), **kwargs):
        attrs = attrs or {}
        attrs['class'] = 'form-select form-select-lg'
        super().__init__(attrs=attrs, choices=choices, **kwargs)


class BootstrapSelectSmall(BootstrapSelect):
    """Small select dropdown (form-select-sm)."""
    def __init__(self, attrs=None, choices=(), **kwargs):
        attrs = attrs or {}
        attrs['class'] = 'form-select form-select-sm'
        super().__init__(attrs=attrs, choices=choices, **kwargs)


# Complete form example:
"""
from django import forms
from common.widgets import (
    BootstrapTextInput,
    BootstrapEmailInput,
    BootstrapDateInput,
    BootstrapSelect,
    BootstrapTextarea,
    BootstrapFileInput,
)
from .models import Patient
from .constants import GenderChoices

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'email', 'date_of_birth', 'gender', 'medical_history', 'profile_picture']
        widgets = {
            'first_name': BootstrapTextInput(attrs={'placeholder': 'First Name'}),
            'last_name': BootstrapTextInput(attrs={'placeholder': 'Last Name'}),
            'email': BootstrapEmailInput(attrs={'placeholder': 'email@example.com'}),
            'date_of_birth': BootstrapDateInput(),
            'gender': BootstrapSelect(choices=GenderChoices.CHOICES),
            'medical_history': BootstrapTextarea(attrs={'rows': 5, 'placeholder': 'Medical history...'}),
            'profile_picture': BootstrapFileInput(attrs={'accept': 'image/*'}),
        }
"""
