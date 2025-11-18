---
name: Code Quality Standards
description: Maintains PEP 8 compliance, type hints, docstrings, and 80%+ test coverage. Auto-applies code quality standards, testing patterns, and documentation requirements.
---

Maintains high code quality, readability, and test coverage throughout the project.

## Core Principles

1. **Clean Code**: Self-documenting, readable code
2. **Test Coverage**: Minimum 80% coverage for critical paths
3. **Type Hints**: Use for all public functions
4. **Documentation**: Docstrings for all public APIs
5. **Linting**: Follow PEP 8 and Django best practices
6. **DRY**: Don't repeat yourself

## Code Style (PEP 8 + Django)

### Naming Conventions

```python
# Classes: PascalCase
class PredictionService:
    pass

# Functions/Methods: snake_case
def create_prediction(xray: XRayImage) -> Prediction:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_FILE_SIZE = 10 * 1024 * 1024
COVID_CLASSES = ['COVID', 'Normal', 'Viral Pneumonia']

# Private methods: _leading_underscore
def _internal_helper(self):
    pass

# Variables: snake_case
prediction_count = 0
is_validated = True
```

### Import Organization

```python
# Standard library imports
import os
import sys
from typing import Optional, List, Dict, Any

# Django imports
from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

# Third-party imports
import torch
import numpy as np
from PIL import Image

# Local app imports
from .models import Prediction, XRayImage
from .forms import XRayUploadForm
from .services import PredictionService
```

### Type Hints

```python
from typing import Optional, List, Dict, Any, Tuple
from django.http import HttpRequest, HttpResponse

def create_prediction(
    xray: XRayImage,
    model_name: str = 'crossvit'
) -> Prediction:
    """
    Create prediction for X-ray image.

    Args:
        xray: XRayImage instance
        model_name: Name of model to use

    Returns:
        Prediction instance

    Raises:
        ValueError: If model_name is invalid
    """
    if model_name not in VALID_MODELS:
        raise ValueError(f"Invalid model: {model_name}")

    # Implementation
    return prediction

def get_statistics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """Get prediction statistics"""
    return {
        'total': 100,
        'covid_cases': 25,
        'average_confidence': 92.5
    }

# Type hints for class attributes
class PredictionService:
    cache_timeout: int = 300
    model_names: List[str] = ['crossvit', 'resnet50']

    def process_batch(
        self,
        xray_ids: List[int]
    ) -> List[Prediction]:
        """Process multiple X-rays"""
        return []
```

## Documentation Standards

### Module Docstrings

```python
"""
COVID-19 Detection - Prediction Services

This module handles all prediction-related business logic including:
- Creating predictions from X-ray images
- Running multi-model inference
- Managing prediction validation workflow

Example:
    service = PredictionService()
    prediction = service.create_prediction(xray)
"""
```

### Class Docstrings

```python
class PredictionService:
    """
    Service layer for prediction operations.

    This class encapsulates all business logic related to creating,
    validating, and managing COVID-19 predictions from X-ray images.

    Attributes:
        cache_timeout (int): Cache timeout in seconds
        model_names (List[str]): List of available model names

    Example:
        service = PredictionService()
        prediction = service.create_prediction(xray_image)
        service.validate_prediction(prediction, doctor_user)
    """
```

### Function Docstrings (Google Style)

```python
def create_prediction(xray: XRayImage, use_cache: bool = True) -> Prediction:
    """
    Create AI prediction for X-ray image.

    Runs all 6 AI models sequentially and creates a consensus prediction.
    Results are cached for 5 minutes if use_cache is True.

    Args:
        xray: XRayImage instance to analyze
        use_cache: Whether to use cached results if available

    Returns:
        Prediction instance with consensus diagnosis

    Raises:
        ValueError: If X-ray image is invalid or corrupted
        RuntimeError: If ML engine initialization fails

    Example:
        xray = XRayImage.objects.get(id=1)
        prediction = create_prediction(xray)
        print(f"Diagnosis: {prediction.final_diagnosis}")
    """
    pass
```

## Testing Standards

### Test Structure

```
tests/
├── __init__.py
├── test_models.py          # Model tests
├── test_views.py           # View tests
├── test_forms.py           # Form tests
├── test_services.py        # Service layer tests
├── test_ml_engine.py       # ML tests
├── fixtures/               # Test data
│   ├── sample_xray.jpg
│   └── test_data.json
└── factories.py            # Test factories
```

### Test Naming Convention

```python
# Format: test_<what>_<condition>_<expected_result>

def test_create_prediction_with_valid_xray_returns_prediction():
    pass

def test_upload_xray_without_authentication_redirects_to_login():
    pass

def test_validate_prediction_with_doctor_role_marks_as_validated():
    pass
```

### Model Tests

```python
# tests/test_models.py
from django.test import TestCase
from django.contrib.auth.models import User
from detection.models import Prediction, XRayImage, Patient

class PredictionModelTest(TestCase):
    """Test Prediction model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.patient = Patient.objects.create(
            user=self.user,
            age=35,
            gender='M'
        )
        self.xray = XRayImage.objects.create(
            patient=self.patient,
            original_image='path/to/test.jpg'
        )

    def test_str_representation_returns_diagnosis_and_patient(self):
        """Test __str__ method"""
        prediction = Prediction.objects.create(
            xray=self.xray,
            final_diagnosis='COVID',
            consensus_confidence=95.5
        )
        expected = f"COVID - {self.user.username}"
        self.assertEqual(str(prediction), expected)

    def test_is_high_confidence_returns_true_for_90_plus(self):
        """Test high confidence detection"""
        prediction = Prediction.objects.create(
            xray=self.xray,
            final_diagnosis='COVID',
            consensus_confidence=92.0
        )
        self.assertTrue(prediction.is_high_confidence())

    def test_is_high_confidence_returns_false_for_below_90(self):
        """Test low confidence detection"""
        prediction = Prediction.objects.create(
            xray=self.xray,
            final_diagnosis='COVID',
            consensus_confidence=85.0
        )
        self.assertFalse(prediction.is_high_confidence())

    def test_get_best_model_returns_model_with_highest_confidence(self):
        """Test best model selection"""
        prediction = Prediction.objects.create(
            xray=self.xray,
            crossvit_confidence=95.0,
            resnet50_confidence=88.0,
            densenet121_confidence=90.0
        )
        model_name, confidence = prediction.get_best_model()
        self.assertEqual(model_name, 'CrossViT')
        self.assertEqual(confidence, 95.0)
```

### View Tests

```python
# tests/test_views.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from detection.models import UserProfile

class DoctorDashboardViewTest(TestCase):
    """Test doctor dashboard view"""

    def setUp(self):
        """Set up test client and users"""
        self.client = Client()

        # Create doctor user
        self.doctor = User.objects.create_user(
            username='doctor',
            password='testpass123'
        )
        self.doctor.profile.role = 'doctor'
        self.doctor.profile.save()

        # Create patient user
        self.patient = User.objects.create_user(
            username='patient',
            password='testpass123'
        )
        self.patient.profile.role = 'patient'
        self.patient.profile.save()

    def test_doctor_can_access_dashboard(self):
        """Test doctor access to dashboard"""
        self.client.login(username='doctor', password='testpass123')
        response = self.client.get(reverse('detection:doctor_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'detection/doctor_dashboard.html')

    def test_patient_cannot_access_doctor_dashboard(self):
        """Test patient is denied access"""
        self.client.login(username='patient', password='testpass123')
        response = self.client.get(reverse('detection:doctor_dashboard'))

        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertRedirects(response, reverse('home'))

    def test_unauthenticated_user_redirected_to_login(self):
        """Test authentication requirement"""
        response = self.client.get(reverse('detection:doctor_dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_dashboard_shows_recent_predictions(self):
        """Test dashboard displays recent predictions"""
        self.client.login(username='doctor', password='testpass123')
        # Create test predictions...
        response = self.client.get(reverse('detection:doctor_dashboard'))

        self.assertIn('recent_predictions', response.context)
        self.assertIn('stats', response.context)
```

### Form Tests

```python
# tests/test_forms.py
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from detection.forms import XRayUploadForm
from detection.models import Patient

class XRayUploadFormTest(TestCase):
    """Test X-ray upload form"""

    def setUp(self):
        """Create test patient"""
        self.patient = Patient.objects.create(age=35, gender='M')

    def test_form_with_valid_data_is_valid(self):
        """Test form validation with valid data"""
        # Create mock image file
        image = SimpleUploadedFile(
            "test.jpg",
            b"fake image content",
            content_type="image/jpeg"
        )

        form_data = {'patient': self.patient.id}
        form_files = {'original_image': image}

        form = XRayUploadForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())

    def test_form_with_large_file_is_invalid(self):
        """Test file size validation"""
        # Create 11MB file (exceeds 10MB limit)
        large_content = b"x" * (11 * 1024 * 1024)
        large_image = SimpleUploadedFile(
            "large.jpg",
            large_content,
            content_type="image/jpeg"
        )

        form_data = {'patient': self.patient.id}
        form_files = {'original_image': large_image}

        form = XRayUploadForm(data=form_data, files=form_files)
        self.assertFalse(form.is_valid())
        self.assertIn('original_image', form.errors)

    def test_form_with_invalid_extension_is_invalid(self):
        """Test file extension validation"""
        txt_file = SimpleUploadedFile(
            "test.txt",
            b"not an image",
            content_type="text/plain"
        )

        form_data = {'patient': self.patient.id}
        form_files = {'original_image': txt_file}

        form = XRayUploadForm(data=form_data, files=form_files)
        self.assertFalse(form.is_valid())
```

### Service Layer Tests

```python
# tests/test_services.py
from django.test import TestCase
from unittest.mock import Mock, patch
from detection.services import PredictionService
from detection.models import XRayImage

class PredictionServiceTest(TestCase):
    """Test prediction service"""

    @patch('detection.services.model_ensemble')
    def test_create_prediction_with_valid_xray_returns_prediction(self, mock_ensemble):
        """Test prediction creation"""
        # Mock ML engine response
        mock_ensemble.predict_all_models.return_value = {
            'crossvit': {'class': 'COVID', 'confidence': 95.0},
            'resnet50': {'class': 'COVID', 'confidence': 88.0},
            'consensus': {'class': 'COVID', 'confidence': 92.0},
            'inference_time': 5.2
        }

        xray = XRayImage.objects.create(...)
        prediction = PredictionService.create_prediction(xray)

        self.assertIsNotNone(prediction)
        self.assertEqual(prediction.final_diagnosis, 'COVID')
        self.assertEqual(prediction.consensus_confidence, 92.0)
        mock_ensemble.predict_all_models.assert_called_once()

    def test_validate_prediction_marks_as_validated(self):
        """Test prediction validation"""
        prediction = Prediction.objects.create(...)
        doctor = User.objects.create_user('doctor', 'pass')

        PredictionService.validate_prediction(prediction, doctor, "Looks correct")

        prediction.refresh_from_db()
        self.assertTrue(prediction.is_validated)
        self.assertEqual(prediction.reviewed_by, doctor)
        self.assertEqual(prediction.doctor_notes, "Looks correct")
```

### Test Factories (Using Factory Boy)

```python
# tests/factories.py
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth.models import User
from detection.models import Patient, XRayImage, Prediction

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

class PatientFactory(DjangoModelFactory):
    class Meta:
        model = Patient

    user = factory.SubFactory(UserFactory)
    age = factory.Faker('random_int', min=18, max=90)
    gender = factory.Faker('random_element', elements=['M', 'F'])

class XRayImageFactory(DjangoModelFactory):
    class Meta:
        model = XRayImage

    patient = factory.SubFactory(PatientFactory)
    original_image = factory.django.ImageField()

# Usage in tests
def test_something(self):
    patient = PatientFactory()
    xray = XRayImageFactory(patient=patient)
```

## Code Quality Tools

### Configuration Files

**.flake8**
```ini
[flake8]
max-line-length = 100
exclude = migrations,__pycache__,venv
ignore = E203,W503
```

**pyproject.toml (for Black)**
```toml
[tool.black]
line-length = 100
target-version = ['py38', 'py39', 'py310', 'py311']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.venv
  | migrations
)/
'''
```

**pytest.ini**
```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = test_*.py
python_classes = *Test
python_functions = test_*
addopts = --cov=detection --cov-report=html --cov-report=term
```

### Pre-commit Hooks

**.pre-commit-config.yaml**
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8

  - repo: https://github.com/pycqa/isort
    rev: 5.13.0
    hooks:
      - id: isort
```

## Code Review Checklist

Before committing:

- ✅ All tests pass (`pytest`)
- ✅ Code coverage ≥ 80% for new code
- ✅ No linting errors (`flake8`)
- ✅ Code formatted (`black`)
- ✅ Type hints added for public functions
- ✅ Docstrings for all classes/functions
- ✅ No commented-out code
- ✅ No print statements (use logging)
- ✅ No hardcoded values (use settings)
- ✅ Error handling implemented
- ✅ Security vulnerabilities addressed
- ✅ Performance considerations reviewed

## Auto-Apply This Skill When:
- Writing any new code
- Refactoring existing code
- Creating new modules/features
- Reviewing pull requests
- Preparing for production
