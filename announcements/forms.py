"""
Announcements Forms
Demonstrates usage of foundation components (Bootstrap Widgets)
"""

from django import forms
from .models import Announcement
from .constants import PRIORITY_CHOICES

# ✅ FOUNDATION: Import Bootstrap widgets instead of hardcoding attrs
from common.widgets import (
    BootstrapTextInput,
    BootstrapTextarea,
    BootstrapSelect,
    BootstrapDateTimeInput,
    BootstrapCheckboxInput
)


class AnnouncementForm(forms.ModelForm):
    """
    Form for creating/editing announcements.

    ✅ Uses Bootstrap widgets from common.widgets
    ✅ No hardcoded attrs={'class': 'form-control'}
    ✅ Consistent UI across all forms

    This eliminates 3-5 lines of boilerplate per field!
    """

    class Meta:
        model = Announcement
        fields = ['title', 'message', 'priority', 'is_active', 'expires_at']

        # ✅ FOUNDATION: Use Bootstrap widgets
        widgets = {
            'title': BootstrapTextInput(attrs={
                'placeholder': 'Enter announcement title',
                'maxlength': '200'
            }),
            'message': BootstrapTextarea(attrs={
                'placeholder': 'Enter announcement message',
                'rows': 5
            }),
            'priority': BootstrapSelect(choices=PRIORITY_CHOICES),
            'is_active': BootstrapCheckboxInput(),
            'expires_at': BootstrapDateTimeInput(attrs={
                'placeholder': 'Optional expiry date and time'
            }),
        }

        labels = {
            'title': 'Title',
            'message': 'Message',
            'priority': 'Priority Level',
            'is_active': 'Active',
            'expires_at': 'Expires At',
        }

        help_texts = {
            'title': 'Short, descriptive title for the announcement',
            'message': 'Full announcement message (supports plain text)',
            'priority': 'Select the importance level',
            'is_active': 'Uncheck to hide this announcement',
            'expires_at': 'Leave empty for no expiration',
        }

    def clean_expires_at(self):
        """Validate expiration date is in the future."""
        from django.utils import timezone

        expires_at = self.cleaned_data.get('expires_at')

        if expires_at and expires_at < timezone.now():
            raise forms.ValidationError(
                "Expiration date must be in the future."
            )

        return expires_at

    def clean(self):
        """Cross-field validation."""
        cleaned_data = super().clean()

        # Example: Urgent announcements should have expiry
        priority = cleaned_data.get('priority')
        expires_at = cleaned_data.get('expires_at')

        if priority == Announcement.PRIORITY_URGENT and not expires_at:
            self.add_error(
                'expires_at',
                "Urgent announcements should have an expiration date."
            )

        return cleaned_data


# ❌ OLD WAY (WITHOUT FOUNDATION) - DO NOT USE:
#
# class AnnouncementFormOld(forms.ModelForm):
#     class Meta:
#         model = Announcement
#         fields = ['title', 'message', 'priority', 'expires_at']
#         widgets = {
#             'title': forms.TextInput(attrs={
#                 'class': 'form-control',  # ❌ Hardcoded
#                 'placeholder': 'Enter announcement title',
#             }),
#             'message': forms.Textarea(attrs={
#                 'class': 'form-control',  # ❌ Hardcoded
#                 'rows': 5,
#             }),
#             'priority': forms.Select(attrs={
#                 'class': 'form-select',  # ❌ Hardcoded
#             }, choices=PRIORITY_CHOICES),
#             'expires_at': forms.DateTimeInput(attrs={
#                 'class': 'form-control',  # ❌ Hardcoded
#                 'type': 'datetime-local',  # ❌ Hardcoded
#             }),
#         }
#
# Result: 20+ lines of hardcoded Bootstrap classes!
# ✅ With foundation widgets: Only 7 lines, no hardcoding!
