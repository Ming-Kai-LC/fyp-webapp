# Django Module Creation Best Practices

Ensures all Django components follow industry standards, are reusable, and maintainable using Object-Oriented principles.

## Core Principles

1. **DRY (Don't Repeat Yourself)**: Reuse code through inheritance and mixins
2. **Fat Models, Thin Views**: Business logic in models, not views
3. **Class-Based Views**: Use CBVs for reusability
4. **Mixins**: Create reusable functionality
5. **Type Hints**: Use Python type hints for clarity
6. **Documentation**: Docstrings for all classes and methods

## Django App Structure

```
app_name/
├── __init__.py
├── models.py              # Database models
├── views.py               # View logic (CBVs preferred)
├── forms.py               # Form definitions
├── admin.py               # Admin configuration
├── urls.py                # URL routing
├── mixins.py              # Reusable mixins
├── managers.py            # Custom model managers
├── services.py            # Business logic services
├── validators.py          # Custom validators
├── signals.py             # Django signals
├── templatetags/          # Custom template tags
│   └── app_tags.py
├── templates/app_name/    # App templates
├── static/app_name/       # App static files
└── tests/                 # Test suite
    ├── test_models.py
    ├── test_views.py
    └── test_forms.py
```

## Models (Fat Models Pattern)

### Model Best Practices

```python
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from typing import Optional

class BaseModel(models.Model):
    """
    Abstract base model with common fields and methods.
    All models should inherit from this.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def __str__(self) -> str:
        """Return string representation"""
        raise NotImplementedError("Subclasses must implement __str__")


class Prediction(BaseModel):
    """
    Stores AI model predictions for X-ray analysis.

    Attributes:
        xray: Foreign key to XRayImage
        final_diagnosis: Consensus diagnosis from all models
        consensus_confidence: Average confidence score
    """
    CLASS_CHOICES = [
        ('COVID', 'COVID-19'),
        ('Normal', 'Normal'),
        ('Viral Pneumonia', 'Viral Pneumonia'),
        ('Lung Opacity', 'Lung Opacity'),
    ]

    xray = models.ForeignKey(
        'XRayImage',
        on_delete=models.CASCADE,
        related_name='predictions',
        help_text="X-ray image being analyzed"
    )
    final_diagnosis = models.CharField(
        max_length=50,
        choices=CLASS_CHOICES,
        help_text="Final consensus diagnosis"
    )
    consensus_confidence = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Confidence of final diagnosis"
    )

    class Meta:
        verbose_name = "Prediction"
        verbose_name_plural = "Predictions"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['final_diagnosis']),
        ]

    def __str__(self) -> str:
        return f"{self.final_diagnosis} - {self.xray.patient.user.username}"

    def get_best_model(self) -> tuple[str, float]:
        """
        Return the model with highest confidence.

        Returns:
            tuple: (model_name, confidence)
        """
        models = [
            ('CrossViT', self.crossvit_confidence),
            ('ResNet-50', self.resnet50_confidence),
            # ... other models
        ]
        return max(models, key=lambda x: x[1])

    def is_high_confidence(self) -> bool:
        """Check if prediction has high confidence (>90%)"""
        return self.consensus_confidence > 90

    def requires_review(self) -> bool:
        """Check if prediction requires doctor review"""
        return not self.is_validated and self.final_diagnosis == 'COVID'
```

### Custom Model Managers

```python
# managers.py
from django.db import models
from django.db.models import Q, Count, Avg

class PredictionQuerySet(models.QuerySet):
    """Custom queryset for Prediction model"""

    def covid_positive(self):
        """Filter COVID positive predictions"""
        return self.filter(final_diagnosis='COVID')

    def pending_validation(self):
        """Filter predictions awaiting validation"""
        return self.filter(is_validated=False)

    def high_confidence(self):
        """Filter high confidence predictions"""
        return self.filter(consensus_confidence__gte=90)

    def with_patient_info(self):
        """Prefetch related patient information"""
        return self.select_related('xray__patient__user')


class PredictionManager(models.Manager):
    """Custom manager for Prediction model"""

    def get_queryset(self):
        return PredictionQuerySet(self.model, using=self._db)

    def covid_positive(self):
        return self.get_queryset().covid_positive()

    def pending_validation(self):
        return self.get_queryset().pending_validation()

    def get_statistics(self):
        """Get aggregated statistics"""
        return self.get_queryset().aggregate(
            total=Count('id'),
            covid_cases=Count('id', filter=Q(final_diagnosis='COVID')),
            normal_cases=Count('id', filter=Q(final_diagnosis='Normal')),
            avg_confidence=Avg('consensus_confidence')
        )


# In models.py
class Prediction(BaseModel):
    # ... fields ...

    objects = PredictionManager()  # Custom manager

    # ... methods ...
```

## Views (Class-Based Views with Mixins)

### Reusable Mixins

```python
# mixins.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from typing import Any

class RoleRequiredMixin(LoginRequiredMixin):
    """
    Mixin to restrict access based on user role.

    Attributes:
        required_role: str - Role required to access view
    """
    required_role: str = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not hasattr(request.user, 'profile'):
            messages.error(request, "User profile not found.")
            return redirect('home')

        if self.required_role and request.user.profile.role != self.required_role:
            messages.error(
                request,
                f"Access denied. This page is for {self.required_role}s only."
            )
            return redirect('home')

        return super().dispatch(request, *args, **kwargs)


class DoctorRequiredMixin(RoleRequiredMixin):
    """Restrict access to doctors only"""
    required_role = 'doctor'


class PatientRequiredMixin(RoleRequiredMixin):
    """Restrict access to patients only"""
    required_role = 'patient'


class SuccessMessageMixin:
    """
    Add success message after successful form submission.

    Attributes:
        success_message: str - Message to display
    """
    success_message: str = ""

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.success_message:
            messages.success(self.request, self.success_message)
        return response


class TitleMixin:
    """
    Add page title to context.

    Attributes:
        title: str - Page title
    """
    title: str = ""

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context
```

### Class-Based Views

```python
# views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from .mixins import DoctorRequiredMixin, SuccessMessageMixin, TitleMixin
from .models import Prediction
from .forms import XRayUploadForm

class PredictionListView(DoctorRequiredMixin, TitleMixin, ListView):
    """
    Display list of predictions for doctors.

    Features:
        - Pagination (25 per page)
        - Filtering by diagnosis
        - Prefetch related data for performance
    """
    model = Prediction
    template_name = 'detection/prediction_list.html'
    context_object_name = 'predictions'
    paginate_by = 25
    title = "Prediction History"

    def get_queryset(self):
        """Filter and optimize queryset"""
        qs = Prediction.objects.with_patient_info()

        # Filter by diagnosis if provided
        diagnosis = self.request.GET.get('diagnosis')
        if diagnosis:
            qs = qs.filter(final_diagnosis=diagnosis)

        return qs

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['total_predictions'] = Prediction.objects.count()
        context['covid_cases'] = Prediction.objects.covid_positive().count()
        return context


class PredictionDetailView(DoctorRequiredMixin, TitleMixin, DetailView):
    """
    Display detailed prediction results.

    Features:
        - Multi-model comparison
        - Explainability visualization
        - Doctor notes
    """
    model = Prediction
    template_name = 'detection/prediction_detail.html'
    context_object_name = 'prediction'
    title = "Prediction Details"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['all_predictions'] = self.object.get_all_predictions()
        context['best_model'] = self.object.get_best_model()
        return context


class XRayUploadView(DoctorRequiredMixin, SuccessMessageMixin, TitleMixin, CreateView):
    """
    Handle X-ray upload and prediction.

    Features:
        - File validation
        - CLAHE preprocessing
        - Multi-model prediction
        - Redirect to results
    """
    form_class = XRayUploadForm
    template_name = 'detection/upload.html'
    success_message = "X-ray uploaded and analyzed successfully!"
    title = "Upload X-Ray"

    def get_success_url(self):
        return reverse_lazy('detection:view_results', kwargs={'pk': self.object.prediction.id})

    def form_valid(self, form):
        """Process upload and run predictions"""
        # Set uploader
        form.instance.uploaded_by = self.request.user

        # Save X-ray
        response = super().form_valid(form)

        # Run ML predictions (in service layer)
        from .services import PredictionService
        prediction = PredictionService.create_prediction(self.object)

        # Store prediction for success_url
        self.object.prediction = prediction

        return response
```

## Services (Business Logic Layer)

```python
# services.py
from typing import Dict, Any
from .models import XRayImage, Prediction
from .ml_engine import model_ensemble
from .preprocessing import apply_clahe
import logging

logger = logging.getLogger(__name__)


class PredictionService:
    """
    Service layer for prediction-related business logic.
    Separates business logic from views.
    """

    @staticmethod
    def create_prediction(xray: XRayImage) -> Prediction:
        """
        Create prediction from X-ray image.

        Args:
            xray: XRayImage instance

        Returns:
            Prediction instance

        Raises:
            ValueError: If prediction fails
        """
        try:
            # Preprocess image
            processed_path = apply_clahe(xray.original_image.path)

            # Run all models
            results = model_ensemble.predict_all_models(processed_path)

            # Create prediction
            prediction = Prediction.objects.create(
                xray=xray,
                crossvit_prediction=results['crossvit']['class'],
                crossvit_confidence=results['crossvit']['confidence'],
                # ... other models ...
                final_diagnosis=results['consensus']['class'],
                consensus_confidence=results['consensus']['confidence'],
                inference_time=results['inference_time']
            )

            logger.info(f"Created prediction {prediction.id} for X-ray {xray.id}")
            return prediction

        except Exception as e:
            logger.error(f"Prediction failed for X-ray {xray.id}: {str(e)}")
            raise ValueError(f"Prediction failed: {str(e)}")

    @staticmethod
    def validate_prediction(prediction: Prediction, doctor_user, notes: str = "") -> None:
        """
        Validate prediction by doctor.

        Args:
            prediction: Prediction instance
            doctor_user: Doctor User instance
            notes: Optional doctor notes
        """
        prediction.mark_as_validated(doctor_user)
        if notes:
            prediction.doctor_notes = notes
            prediction.save()

        logger.info(f"Prediction {prediction.id} validated by {doctor_user.username}")
```

## Forms (Validation and Cleaning)

```python
# forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import XRayImage, Patient
from typing import Any

class XRayUploadForm(forms.ModelForm):
    """
    Form for uploading X-ray images.

    Features:
        - File type validation
        - File size validation
        - Patient selection
        - Optional notes
    """
    patient = forms.ModelChoiceField(
        queryset=Patient.objects.select_related('user'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Select the patient for this X-ray"
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Add any clinical observations...'
        }),
        required=False
    )

    class Meta:
        model = XRayImage
        fields = ['patient', 'original_image', 'notes']
        widgets = {
            'original_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/png'
            })
        }

    def clean_original_image(self) -> Any:
        """Validate uploaded image"""
        image = self.cleaned_data.get('original_image')

        if not image:
            raise ValidationError("Please select an image file.")

        # Check file size (10MB max)
        if image.size > 10 * 1024 * 1024:
            raise ValidationError("File size must be under 10MB.")

        # Check file extension
        allowed_extensions = ['.jpg', '.jpeg', '.png']
        if not any(image.name.lower().endswith(ext) for ext in allowed_extensions):
            raise ValidationError("Only JPG and PNG files are allowed.")

        return image

    def save(self, commit: bool = True) -> XRayImage:
        """Save with additional processing"""
        xray = super().save(commit=False)
        # Additional processing here
        if commit:
            xray.save()
        return xray
```

## Template Tags (Reusable Template Logic)

```python
# templatetags/detection_tags.py
from django import template
from typing import Any

register = template.Library()


@register.filter
def diagnosis_badge_class(diagnosis: str) -> str:
    """
    Return Bootstrap badge class for diagnosis.

    Args:
        diagnosis: Diagnosis string

    Returns:
        Bootstrap class string
    """
    mapping = {
        'COVID': 'bg-danger',
        'Normal': 'bg-success',
        'Viral Pneumonia': 'bg-warning',
        'Lung Opacity': 'bg-info',
    }
    return mapping.get(diagnosis, 'bg-secondary')


@register.inclusion_tag('detection/components/model_comparison_table.html')
def model_comparison_table(prediction: Any):
    """
    Render model comparison table component.

    Args:
        prediction: Prediction instance

    Returns:
        Context dict for template
    """
    return {
        'prediction': prediction,
        'all_predictions': prediction.get_all_predictions(),
        'best_model': prediction.get_best_model(),
    }


@register.simple_tag
def confidence_badge(confidence: float) -> str:
    """
    Return colored confidence badge.

    Args:
        confidence: Confidence percentage

    Returns:
        HTML badge string
    """
    if confidence >= 90:
        color = 'success'
    elif confidence >= 75:
        color = 'warning'
    else:
        color = 'danger'

    return f'<span class="badge bg-{color}">{confidence:.1f}%</span>'
```

## Checklist for New Module Creation

When creating a new Django app/module:

- ✅ Create proper directory structure
- ✅ Use abstract base models for common fields
- ✅ Implement custom managers/querysets for complex queries
- ✅ Use class-based views with mixins
- ✅ Separate business logic into services
- ✅ Add type hints to all functions
- ✅ Write comprehensive docstrings
- ✅ Validate all user input in forms
- ✅ Create reusable template tags for common patterns
- ✅ Add proper indexes to models
- ✅ Use `select_related`/`prefetch_related` for optimization
- ✅ Log important operations
- ✅ Handle exceptions properly
- ✅ Write unit tests

## Auto-Apply This Skill When:
- Creating new Django apps
- Adding new models
- Creating new views
- Implementing new features
- Refactoring existing code
- Adding business logic
