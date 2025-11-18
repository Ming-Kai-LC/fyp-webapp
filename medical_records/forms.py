from django import forms
from .models import (
    MedicalCondition, Allergy, Medication, Vaccination,
    Surgery, FamilyHistory, MedicalDocument, LifestyleInformation
)


class MedicalConditionForm(forms.ModelForm):
    """Form for adding/editing medical conditions"""

    class Meta:
        model = MedicalCondition
        fields = [
            'condition_name', 'icd_code', 'severity', 'status',
            'diagnosed_date', 'resolved_date', 'description',
            'symptoms', 'treatment', 'increases_covid_risk', 'notes'
        ]
        widgets = {
            'diagnosed_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'resolved_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'condition_name': forms.TextInput(attrs={'class': 'form-control'}),
            'icd_code': forms.TextInput(attrs={'class': 'form-control'}),
            'severity': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'symptoms': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'treatment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'increases_covid_risk': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AllergyForm(forms.ModelForm):
    """Form for adding/editing allergies"""

    class Meta:
        model = Allergy
        fields = [
            'allergen', 'allergy_type', 'severity', 'reaction_description',
            'onset_date', 'is_active', 'verified_by_doctor'
        ]
        widgets = {
            'allergen': forms.TextInput(attrs={'class': 'form-control'}),
            'allergy_type': forms.Select(attrs={'class': 'form-control'}),
            'severity': forms.Select(attrs={'class': 'form-control'}),
            'reaction_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'onset_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'verified_by_doctor': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MedicationForm(forms.ModelForm):
    """Form for adding/editing medications"""

    class Meta:
        model = Medication
        fields = [
            'medication_name', 'dosage', 'frequency', 'route',
            'start_date', 'end_date', 'status', 'purpose',
            'prescribing_doctor', 'side_effects', 'notes'
        ]
        widgets = {
            'medication_name': forms.TextInput(attrs={'class': 'form-control'}),
            'dosage': forms.TextInput(attrs={'class': 'form-control'}),
            'frequency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Twice daily'}),
            'route': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., oral'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'purpose': forms.TextInput(attrs={'class': 'form-control'}),
            'prescribing_doctor': forms.TextInput(attrs={'class': 'form-control'}),
            'side_effects': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class VaccinationForm(forms.ModelForm):
    """Form for adding/editing vaccination records"""

    class Meta:
        model = Vaccination
        fields = [
            'vaccine_name', 'vaccine_brand', 'dose_number', 'lot_number',
            'administered_date', 'administered_by', 'location',
            'side_effects', 'adverse_reaction', 'verification_document', 'notes'
        ]
        widgets = {
            'vaccine_name': forms.Select(attrs={'class': 'form-control'}),
            'vaccine_brand': forms.TextInput(attrs={'class': 'form-control'}),
            'dose_number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'lot_number': forms.TextInput(attrs={'class': 'form-control'}),
            'administered_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'administered_by': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'side_effects': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'adverse_reaction': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'verification_document': forms.FileInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class SurgeryForm(forms.ModelForm):
    """Form for adding/editing surgical history"""

    class Meta:
        model = Surgery
        fields = [
            'surgery_name', 'procedure_code', 'surgery_date',
            'surgeon_name', 'hospital', 'reason', 'complications', 'outcome', 'notes'
        ]
        widgets = {
            'surgery_name': forms.TextInput(attrs={'class': 'form-control'}),
            'procedure_code': forms.TextInput(attrs={'class': 'form-control'}),
            'surgery_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'surgeon_name': forms.TextInput(attrs={'class': 'form-control'}),
            'hospital': forms.TextInput(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'complications': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'outcome': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class FamilyHistoryForm(forms.ModelForm):
    """Form for adding/editing family history"""

    class Meta:
        model = FamilyHistory
        fields = [
            'relationship', 'condition', 'age_at_diagnosis',
            'is_deceased', 'cause_of_death', 'notes'
        ]
        widgets = {
            'relationship': forms.Select(attrs={'class': 'form-control'}),
            'condition': forms.TextInput(attrs={'class': 'form-control'}),
            'age_at_diagnosis': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'is_deceased': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'cause_of_death': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class MedicalDocumentForm(forms.ModelForm):
    """Form for uploading medical documents"""

    class Meta:
        model = MedicalDocument
        fields = [
            'document_type', 'title', 'description', 'file',
            'document_date', 'is_sensitive'
        ]
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'document_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'is_sensitive': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class LifestyleInformationForm(forms.ModelForm):
    """Form for updating lifestyle information"""

    class Meta:
        model = LifestyleInformation
        fields = [
            'smoking_status', 'cigarettes_per_day', 'years_smoked', 'quit_date',
            'alcohol_use', 'drinks_per_week',
            'exercise_level', 'exercise_hours_per_week',
            'occupation', 'occupational_exposure_risk'
        ]
        widgets = {
            'smoking_status': forms.Select(attrs={'class': 'form-control'}),
            'cigarettes_per_day': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'years_smoked': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'quit_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'alcohol_use': forms.Select(attrs={'class': 'form-control'}),
            'drinks_per_week': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'exercise_level': forms.Select(attrs={'class': 'form-control'}),
            'exercise_hours_per_week': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.1'}),
            'occupation': forms.TextInput(attrs={'class': 'form-control'}),
            'occupational_exposure_risk': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
