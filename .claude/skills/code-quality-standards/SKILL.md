---
name: Code Quality Standards & Environment Management
description: Maintains PEP 8 compliance, type hints, docstrings, 80%+ test coverage, and enforces virtual environment usage. Auto-applies to all Python code execution, package installations, and development workflows.
---

# Code Quality Standards & Environment Management

Maintains high code quality, readability, test coverage, and proper Python environment isolation throughout the project.

## Core Principles

1. **Clean Code**: Self-documenting, readable code
2. **Test Coverage**: Minimum 80% coverage for critical paths
3. **Type Hints**: Use for all public functions
4. **Documentation**: Docstrings for all public APIs
5. **Linting**: Follow PEP 8 and Django best practices
6. **DRY**: Don't repeat yourself
7. **Isolation**: All Python operations in virtual environment
8. **Reproducibility**: Dependencies tracked in requirements.txt

---

## Part 1: Virtual Environment Management

### Virtual Environment Rules

**CRITICAL: ALWAYS use virtual environment for ALL Python operations**

### Location
```
fyp-webapp/
├── venv/                    # Virtual environment directory
│   ├── Scripts/            # (Windows) Executables and activation scripts
│   ├── Lib/                # Python packages
│   └── ...
├── requirements.txt        # Package dependencies
└── ...
```

### ✅ ALWAYS Use Virtual Environment Python

**Windows:**
```bash
# Python commands
venv/Scripts/python.exe script.py
venv/Scripts/python.exe manage.py runserver
venv/Scripts/python.exe manage.py migrate

# Pip commands
venv/Scripts/python.exe -m pip install package_name
venv/Scripts/python.exe -m pip install -r requirements.txt
venv/Scripts/python.exe -m pip freeze > requirements.txt
```

**Linux/Mac:**
```bash
# Python commands
venv/bin/python script.py
venv/bin/python manage.py runserver
venv/bin/python manage.py migrate

# Pip commands
venv/bin/python -m pip install package_name
venv/bin/python -m pip install -r requirements.txt
venv/bin/python -m pip freeze > requirements.txt
```

### ❌ NEVER Use Global Python

```bash
# DON'T do this:
python manage.py runserver        # Uses system Python
pip install django                 # Installs globally

# ALWAYS do this instead:
venv/Scripts/python.exe manage.py runserver    # Windows
venv/bin/python manage.py runserver            # Linux/Mac
```

### Common Django Commands with venv

```bash
# Windows
venv/Scripts/python.exe manage.py runserver
venv/Scripts/python.exe manage.py makemigrations
venv/Scripts/python.exe manage.py migrate
venv/Scripts/python.exe manage.py test
venv/Scripts/python.exe -m pytest
venv/Scripts/python.exe manage.py createsuperuser

# Linux/Mac
venv/bin/python manage.py runserver
venv/bin/python manage.py makemigrations
venv/bin/python manage.py migrate
venv/bin/python manage.py test
venv/bin/python -m pytest
venv/bin/python manage.py createsuperuser
```

### Package Management

**Installing new packages:**
```bash
# Windows
venv/Scripts/python.exe -m pip install package_name
venv/Scripts/python.exe -m pip freeze > requirements.txt

# Linux/Mac
venv/bin/python -m pip install package_name
venv/bin/python -m pip freeze > requirements.txt
```

**Installing from requirements.txt:**
```bash
# Windows
venv/Scripts/python.exe -m pip install -r requirements.txt

# Linux/Mac
venv/bin/python -m pip install -r requirements.txt
```

### Verifying Virtual Environment

```bash
# Windows - Check Python location
venv/Scripts/python.exe -c "import sys; print(sys.executable)"
# Should output: D:\Users\USER\Documents\GitHub\fyp-webapp\venv\Scripts\python.exe

# Linux/Mac - Check Python location
venv/bin/python -c "import sys; print(sys.executable)"
# Should output: /path/to/fyp-webapp/venv/bin/python
```

---

## Part 2: Code Style (PEP 8 + Django)

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

---

## Part 3: Documentation Standards

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

---

## Part 4: Testing Standards

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
```

### View Tests

```python
# tests/test_views.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

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

    def test_doctor_can_access_dashboard(self):
        """Test doctor access to dashboard"""
        self.client.login(username='doctor', password='testpass123')
        response = self.client.get(reverse('detection:doctor_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'detection/doctor_dashboard.html')

    def test_unauthenticated_user_redirected_to_login(self):
        """Test authentication requirement"""
        response = self.client.get(reverse('detection:doctor_dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
```

### Form Tests

```python
# tests/test_forms.py
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from detection.forms import XRayUploadForm

class XRayUploadFormTest(TestCase):
    """Test X-ray upload form"""

    def test_form_with_valid_data_is_valid(self):
        """Test form validation with valid data"""
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
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        large_image = SimpleUploadedFile(
            "large.jpg",
            large_content,
            content_type="image/jpeg"
        )

        form = XRayUploadForm(data=form_data, files={'original_image': large_image})
        self.assertFalse(form.is_valid())
        self.assertIn('original_image', form.errors)
```

### Service Layer Tests

```python
# tests/test_services.py
from django.test import TestCase
from unittest.mock import Mock, patch
from detection.services import PredictionService

class PredictionServiceTest(TestCase):
    """Test prediction service"""

    @patch('detection.services.model_ensemble')
    def test_create_prediction_with_valid_xray_returns_prediction(self, mock_ensemble):
        """Test prediction creation"""
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
        mock_ensemble.predict_all_models.assert_called_once()
```

### Test Factories (Using Factory Boy)

```python
# tests/factories.py
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth.models import User
from detection.models import Patient, XRayImage

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

# Usage in tests
def test_something(self):
    patient = PatientFactory()
    xray = XRayImageFactory(patient=patient)
```

---

## Part 5: Code Quality Tools

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

---

## Part 6: Code Review Checklist

### Before Committing:

**Code Quality:**
- ✅ All tests pass (`venv/Scripts/python.exe -m pytest`)
- ✅ Code coverage ≥ 80% for new code
- ✅ No linting errors (`flake8`)
- ✅ Code formatted (`black`)
- ✅ Type hints added for public functions
- ✅ Docstrings for all classes/functions
- ✅ No commented-out code
- ✅ No print statements (use logging)
- ✅ No hardcoded values (use settings)
- ✅ Error handling implemented

**Virtual Environment:**
- ✅ Virtual environment exists at `venv/`
- ✅ All commands use `venv/Scripts/python.exe` (Windows) or `venv/bin/python` (Linux/Mac)
- ✅ requirements.txt is up to date
- ✅ venv is in .gitignore
- ✅ Not using global `python` or `pip`

**Security & Performance:**
- ✅ Security vulnerabilities addressed
- ✅ Performance considerations reviewed

---

## Part 7: Project Dependencies

### Current Dependencies

**Core Django:**
- Django==4.2.7
- django-crispy-forms
- crispy-bootstrap5

**ML/AI:**
- torch
- torchvision
- timm
- opencv-python
- scikit-learn
- numpy
- pandas

**REST API:**
- djangorestframework
- djangorestframework-simplejwt
- drf-yasg
- django-cors-headers
- django-filter

**Reporting:**
- weasyprint
- xhtml2pdf
- openpyxl
- qrcode

**Utilities:**
- Pillow
- plotly
- python-dateutil
- pytz

### Updating requirements.txt

**After installing new packages:**
```bash
# Windows
venv/Scripts/python.exe -m pip freeze > requirements.txt

# Linux/Mac
venv/bin/python -m pip freeze > requirements.txt
```

**Best practice:** Commit requirements.txt with every package change

---

## Auto-Apply This Skill When:

**Virtual Environment Enforcement:**
- Running `python` commands
- Running `pip` commands
- Running Django `manage.py` commands
- Installing or upgrading packages
- Running tests
- Starting development server
- Performing database migrations
- Creating new Django apps
- Executing Python scripts

**Code Quality Standards:**
- Writing any new code
- Refactoring existing code
- Creating new modules/features
- Reviewing pull requests
- Preparing for production

---

## Critical Reminders

**Virtual Environment:**
1. **NEVER** use bare `python` or `pip` commands
2. **ALWAYS** use `venv/Scripts/python.exe` (Windows) or `venv/bin/python` (Linux/Mac)
3. **ALWAYS** update requirements.txt after package changes
4. **NEVER** commit the venv folder to git

**Code Quality:**
5. **ALWAYS** add type hints to public functions
6. **ALWAYS** write docstrings for classes and functions
7. **ALWAYS** maintain 80%+ test coverage
8. **ALWAYS** follow PEP 8 naming conventions

---

## Quick Reference Card

**Windows:**
```bash
# Python
venv/Scripts/python.exe

# Pip
venv/Scripts/python.exe -m pip

# Django manage.py
venv/Scripts/python.exe manage.py

# Tests
venv/Scripts/python.exe -m pytest
```

**Linux/Mac:**
```bash
# Python
venv/bin/python

# Pip
venv/bin/python -m pip

# Django manage.py
venv/bin/python manage.py

# Tests
venv/bin/python -m pytest
```
