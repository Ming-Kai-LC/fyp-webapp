from django import forms
from django.contrib.auth.models import User
from .models import ComplianceReport, AuditLog
from datetime import datetime, timedelta
from django.utils import timezone


class AuditLogFilterForm(forms.Form):
    """
    Filter form for audit log list
    """
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        label="User",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    action_type = forms.ChoiceField(
        choices=[('', 'All Actions')] + list(AuditLog.ACTION_TYPES),
        required=False,
        label="Action Type",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    severity = forms.ChoiceField(
        choices=[('', 'All Severities')] + list(AuditLog.SEVERITY_LEVELS),
        required=False,
        label="Severity",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    date_from = forms.DateTimeField(
        required=False,
        label="From Date",
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )

    date_to = forms.DateTimeField(
        required=False,
        label="To Date",
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )

    search = forms.CharField(
        required=False,
        label="Search",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search in description or username...'
        })
    )


class ComplianceReportForm(forms.Form):
    """
    Form for generating compliance reports
    """
    report_type = forms.ChoiceField(
        choices=ComplianceReport.REPORT_TYPES,
        required=True,
        label="Report Type",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    start_date = forms.DateTimeField(
        required=True,
        label="Start Date",
        initial=lambda: timezone.now() - timedelta(days=30),
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )

    end_date = forms.DateTimeField(
        required=True,
        label="End Date",
        initial=timezone.now,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date >= end_date:
                raise forms.ValidationError("End date must be after start date.")

        return cleaned_data
