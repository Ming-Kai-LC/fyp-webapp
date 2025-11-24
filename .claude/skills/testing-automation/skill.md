# Testing & Git Workflow Automation

**Version:** 2.0.0
**Last Updated:** 2025-11-24
**Auto-apply:** YES - Automatically triggers during code generation, commits, and PRs

---

## Purpose

This skill ensures comprehensive automated testing throughout the development lifecycle with four levels of automation:
1. **Pre-commit hooks** - Fast quality gates before commits
2. **GitHub Actions CI/CD** - Full test suite on push/PR
3. **Test generation guidance** - Comprehensive test patterns for all code
4. **Coverage enforcement** - Maintain ≥80% test coverage

---

## When This Skill Auto-Triggers

Claude Code should **automatically apply this skill** when:
- Any code is written or modified
- New module/feature is being created (integrates with `module-creation-lifecycle`)
- User asks to "test this", "run tests", "check if it works"
- Before creating git commits
- User requests to create a PR
- User mentions "testing", "test coverage", "CI/CD"

**Examples:**
- "Create a new appointment module" → Auto-creates tests during development
- "Update the prediction model" → Auto-runs tests after changes
- "Commit these changes" → Auto-runs pre-commit hooks
- "Create a PR" → Auto-verifies tests pass and coverage ≥80%

---

## Testing Philosophy

### Core Principles

1. **Test-Driven Development (TDD) Preferred**
   - Write tests DURING development, not after
   - Tests define expected behavior
   - Red → Green → Refactor cycle

2. **Comprehensive Coverage**
   - Unit tests: Test individual functions/methods
   - Integration tests: Test component interactions
   - Permission tests: Test role-based access control
   - API tests: Test all endpoints with all roles
   - E2E tests: Test complete user workflows

3. **Fast Feedback**
   - Pre-commit hooks: <10 seconds (fast unit tests only)
   - CI/CD pipeline: <5 minutes (full test suite)
   - Developers notified immediately on failure

4. **Quality Gates**
   - All tests must pass before merge
   - Coverage must be ≥80%
   - No security vulnerabilities
   - Code quality checks pass (black, flake8)

---

## Level 1: Pre-commit Hooks

**Purpose:** Fast quality checks before allowing commits. Catch errors early.

### Configuration File

Create `.pre-commit-config.yaml` in project root:

```yaml
# .pre-commit-config.yaml
# Pre-commit hooks for code quality and fast testing

repos:
  # Code formatting
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.11
        args: ['--line-length=100']

  # Import sorting
  - repo: https://github.com/PyCQA/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ['--profile', 'black', '--line-length', '100']

  # Linting
  - repo: https://github.com/PyCQA/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=100', '--extend-ignore=E203,W503']
        additional_dependencies:
          - flake8-docstrings
          - flake8-bugbear

  # Type checking
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        args: ['--ignore-missing-imports', '--no-strict-optional']
        additional_dependencies:
          - django-stubs
          - djangorestframework-stubs

  # Django checks
  - repo: local
    hooks:
      - id: django-check
        name: Django system check
        entry: venv/Scripts/python.exe
        args: ['manage.py', 'check']
        language: system
        pass_filenames: false
        always_run: true

      - id: django-check-migrations
        name: Check for missing migrations
        entry: venv/Scripts/python.exe
        args: ['manage.py', 'makemigrations', '--check', '--dry-run']
        language: system
        pass_filenames: false
        always_run: true

  # Fast unit tests (< 10 seconds)
  - repo: local
    hooks:
      - id: pytest-fast
        name: Fast unit tests
        entry: venv/Scripts/python.exe
        args: ['-m', 'pytest', '-m', 'unit', '--maxfail=1', '-q']
        language: system
        pass_filenames: false
        types: [python]

  # Security checks
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ['-r', 'detection', 'api', 'dashboards', '-ll']

  # YAML validation
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-yaml
      - id: check-json
      - id: check-toml
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: mixed-line-ending

  # Secrets detection
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
        exclude: package-lock.json
```

### Installation

```bash
# Install pre-commit
venv/Scripts/pip.exe install pre-commit

# Install git hooks
venv/Scripts/python.exe -m pre_commit install

# Run manually to test
venv/Scripts/python.exe -m pre_commit run --all-files
```

### Fast Test Marker

In `pytest.ini`, add marker for fast tests:

```ini
[pytest]
markers =
    unit: Fast unit tests (< 1 second each)
    integration: Integration tests (1-5 seconds)
    slow: Slow tests (> 5 seconds), e.g., ML inference
    permission: Permission/access control tests
    api: API endpoint tests
    e2e: End-to-end workflow tests
```

Mark fast tests with `@pytest.mark.unit`:

```python
import pytest

@pytest.mark.unit
def test_appointment_str(sample_appointment):
    """Fast unit test for __str__ method."""
    assert str(sample_appointment) == f"Appointment for {sample_appointment.patient}"
```

### When Pre-commit Hooks Run

**Automatically runs on:**
- `git commit` - Blocks commit if any check fails
- `git commit --no-verify` - Bypasses hooks (NEVER use unless emergency)

**Manual run:**
```bash
venv/Scripts/python.exe -m pre_commit run --all-files
```

### Expected Behavior

```
$ git commit -m "Add appointment feature"

black....................................................................Passed
isort....................................................................Passed
flake8...................................................................Passed
mypy.....................................................................Passed
Django system check......................................................Passed
Check for missing migrations.............................................Passed
Fast unit tests..........................................................Passed
bandit...................................................................Passed
check yaml...............................................................Passed
detect-secrets...........................................................Passed

[main abc1234] Add appointment feature
 10 files changed, 500 insertions(+)
```

If ANY check fails:
```
$ git commit -m "Add appointment feature"

black....................................................................Failed
- hook id: black
- files were modified by this hook

reformatted detection/models.py
1 file reformatted.

# Commit blocked! Fix the issues and try again.
```

---

## Level 2: GitHub Actions CI/CD

**Purpose:** Full test suite on every push/PR with comprehensive checks and quality gates.

### Workflow Configuration

Create `.github/workflows/django-ci.yml`:

```yaml
# .github/workflows/django-ci.yml
# Continuous Integration workflow for Django app

name: Django CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: ['3.11', '3.12']

    services:
      # PostgreSQL for testing (production-like environment)
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      # Checkout code
      - name: Checkout code
        uses: actions/checkout@v4

      # Setup Python
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      # Install dependencies
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-django pytest-cov coverage

      # Run Django checks
      - name: Run Django system checks
        run: |
          python manage.py check --deploy
        env:
          DJANGO_SETTINGS_MODULE: config.settings
          SECRET_KEY: test-secret-key-for-ci

      # Check for missing migrations
      - name: Check for missing migrations
        run: |
          python manage.py makemigrations --check --dry-run --no-input
        env:
          DJANGO_SETTINGS_MODULE: config.settings
          SECRET_KEY: test-secret-key-for-ci

      # Run migrations
      - name: Run migrations
        run: |
          python manage.py migrate --no-input
        env:
          DJANGO_SETTINGS_MODULE: config.settings
          SECRET_KEY: test-secret-key-for-ci
          DATABASE_URL: postgresql://test_user:test_password@localhost:5432/test_db

      # Run tests with coverage
      - name: Run tests with coverage
        run: |
          pytest --cov=detection --cov=api --cov=dashboards --cov=reporting --cov=audit \
                 --cov-report=xml --cov-report=html --cov-report=term \
                 --cov-fail-under=80 \
                 -v --tb=short
        env:
          DJANGO_SETTINGS_MODULE: config.settings
          SECRET_KEY: test-secret-key-for-ci
          DATABASE_URL: postgresql://test_user:test_password@localhost:5432/test_db

      # Upload coverage to Codecov
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          flags: unittests
          name: codecov-umbrella
          fail_ci_if_error: true

      # Upload HTML coverage report as artifact
      - name: Upload coverage HTML report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: coverage-report-${{ matrix.python-version }}
          path: htmlcov/

      # Security check with bandit
      - name: Security check (bandit)
        run: |
          pip install bandit
          bandit -r detection api dashboards reporting audit notifications -ll -f json -o bandit-report.json
        continue-on-error: false

      # Upload bandit report
      - name: Upload bandit security report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: bandit-report-${{ matrix.python-version }}
          path: bandit-report.json

      # Dependency vulnerability check
      - name: Check dependencies for vulnerabilities
        run: |
          pip install safety
          safety check --json --output safety-report.json
        continue-on-error: false

      # Upload safety report
      - name: Upload safety report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: safety-report-${{ matrix.python-version }}
          path: safety-report.json

      # Code quality check
      - name: Code quality (flake8)
        run: |
          pip install flake8
          flake8 detection api dashboards reporting audit --max-line-length=100 --statistics

  # Separate job for deployment (only on main branch)
  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Deploy to staging
        run: |
          echo "Deploying to staging environment..."
          # Add your deployment script here
```

### Branch Protection Rules

Configure in GitHub → Settings → Branches → Branch protection rules for `main`:

```
✅ Require pull request reviews before merging
✅ Require status checks to pass before merging
   ✅ Django CI / test (Python 3.11)
   ✅ Django CI / test (Python 3.12)
✅ Require branches to be up to date before merging
✅ Require conversation resolution before merging
✅ Do not allow bypassing the above settings
```

### Expected Behavior

**On Push/PR:**
1. GitHub Actions automatically runs
2. Runs on Python 3.11 and 3.12 (matrix)
3. Installs dependencies
4. Runs Django checks
5. Checks for missing migrations
6. Runs migrations on test database
7. Runs full test suite with coverage
8. Fails if coverage < 80%
9. Runs security checks (bandit, safety)
10. Uploads coverage report to Codecov
11. Uploads artifacts (coverage HTML, security reports)

**Pull Request Status:**
```
✅ Django CI / test (Python 3.11) — Tests passed, coverage 85%
✅ Django CI / test (Python 3.12) — Tests passed, coverage 85%
✅ All checks have passed

[Merge pull request] button enabled
```

**If tests fail or coverage < 80%:**
```
❌ Django CI / test (Python 3.11) — Tests failed
   Details: 5 tests failed, coverage 75% (below 80% threshold)

[Merge pull request] button disabled
```

---

## Level 3: Test Generation Guidance

**Purpose:** Comprehensive patterns for generating tests for all code types.

### Test Organization Structure

```
<module>/tests/
├── __init__.py
├── conftest.py              # Fixtures and test configuration
├── factories.py             # Factory Boy factories for test data
├── test_models.py           # Model tests
├── test_forms.py            # Form tests
├── test_views.py            # View tests (includes permission tests)
├── test_services.py         # Service layer tests
├── test_api.py              # API endpoint tests
├── test_integration.py      # Integration tests
└── test_e2e.py              # End-to-end workflow tests
```

### Test Fixtures (conftest.py)

Create reusable fixtures for all modules:

```python
# <module>/tests/conftest.py
import pytest
from django.contrib.auth.models import User
from detection.models import UserProfile, Patient
from appointments.models import Appointment
from appointments.constants import AppointmentStatus


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    user = User.objects.create_user(
        username='admin',
        email='admin@test.com',
        password='testpass123'
    )
    UserProfile.objects.create(user=user, role='admin')
    return user


@pytest.fixture
def staff_user(db):
    """Create a staff user."""
    user = User.objects.create_user(
        username='staff',
        email='staff@test.com',
        password='testpass123'
    )
    UserProfile.objects.create(user=user, role='staff')
    return user


@pytest.fixture
def patient_user(db):
    """Create a patient user."""
    user = User.objects.create_user(
        username='patient',
        email='patient@test.com',
        password='testpass123'
    )
    profile = UserProfile.objects.create(user=user, role='patient')
    patient = Patient.objects.create(
        user=user,
        first_name='John',
        last_name='Doe',
        date_of_birth='1990-01-01'
    )
    return user


@pytest.fixture
def sample_appointment(db, patient_user):
    """Create a sample appointment."""
    from django.utils import timezone

    patient = Patient.objects.get(user=patient_user)
    appointment = Appointment.objects.create(
        patient=patient,
        scheduled_date=timezone.now() + timezone.timedelta(days=1),
        status=AppointmentStatus.SCHEDULED,
        appointment_type='consultation'
    )
    return appointment


@pytest.fixture
def api_client():
    """Create API client."""
    from rest_framework.test import APIClient
    return APIClient()
```

### Factory Pattern (Optional but Recommended)

```python
# <module>/tests/factories.py
import factory
from factory.django import DjangoModelFactory
from django.utils import timezone
from appointments.models import Appointment
from appointments.constants import AppointmentStatus


class AppointmentFactory(DjangoModelFactory):
    class Meta:
        model = Appointment

    patient = factory.SubFactory('detection.tests.factories.PatientFactory')
    scheduled_date = factory.LazyFunction(lambda: timezone.now() + timezone.timedelta(days=1))
    status = AppointmentStatus.SCHEDULED
    appointment_type = 'consultation'
    notes = factory.Faker('text', max_nb_chars=200)


# Usage in tests:
# appointment = AppointmentFactory()
# appointments = AppointmentFactory.create_batch(5)
```

### 1. Model Tests Pattern

```python
# tests/test_models.py
import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from appointments.models import Appointment
from appointments.constants import AppointmentStatus


@pytest.mark.django_db
class TestAppointmentModel:
    """Tests for Appointment model."""

    def test_str_representation(self, sample_appointment):
        """Test __str__ method returns expected format."""
        expected = f"Appointment for {sample_appointment.patient}"
        assert str(sample_appointment) == expected

    def test_created_at_auto_set(self, sample_appointment):
        """Test created_at is automatically set."""
        assert sample_appointment.created_at is not None
        assert sample_appointment.created_at <= timezone.now()

    def test_updated_at_auto_updates(self, sample_appointment):
        """Test updated_at changes on save."""
        old_updated = sample_appointment.updated_at
        sample_appointment.notes = "Updated notes"
        sample_appointment.save()
        assert sample_appointment.updated_at > old_updated

    def test_upcoming_queryset(self, patient_user):
        """Test upcoming() queryset method."""
        patient = patient_user.patient

        # Create future and past appointments
        future = Appointment.objects.create(
            patient=patient,
            scheduled_date=timezone.now() + timezone.timedelta(days=1),
            status=AppointmentStatus.SCHEDULED
        )
        past = Appointment.objects.create(
            patient=patient,
            scheduled_date=timezone.now() - timezone.timedelta(days=1),
            status=AppointmentStatus.COMPLETED
        )

        upcoming = Appointment.objects.upcoming()
        assert future in upcoming
        assert past not in upcoming

    def test_for_patient_queryset(self, patient_user, staff_user):
        """Test for_patient() queryset method."""
        patient1 = patient_user.patient
        patient2 = Patient.objects.create(
            user=staff_user,
            first_name='Jane',
            last_name='Smith'
        )

        appt1 = Appointment.objects.create(
            patient=patient1,
            scheduled_date=timezone.now() + timezone.timedelta(days=1),
            status=AppointmentStatus.SCHEDULED
        )
        appt2 = Appointment.objects.create(
            patient=patient2,
            scheduled_date=timezone.now() + timezone.timedelta(days=1),
            status=AppointmentStatus.SCHEDULED
        )

        patient1_appts = Appointment.objects.for_patient(patient1)
        assert appt1 in patient1_appts
        assert appt2 not in patient1_appts

    @pytest.mark.parametrize('status', [
        AppointmentStatus.SCHEDULED,
        AppointmentStatus.CONFIRMED,
        AppointmentStatus.CANCELLED,
        AppointmentStatus.COMPLETED,
        AppointmentStatus.NO_SHOW,
    ])
    def test_valid_status_choices(self, patient_user, status):
        """Test all valid status choices."""
        patient = patient_user.patient
        appointment = Appointment.objects.create(
            patient=patient,
            scheduled_date=timezone.now() + timezone.timedelta(days=1),
            status=status
        )
        assert appointment.status == status

    def test_invalid_status_raises_error(self, patient_user):
        """Test invalid status raises ValidationError."""
        patient = patient_user.patient
        with pytest.raises(ValidationError):
            appointment = Appointment(
                patient=patient,
                scheduled_date=timezone.now() + timezone.timedelta(days=1),
                status='invalid_status'
            )
            appointment.full_clean()  # Trigger validation
```

### 2. Form Tests Pattern

```python
# tests/test_forms.py
import pytest
from django.utils import timezone
from appointments.forms import AppointmentForm
from appointments.constants import AppointmentType, ERROR_PAST_DATE, ERROR_OUTSIDE_HOURS


@pytest.mark.django_db
class TestAppointmentForm:
    """Tests for AppointmentForm."""

    def test_valid_form(self, patient_user):
        """Test form with valid data."""
        patient = patient_user.patient
        scheduled_date = timezone.now() + timezone.timedelta(days=1)
        scheduled_date = scheduled_date.replace(hour=10, minute=0)  # 10 AM

        form_data = {
            'patient': patient.id,
            'scheduled_date': scheduled_date,
            'appointment_type': AppointmentType.CONSULTATION,
            'notes': 'Test appointment'
        }
        form = AppointmentForm(data=form_data)
        assert form.is_valid(), form.errors

    def test_past_date_invalid(self, patient_user):
        """Test form rejects past dates."""
        patient = patient_user.patient
        past_date = timezone.now() - timezone.timedelta(days=1)

        form_data = {
            'patient': patient.id,
            'scheduled_date': past_date,
            'appointment_type': AppointmentType.CONSULTATION,
        }
        form = AppointmentForm(data=form_data)
        assert not form.is_valid()
        assert ERROR_PAST_DATE in form.errors['scheduled_date'][0]

    @pytest.mark.parametrize('hour', [8, 18, 20])
    def test_outside_business_hours_invalid(self, patient_user, hour):
        """Test form rejects times outside business hours."""
        patient = patient_user.patient
        scheduled_date = timezone.now() + timezone.timedelta(days=1)
        scheduled_date = scheduled_date.replace(hour=hour, minute=0)

        form_data = {
            'patient': patient.id,
            'scheduled_date': scheduled_date,
            'appointment_type': AppointmentType.CONSULTATION,
        }
        form = AppointmentForm(data=form_data)
        assert not form.is_valid()
        assert ERROR_OUTSIDE_HOURS in form.errors['scheduled_date'][0]

    def test_missing_required_fields(self):
        """Test form requires all required fields."""
        form = AppointmentForm(data={})
        assert not form.is_valid()
        assert 'patient' in form.errors
        assert 'scheduled_date' in form.errors
        assert 'appointment_type' in form.errors
```

### 3. View Tests Pattern (with Permissions)

```python
# tests/test_views.py
import pytest
from django.urls import reverse
from appointments.models import Appointment


@pytest.mark.django_db
class TestAppointmentListView:
    """Tests for AppointmentListView."""

    def test_unauthenticated_redirects_to_login(self, client):
        """Test unauthenticated user redirected to login."""
        url = reverse('appointments:list')
        response = client.get(url)
        assert response.status_code == 302
        assert '/login/' in response.url

    def test_patient_sees_only_own_appointments(self, client, patient_user):
        """Test patient can only see their own appointments."""
        # Login as patient
        client.force_login(patient_user)

        # Create appointment for this patient
        patient = patient_user.patient
        appt1 = Appointment.objects.create(
            patient=patient,
            scheduled_date=timezone.now() + timezone.timedelta(days=1),
            status=AppointmentStatus.SCHEDULED
        )

        # Create appointment for different patient
        other_user = User.objects.create_user(username='other', password='test')
        other_patient = Patient.objects.create(user=other_user, first_name='Other')
        appt2 = Appointment.objects.create(
            patient=other_patient,
            scheduled_date=timezone.now() + timezone.timedelta(days=1),
            status=AppointmentStatus.SCHEDULED
        )

        url = reverse('appointments:list')
        response = client.get(url)

        assert response.status_code == 200
        assert appt1 in response.context['appointments']
        assert appt2 not in response.context['appointments']

    def test_staff_sees_all_appointments(self, client, staff_user, sample_appointment):
        """Test staff can see all appointments."""
        client.force_login(staff_user)

        url = reverse('appointments:list')
        response = client.get(url)

        assert response.status_code == 200
        assert sample_appointment in response.context['appointments']

    def test_admin_sees_all_appointments(self, client, admin_user, sample_appointment):
        """Test admin can see all appointments."""
        client.force_login(admin_user)

        url = reverse('appointments:list')
        response = client.get(url)

        assert response.status_code == 200
        assert sample_appointment in response.context['appointments']


@pytest.mark.django_db
class TestAppointmentCreateView:
    """Tests for AppointmentCreateView."""

    def test_patient_cannot_create_appointment(self, client, patient_user):
        """Test patient cannot access create view."""
        client.force_login(patient_user)

        url = reverse('appointments:create')
        response = client.get(url)

        assert response.status_code == 403  # Forbidden

    def test_staff_can_create_appointment(self, client, staff_user, patient_user):
        """Test staff can create appointments."""
        client.force_login(staff_user)

        patient = patient_user.patient
        scheduled_date = timezone.now() + timezone.timedelta(days=1)
        scheduled_date = scheduled_date.replace(hour=10, minute=0)

        url = reverse('appointments:create')
        data = {
            'patient': patient.id,
            'scheduled_date': scheduled_date.strftime('%Y-%m-%dT%H:%M'),
            'appointment_type': AppointmentType.CONSULTATION,
            'notes': 'Test'
        }
        response = client.post(url, data)

        assert response.status_code == 302  # Redirect on success
        assert Appointment.objects.filter(patient=patient).exists()
```

### 4. Service Tests Pattern

```python
# tests/test_services.py
import pytest
from unittest.mock import patch, MagicMock
from django.core.exceptions import ValidationError
from appointments.services.appointment_service import AppointmentService
from appointments.constants import ERROR_APPOINTMENT_CONFLICT


@pytest.mark.django_db
class TestAppointmentService:
    """Tests for AppointmentService."""

    def test_create_appointment_success(self, patient_user):
        """Test successful appointment creation."""
        patient = patient_user.patient
        scheduled_date = timezone.now() + timezone.timedelta(days=1)
        scheduled_date = scheduled_date.replace(hour=10, minute=0)

        appointment = AppointmentService.create_appointment(
            patient=patient,
            scheduled_date=scheduled_date,
            appointment_type=AppointmentType.CONSULTATION,
            notes='Test',
            created_by=patient_user
        )

        assert appointment.id is not None
        assert appointment.patient == patient
        assert appointment.status == AppointmentStatus.SCHEDULED

    def test_create_appointment_with_conflict_raises_error(self, patient_user):
        """Test appointment creation fails when conflict exists."""
        patient = patient_user.patient
        scheduled_date = timezone.now() + timezone.timedelta(days=1)
        scheduled_date = scheduled_date.replace(hour=10, minute=0)

        # Create first appointment
        Appointment.objects.create(
            patient=patient,
            scheduled_date=scheduled_date,
            status=AppointmentStatus.SCHEDULED
        )

        # Try to create conflicting appointment
        with pytest.raises(ValidationError) as exc_info:
            AppointmentService.create_appointment(
                patient=patient,
                scheduled_date=scheduled_date,
                appointment_type=AppointmentType.CONSULTATION
            )

        assert ERROR_APPOINTMENT_CONFLICT in str(exc_info.value)

    @patch('appointments.services.appointment_service.AppointmentService._send_confirmation_email')
    def test_create_appointment_sends_email(self, mock_send_email, patient_user):
        """Test confirmation email sent on appointment creation."""
        patient = patient_user.patient
        scheduled_date = timezone.now() + timezone.timedelta(days=1)
        scheduled_date = scheduled_date.replace(hour=10, minute=0)

        appointment = AppointmentService.create_appointment(
            patient=patient,
            scheduled_date=scheduled_date,
            appointment_type=AppointmentType.CONSULTATION
        )

        mock_send_email.assert_called_once_with(appointment)
```

### 5. API Tests Pattern

```python
# tests/test_api.py
import pytest
from django.urls import reverse
from rest_framework import status
from appointments.models import Appointment


@pytest.mark.django_db
class TestAppointmentAPI:
    """Tests for Appointment API endpoints."""

    def test_list_appointments_unauthenticated(self, api_client):
        """Test unauthenticated request returns 401."""
        url = reverse('api:appointment-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_appointments_as_patient(self, api_client, patient_user, sample_appointment):
        """Test patient sees only own appointments via API."""
        api_client.force_authenticate(user=patient_user)

        # Create appointment for different patient
        other_user = User.objects.create_user(username='other', password='test')
        other_patient = Patient.objects.create(user=other_user, first_name='Other')
        other_appt = Appointment.objects.create(
            patient=other_patient,
            scheduled_date=timezone.now() + timezone.timedelta(days=1),
            status=AppointmentStatus.SCHEDULED
        )

        url = reverse('api:appointment-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        appointment_ids = [appt['id'] for appt in response.data['results']]
        assert sample_appointment.id in appointment_ids
        assert other_appt.id not in appointment_ids

    def test_create_appointment_as_staff(self, api_client, staff_user, patient_user):
        """Test staff can create appointments via API."""
        api_client.force_authenticate(user=staff_user)

        patient = patient_user.patient
        scheduled_date = timezone.now() + timezone.timedelta(days=1)
        scheduled_date = scheduled_date.replace(hour=10, minute=0)

        url = reverse('api:appointment-list')
        data = {
            'patient': patient.id,
            'scheduled_date': scheduled_date.isoformat(),
            'appointment_type': AppointmentType.CONSULTATION,
            'notes': 'API test'
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert Appointment.objects.filter(patient=patient).exists()

    def test_create_appointment_as_patient_forbidden(self, api_client, patient_user):
        """Test patient cannot create appointments via API."""
        api_client.force_authenticate(user=patient_user)

        patient = patient_user.patient
        scheduled_date = timezone.now() + timezone.timedelta(days=1)

        url = reverse('api:appointment-list')
        data = {
            'patient': patient.id,
            'scheduled_date': scheduled_date.isoformat(),
            'appointment_type': AppointmentType.CONSULTATION
        }
        response = api_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN
```

### 6. Integration Tests Pattern

```python
# tests/test_integration.py
import pytest
from appointments.services.appointment_service import AppointmentService
from notifications.models import Notification


@pytest.mark.integration
@pytest.mark.django_db
class TestAppointmentNotificationIntegration:
    """Integration tests between appointments and notifications."""

    def test_creating_appointment_creates_notification(self, patient_user):
        """Test appointment creation triggers notification."""
        patient = patient_user.patient
        scheduled_date = timezone.now() + timezone.timedelta(days=1)

        appointment = AppointmentService.create_appointment(
            patient=patient,
            scheduled_date=scheduled_date,
            appointment_type=AppointmentType.CONSULTATION,
            created_by=patient_user
        )

        # Verify notification created
        notification = Notification.objects.filter(
            user=patient_user,
            related_object_id=appointment.id
        ).first()

        assert notification is not None
        assert 'appointment' in notification.message.lower()
```

### 7. End-to-End Tests Pattern

```python
# tests/test_e2e.py
import pytest
from django.urls import reverse


@pytest.mark.e2e
@pytest.mark.django_db
class TestAppointmentE2E:
    """End-to-end tests for complete appointment workflow."""

    def test_complete_appointment_workflow(self, client, staff_user, patient_user):
        """Test complete workflow: create → confirm → complete appointment."""
        # 1. Staff logs in
        client.force_login(staff_user)

        # 2. Staff creates appointment
        patient = patient_user.patient
        scheduled_date = timezone.now() + timezone.timedelta(days=1)

        create_url = reverse('appointments:create')
        data = {
            'patient': patient.id,
            'scheduled_date': scheduled_date.strftime('%Y-%m-%dT%H:%M'),
            'appointment_type': AppointmentType.CONSULTATION,
        }
        response = client.post(create_url, data)
        assert response.status_code == 302

        # 3. Verify appointment created
        appointment = Appointment.objects.get(patient=patient)
        assert appointment.status == AppointmentStatus.SCHEDULED

        # 4. Patient logs in and views appointment
        client.force_login(patient_user)
        list_url = reverse('appointments:list')
        response = client.get(list_url)
        assert appointment in response.context['appointments']

        # 5. Staff confirms appointment
        client.force_login(staff_user)
        confirm_url = reverse('appointments:confirm', kwargs={'pk': appointment.pk})
        response = client.post(confirm_url)

        appointment.refresh_from_db()
        assert appointment.status == AppointmentStatus.CONFIRMED

        # 6. Staff completes appointment
        complete_url = reverse('appointments:complete', kwargs={'pk': appointment.pk})
        response = client.post(complete_url)

        appointment.refresh_from_db()
        assert appointment.status == AppointmentStatus.COMPLETED
```

---

## Level 4: Coverage Enforcement

**Purpose:** Maintain ≥80% test coverage across all modules.

### pytest Configuration

Update `pytest.ini`:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = tests.py test_*.py *_tests.py
python_classes = Test*
python_functions = test_*

addopts =
    --verbose
    --strict-markers
    --tb=short
    --cov=detection
    --cov=api
    --cov=dashboards
    --cov=reporting
    --cov=audit
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=80
    --cov-branch

markers =
    unit: Fast unit tests
    integration: Integration tests
    slow: Slow tests (ML inference, file uploads)
    permission: Permission/access control tests
    api: API endpoint tests
    e2e: End-to-end workflow tests

testpaths = .

filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

### Running Coverage Reports

```bash
# Run tests with coverage
venv/Scripts/python.exe -m pytest --cov=appointments --cov-report=term-missing

# Generate HTML report
venv/Scripts/python.exe -m pytest --cov=appointments --cov-report=html

# Open HTML report
start htmlcov/index.html  # Windows

# Generate XML report (for CI/CD)
venv/Scripts/python.exe -m pytest --cov=appointments --cov-report=xml

# Fail if coverage below 80%
venv/Scripts/python.exe -m pytest --cov=appointments --cov-fail-under=80
```

### Coverage Report Example

```
Name                              Stmts   Miss Branch BrPart  Cover   Missing
-----------------------------------------------------------------------------
appointments/__init__.py              0      0      0      0   100%
appointments/admin.py                24      0      4      0   100%
appointments/constants.py            12      0      0      0   100%
appointments/forms.py                45      2      8      1    95%   67, 89
appointments/models.py               67      3     12      2    93%   102-104, 156
appointments/services.py             89      5     18      3    92%   234-236, 267, 301
appointments/views.py                56      8     10      2    82%   45-48, 103-108
appointments/urls.py                  8      0      0      0   100%
-----------------------------------------------------------------------------
TOTAL                               301     18     52      8    91%

Coverage: 91% (above 80% threshold) ✅
```

### Coverage Quality Gates

**Minimum Coverage by Module Type:**
- **Models:** 90%+
- **Services:** 85%+
- **Forms:** 85%+
- **Views:** 80%+
- **APIs:** 85%+
- **Utils:** 90%+

**Overall Project:** 80%+

### Handling Uncovered Lines

**For intentionally uncovered code:**

```python
def some_function():
    if DEBUG:  # pragma: no cover
        # This code only runs in development, skip coverage
        print("Debug mode")
```

**For deprecated code:**

```python
# pragma: no cover start
def old_deprecated_function():
    """Deprecated, will be removed."""
    pass
# pragma: no cover end
```

---

## Integration with TodoWrite Tool

**Automatically create testing todos during development:**

```
After creating models.py:
- [ ] Create test_models.py
- [ ] Test all model methods
- [ ] Test model validation
- [ ] Test model querysets
- [ ] Verify 90%+ model coverage

After creating forms.py:
- [ ] Create test_forms.py
- [ ] Test valid form data
- [ ] Test invalid form data
- [ ] Test field validation
- [ ] Verify 85%+ form coverage

After creating views.py:
- [ ] Create test_views.py
- [ ] Test all HTTP methods (GET, POST, PUT, DELETE)
- [ ] Test permission enforcement (admin/staff/patient)
- [ ] Test unauthenticated access
- [ ] Verify 80%+ view coverage

After creating services/:
- [ ] Create test_services.py
- [ ] Test all service methods
- [ ] Mock external dependencies
- [ ] Test error handling
- [ ] Verify 85%+ service coverage

After creating API:
- [ ] Create test_api.py
- [ ] Test all endpoints with all roles
- [ ] Test pagination
- [ ] Test filtering
- [ ] Verify 85%+ API coverage

Before git commit:
- [ ] Run pre-commit hooks
- [ ] Verify all tests pass
- [ ] Verify coverage ≥ 80%

Before creating PR:
- [ ] Run full test suite locally
- [ ] Verify GitHub Actions will pass
- [ ] Check coverage report
- [ ] Review security scan results
```

---

## Common Testing Patterns

### Mocking External Services

```python
from unittest.mock import patch, MagicMock

@patch('appointments.services.email_service.send_email')
def test_appointment_sends_email(mock_send_email):
    """Test email sending without actually sending."""
    mock_send_email.return_value = True

    # Test code that sends email
    appointment = create_appointment(...)

    # Verify email sending was called
    mock_send_email.assert_called_once()
    args, kwargs = mock_send_email.call_args
    assert 'appointment' in kwargs['subject'].lower()
```

### Testing Transactions

```python
from django.db import transaction

def test_service_rolls_back_on_error(patient_user):
    """Test transaction rollback on error."""
    with pytest.raises(ValidationError):
        with transaction.atomic():
            # This should roll back
            AppointmentService.create_appointment(
                patient=patient_user.patient,
                scheduled_date='invalid',  # Trigger error
                appointment_type='consultation'
            )

    # Verify no appointment created
    assert Appointment.objects.count() == 0
```

### Testing File Uploads

```python
from django.core.files.uploadedfile import SimpleUploadedFile

def test_xray_upload(client, staff_user):
    """Test X-ray image upload."""
    client.force_login(staff_user)

    # Create fake image file
    image_content = b'fake image content'
    image = SimpleUploadedFile(
        name='test.png',
        content=image_content,
        content_type='image/png'
    )

    url = reverse('detection:upload')
    data = {'image': image}
    response = client.post(url, data)

    assert response.status_code == 302
    assert XRayImage.objects.filter(original_image__icontains='test').exists()
```

---

## Success Criteria

Testing automation is complete when:

✅ Pre-commit hooks configured and running
✅ GitHub Actions CI/CD workflow active
✅ All modules have comprehensive tests (unit, integration, permission, API, E2E)
✅ Overall coverage ≥ 80% enforced
✅ Branch protection rules require passing tests
✅ Coverage reports uploaded to Codecov
✅ Security scans pass (bandit, safety)
✅ Pull requests blocked if tests fail or coverage drops

---

## Level 5: Git Workflow & Version Control Automation

**Purpose:** Enforce consistent git practices, commit standards, and code review processes.

### Git Workflow Overview

This project follows a **Git Flow** inspired workflow:

```
main (production-ready)
  ↑
  └─ develop (integration branch)
       ↑
       ├─ feature/feature-name
       ├─ bugfix/issue-number-description
       ├─ hotfix/critical-fix
       └─ release/v1.0.0
```

### Branch Naming Standards

**Feature branches:**
```
feature/<short-description>
feature/<issue-number>-<short-description>
```

**Examples:**
```
feature/appointment-scheduling
feature/123-patient-dashboard
feature/ml-model-caching
```

**Bugfix branches:**
```
bugfix/<issue-number>-<short-description>
bugfix/<short-description>
```

**Examples:**
```
bugfix/456-fix-login-redirect
bugfix/permission-check-error
```

**Hotfix branches:**
```
hotfix/<critical-issue-description>
```

**Examples:**
```
hotfix/security-vulnerability
hotfix/data-leak-patient-records
```

**Release branches:**
```
release/v<major>.<minor>.<patch>
```

**Naming conventions:**
- Use lowercase
- Use hyphens (-) not underscores (_)
- Be descriptive but concise (3-5 words max)
- Include issue number when applicable

### Conventional Commits Format

**All commits MUST follow Conventional Commits specification:**

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Commit Types:**

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(api): Add batch prediction endpoint` |
| `fix` | Bug fix | `fix(auth): Correct permission check for staff` |
| `docs` | Documentation only | `docs(readme): Update installation instructions` |
| `style` | Code style (formatting) | `style(forms): Format with black` |
| `refactor` | Code refactoring | `refactor(services): Extract common logic` |
| `perf` | Performance improvement | `perf(queries): Add select_related for patients` |
| `test` | Adding/updating tests | `test(appointments): Add permission tests` |
| `chore` | Build/tooling changes | `chore(deps): Update Django to 5.1.1` |
| `ci` | CI/CD changes | `ci(github): Add coverage reporting` |
| `security` | Security fixes | `security(api): Fix JWT token expiration` |

**Scopes (module/component affected):**
- `api`, `auth`, `detection`, `appointments`, `dashboards`, `models`, `forms`, `tests`, `deps`

**Subject guidelines:**
- First line, max 72 characters
- Imperative mood ("Add feature" not "Added feature")
- No period at end
- Capitalize first letter
- Clear and concise

**Body (optional but recommended):**
- Explain **why** not **what** (code shows what)
- Separate from subject with blank line
- Wrap at 72 characters

**Footer (optional):**
- Reference issues: `Closes #123`, `Fixes #456`, `Refs #789`
- Breaking changes: `BREAKING CHANGE: Description`
- Co-authors: `Co-Authored-By: Name <email>`

### Complete Commit Example

```
feat(appointments): Add appointment scheduling system

Implement complete appointment scheduling with:
- Staff can create/update/cancel appointments
- Patients can view their own appointments
- Email notifications on creation and reminders
- Conflict detection for time slots
- Business hours validation (9 AM - 5 PM)

This resolves the patient scheduling workflow requirement
and provides foundation for future calendar integration.

Closes #123
Refs #456

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Automated Commit Workflow

**When user requests "commit my changes", Claude Code automatically:**

1. **Run `git status`** - See all untracked files and modifications
2. **Run `git diff`** - Review staged and unstaged changes
3. **Run `git log`** - Check recent commit message style
4. **Analyze changes** - Determine commit type and scope
5. **Draft commit message** - Following Conventional Commits format
6. **Stage relevant files** - Add changed files (never .env, credentials, secrets)
7. **Create commit** - Using HEREDOC for proper formatting:

```bash
git commit -m "$(cat <<'EOF'
feat(appointments): Add appointment scheduling system

Implement appointment booking with business hours validation
and conflict detection for time slots.

Closes #123

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

8. **Run `git status` again** - Verify commit success

**Never commit:**
- `.env` files
- `credentials.json`
- API keys or secrets
- Large binary files (unless explicitly requested)

### Pull Request (PR) Workflow

**When user requests "create a PR", Claude Code automatically:**

1. **Verify branch status** - Check if branch is up to date with remote
2. **Run tests locally** - Ensure tests pass before creating PR
3. **Push branch** - Push to remote with `-u` flag if needed
4. **Analyze all commits** - Review ALL commits that will be included in PR
5. **Generate PR description** - Using template format:

```markdown
## Summary
- Bullet point 1: What changed
- Bullet point 2: Why it changed
- Bullet point 3: Impact/benefits

## Test plan
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Permission tests pass for all roles
- [ ] Manual testing completed
- [ ] API endpoints tested with all roles

## Database changes
- [ ] No migrations needed / Migrations included and tested
- [ ] Backward compatible / Breaking change documented

## Security considerations
- [ ] No security vulnerabilities introduced
- [ ] Input validation implemented
- [ ] OWASP Top 10 compliance maintained

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

6. **Create PR** - Using `gh pr create` command:

```bash
gh pr create --title "feat(appointments): Add appointment scheduling system" --body "$(cat <<'EOF'
## Summary
- Add complete appointment scheduling module
- Staff can create/update/cancel appointments
- Patients can view own appointments
- Email notifications and conflict detection

## Test plan
- [x] Unit tests pass (87% coverage)
- [x] Permission tests pass for all roles
- [x] Manual testing completed
- [x] API endpoints tested

## Database changes
- [x] Migrations included and tested

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

7. **Monitor CI/CD status** - Verify tests pass in GitHub Actions

### Pull Request Template

Create `.github/pull_request_template.md`:

```markdown
## Summary
<!-- Briefly describe what this PR does and why -->

## Type of Change
- [ ] feat: New feature
- [ ] fix: Bug fix
- [ ] docs: Documentation only
- [ ] style: Code style/formatting
- [ ] refactor: Code refactoring
- [ ] perf: Performance improvement
- [ ] test: Adding/updating tests
- [ ] chore: Build/tooling changes
- [ ] security: Security fix

## Related Issues
<!-- Link to related issues: Closes #123, Fixes #456, Refs #789 -->

## Changes Made
<!-- Detailed list of changes -->
- Change 1
- Change 2
- Change 3

## Testing Done
<!-- Describe testing performed -->

### Unit Tests
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Coverage ≥80%

### Integration Tests
- [ ] Integration tests pass
- [ ] API endpoints tested with all roles

### Permission Tests
- [ ] Admin access tested
- [ ] Staff access tested
- [ ] Patient access tested

### Manual Testing
- [ ] Feature tested manually
- [ ] Edge cases tested
- [ ] Error handling tested

## Database Changes
- [ ] No database changes
- [ ] Migrations created and tested
- [ ] Data migration strategy documented
- [ ] Backward compatible

## Security Considerations
- [ ] No security vulnerabilities introduced
- [ ] Input validation implemented
- [ ] OWASP Top 10 compliance maintained
- [ ] Sensitive data handled securely
- [ ] No secrets committed

## Performance Impact
- [ ] No performance impact
- [ ] Performance tested
- [ ] Database queries optimized (N+1 prevention)
- [ ] Caching implemented where appropriate

## Documentation
- [ ] Code comments added where needed
- [ ] Docstrings added for public APIs
- [ ] README updated (if needed)
- [ ] API documentation updated (if needed)

## Checklist Before Requesting Review
- [ ] Code follows project style guide
- [ ] Self-review performed
- [ ] Tests pass locally
- [ ] No merge conflicts
- [ ] Branch is up to date with base branch
- [ ] Commit messages follow Conventional Commits format

## Screenshots (if applicable)
<!-- Add screenshots for UI changes -->

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

### Code Review Guidelines

**For reviewers:**

1. **Correctness** - Does the code work as intended?
2. **Security** - Are there any vulnerabilities?
3. **Performance** - Are queries optimized? Any N+1 problems?
4. **Tests** - Are tests comprehensive? Coverage ≥80%?
5. **Code Quality** - PEP 8 compliant? Type hints? Docstrings?
6. **Design** - Follows project patterns? Uses foundation components?
7. **Documentation** - Clear comments? Updated docs?

**Review checklist:**
- ✅ All CI checks pass (tests, coverage, security)
- ✅ Code follows project patterns and conventions
- ✅ No hardcoded Bootstrap classes (uses widget library)
- ✅ Models inherit from TimeStampedModel or other base models
- ✅ Templates use `{% load common_tags %}`
- ✅ Permission checks implemented for all views
- ✅ Database queries optimized (select_related/prefetch_related)
- ✅ No secrets or sensitive data committed
- ✅ Tests cover new functionality (≥80% coverage)

### Git Commands Reference

**Creating branches:**
```bash
git checkout -b feature/appointment-scheduling
git checkout -b bugfix/123-form-validation
git checkout -b hotfix/security-patch
```

**Committing changes:**
```bash
# Stage files
git add file1.py file2.py

# Commit with Conventional Commits format
git commit -m "feat(appointments): Add scheduling feature"
```

**Pushing to remote:**
```bash
# First push (set upstream)
git push -u origin feature/appointment-scheduling

# Subsequent pushes
git push
```

**Creating PR:**
```bash
gh pr create --title "feat(appointments): Add scheduling" --body "..."
```

### Integration with Testing Levels

**Complete workflow:**

1. **Write code** → Level 3 (Test Generation) - Create tests during development
2. **Commit changes** → Level 1 (Pre-commit) - Fast quality checks (<10 sec)
3. **Push to remote** → Level 2 (CI/CD) - Full test suite (< 5 min)
4. **Create PR** → Level 5 (Git Workflow) - PR template + review checklist
5. **Merge PR** → Level 4 (Coverage) - Verify ≥80% coverage maintained

---

## Complete Testing & Git Workflow Summary

### 5-Level Automation System

| Level | Purpose | When | Duration | Blocks |
|-------|---------|------|----------|--------|
| 1. Pre-commit Hooks | Fast quality gates | Before commit | <10 sec | Commit if fails |
| 2. GitHub Actions CI/CD | Full test suite | On push/PR | <5 min | PR merge if fails |
| 3. Test Generation | Comprehensive tests | During development | N/A | N/A |
| 4. Coverage Enforcement | Maintain quality | On PR | N/A | PR if <80% |
| 5. Git Workflow | Consistent practices | On commit/PR | N/A | N/A |

### Auto-Apply Triggers

**Testing automation applies when:**
- Writing any code
- Creating new modules
- Running tests
- Creating commits
- Creating PRs

**Git workflow applies when:**
- User mentions "commit", "push", "PR"
- Before git commands via Bash
- During code review

### Success Criteria

✅ **Pre-commit:** All checks pass in <10 seconds
✅ **CI/CD:** Full suite passes in <5 minutes
✅ **Tests:** Comprehensive coverage ≥80%
✅ **Coverage:** Maintained across all PRs
✅ **Commits:** Follow Conventional Commits format
✅ **Branches:** Follow naming standards
✅ **PRs:** Use template with complete checklist
✅ **Reviews:** Follow code review guidelines

---

## Version History

- **2.0.0** (2025-11-24): Added Level 5 - Git Workflow & Version Control Automation
- **1.0.0** (2025-11-22): Initial version with 4-level testing automation

---

**Last Updated:** 2025-11-24
**Version:** 2.0.0 (includes Git Workflow Automation)
**Status:** Active
**Includes:** 5-level comprehensive testing & git workflow automation
