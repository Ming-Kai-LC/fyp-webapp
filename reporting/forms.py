from django import forms
from .models import ReportTemplate, Report
from detection.models import Prediction


class ReportGenerationForm(forms.Form):
    """
    Form for configuring single report generation
    """
    template = forms.ModelChoiceField(
        queryset=ReportTemplate.objects.filter(is_active=True, template_type__in=['standard', 'detailed', 'summary']),
        required=True,
        label="Report Template",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    include_signature = forms.BooleanField(
        required=False,
        initial=True,
        label="Include Doctor Signature",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    include_hospital_logo = forms.BooleanField(
        required=False,
        initial=True,
        label="Include Hospital Logo",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    include_qr_code = forms.BooleanField(
        required=False,
        initial=True,
        label="Include QR Code for Verification",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    custom_notes = forms.CharField(
        required=False,
        label="Additional Notes",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Add any additional notes or recommendations for the report...'
        })
    )


class BatchReportForm(forms.Form):
    """
    Form for batch report generation
    """
    predictions = forms.ModelMultipleChoiceField(
        queryset=Prediction.objects.all(),
        required=True,
        label="Select Predictions",
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )

    template = forms.ModelChoiceField(
        queryset=ReportTemplate.objects.filter(is_active=True),
        required=True,
        label="Report Template",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show predictions that don't have reports yet (optional)
        # self.fields['predictions'].queryset = Prediction.objects.filter(reports__isnull=True)


class ReportTemplateForm(forms.ModelForm):
    """
    Form for creating/editing report templates
    """
    class Meta:
        model = ReportTemplate
        fields = ['name', 'template_type', 'description', 'html_template', 'css_styles', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'template_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'html_template': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'style': 'font-family: monospace;'}),
            'css_styles': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'style': 'font-family: monospace;'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
