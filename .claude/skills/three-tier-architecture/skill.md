# Three-Tier Architecture for Django

**Version:** 1.0.0
**Last Updated:** 2025-11-21
**Status:** Active

## Overview

This skill enforces a **hybrid three-tier architecture** for Django applications, using selective service layers to improve code organization, reusability, and maintainability.

**Architecture Layers:**
1. **Presentation Tier** - Views, templates, forms, API endpoints (thin controllers)
2. **Application Tier** - Service layer with business logic (reusable)
3. **Data Tier** - Django ORM models (data persistence)

**Key Principle:** Use service layers for complex business logic, keep simple CRUD operations in Django's natural MVT pattern.

---

## Auto-Apply Triggers

**Apply this skill when:**
- Creating new Django modules or features
- Implementing complex business workflows (multi-step processes)
- Adding functionality that will be shared between web views and API
- Noticing code duplication between views or API endpoints
- Writing business logic that involves multiple models
- Implementing operations with external integrations
- Refactoring fat views with embedded business logic
- Adding features that need to be testable independently from HTTP layer

---

## Section 1: When to Use Service Layers

### ✅ USE Service Layer For:

**1. Complex Multi-Step Workflows**
```python
# Example: X-ray upload → preprocess → ML inference → save → notify
# This is a complex workflow that should be in a service
```

**2. Business Logic Involving Multiple Models**
```python
# Example: Creating a prediction requires XRayImage + Prediction + Notification
# Service orchestrates these operations
```

**3. Operations Shared Between Interfaces**
```python
# Example: Both web views AND API endpoints need prediction logic
# Service provides single source of truth
```

**4. External Integrations**
```python
# Example: Sending emails, SMS, calling external APIs
# Service encapsulates integration logic
```

**5. Complex Calculations or Algorithms**
```python
# Example: Risk assessment scoring, statistical aggregations
# Service contains calculation logic
```

**6. Operations Requiring Transaction Management**
```python
# Example: Creating multiple related objects that must all succeed or rollback
# Service handles transaction boundaries
```

### ❌ DON'T Use Service Layer For:

**1. Simple CRUD Operations**
```python
# ❌ DON'T create service for:
def list_patients(request):
    patients = Patient.objects.all()
    return render(request, 'list.html', {'patients': patients})
```

**2. Basic Queries**
```python
# ❌ DON'T create service for:
patient = Patient.objects.get(id=patient_id)
```

**3. Model-Specific Methods**
```python
# ❌ DON'T create service for:
class Patient(models.Model):
    def get_age(self):
        # This belongs in the model
        return calculate_age(self.date_of_birth)
```

**4. Simple Form Validation**
```python
# ❌ DON'T create service for:
# Form validators should stay in forms.py
```

---

## Section 2: Service Layer Structure

### Directory Organization

```
app_name/
├── services/                     # Application Tier
│   ├── __init__.py              # Export all services
│   ├── entity_service.py        # Core domain service
│   ├── helper_service.py        # Supporting service
│   └── statistics_service.py    # Aggregation service
├── models.py                     # Data Tier
├── views.py                      # Presentation Tier (thin)
├── forms.py                      # Presentation Tier
└── api/                          # Presentation Tier (API)
```

### Service Class Pattern

```python
# app_name/services/entity_service.py

"""
Entity Service
Brief description of service responsibility
"""

from typing import Optional, Dict, Any
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from app_name.models import Entity
import logging

logger = logging.getLogger(__name__)


class EntityService:
    """
    Service for Entity operations

    Responsibilities:
    - Core workflow orchestration
    - Business rule enforcement
    - Cross-model coordination
    """

    @staticmethod
    def create_entity_workflow(
        data: Dict[str, Any],
        user: User
    ) -> Entity:
        """
        Complete workflow for entity creation

        Args:
            data: Dictionary with entity data
            user: User creating the entity

        Returns:
            Created Entity instance

        Raises:
            ValidationError: If validation fails

        Example:
            >>> entity = EntityService.create_entity_workflow(
            ...     data={'name': 'Test'},
            ...     user=request.user
            ... )
        """
        # 1. Validate
        EntityService._validate_input(data, user)

        # 2. Create
        entity = EntityService._create_entity(data)

        # 3. Post-process
        EntityService._post_creation_tasks(entity, user)

        logger.info(f"Entity created: ID={entity.id}")

        return entity

    @staticmethod
    def _validate_input(data: Dict[str, Any], user: User):
        """Private: Validate inputs"""
        if not user.has_perm('app.add_entity'):
            raise PermissionDenied("No permission")

    @staticmethod
    def _create_entity(data: Dict[str, Any]) -> Entity:
        """Private: Create entity"""
        return Entity.objects.create(**data)

    @staticmethod
    def _post_creation_tasks(entity: Entity, user: User):
        """Private: Handle post-creation tasks"""
        # Send notifications, log audit, etc.
        pass
```

### Service Naming Conventions

| Service Type | Naming Pattern | Example | Responsibility |
|--------------|---------------|---------|----------------|
| **Core Service** | `{Entity}Service` | `PredictionService` | Main business logic for entity |
| **Helper Service** | `{Domain}Service` | `XRayService` | Supporting operations |
| **Statistics** | `StatisticsService` | `StatisticsService` | Data aggregation |
| **Integration** | `{External}Service` | `NotificationService` | External system integration |

---

## Section 3: Real Implementation Example (detection/ module)

### Before: Fat View with Business Logic (BAD)

```python
# detection/views.py - 133 LINES
@login_required
def upload_xray(request):
    """Upload X-ray and run predictions"""
    if request.method == "POST":
        form = XRayUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # ❌ 80+ lines of business logic embedded in view:

            # Save image
            xray = form.save(commit=False)
            xray.patient = patient
            xray.uploaded_by = request.user
            xray.save()

            # Preprocess
            processed_path = apply_clahe(xray.original_image.path)

            # Run ML models
            results = model_ensemble.predict_all_models(processed_path)

            # Save 6 model results (40+ lines)
            prediction = Prediction.objects.create(
                xray=xray,
                crossvit_prediction=results["individual_results"]["crossvit"]["prediction"],
                crossvit_confidence=results["individual_results"]["crossvit"]["confidence"],
                # ... 20+ more fields
            )

            # Send notification
            NotificationService.send_prediction_notification(prediction)

            return redirect("view_results", prediction.id)
```

**Problems:**
- Business logic mixed with HTTP handling
- Cannot reuse in API endpoints
- Hard to test (requires HTTP layer)
- Violates Single Responsibility Principle

---

### After: Service Layer (GOOD)

#### Step 1: Create Service

```python
# detection/services/prediction_service.py

class PredictionService:
    """Core service for COVID-19 prediction workflow"""

    @staticmethod
    def create_prediction_from_xray(
        xray_image_file,
        patient: Patient,
        uploaded_by: User,
        notes: str = ""
    ) -> Prediction:
        """
        Complete prediction pipeline

        Orchestrates:
        1. Save X-ray image
        2. Apply preprocessing
        3. Run 6 ML models
        4. Save prediction
        5. Send notification
        """
        try:
            # Validate
            PredictionService._validate_prediction_request(patient, uploaded_by)

            # Save image
            xray = XRayService.save_xray(
                image_file=xray_image_file,
                patient=patient,
                uploaded_by=uploaded_by,
                notes=notes
            )

            # Preprocess
            processed_path = XRayService.apply_preprocessing(xray)

            # ML inference
            ml_results = PredictionService._run_ml_inference(processed_path)

            # Save prediction
            prediction = PredictionService._save_prediction(xray, ml_results)

            # Notification (don't fail if this fails)
            try:
                NotificationService.send_prediction_notification(prediction)
            except Exception as e:
                logger.error(f"Notification failed: {e}")

            return prediction

        except Exception as e:
            logger.error(f"Prediction failed: {e}", exc_info=True)
            raise
```

#### Step 2: Refactor View (Thin Controller)

```python
# detection/views.py - 66 LINES (50% reduction!)

@login_required
def upload_xray(request):
    """Upload X-ray and run predictions (Thin Controller)"""
    if not request.user.profile.is_staff():
        messages.error(request, "Access denied. Staff only.")
        return redirect("home")

    if request.method == "POST":
        form = XRayUploadForm(request.POST, request.FILES)
        patient_id = request.POST.get("patient_id")

        if form.is_valid():
            try:
                patient = get_object_or_404(Patient, id=patient_id)

                # ✅ Single service call
                prediction = PredictionService.create_prediction_from_xray(
                    xray_image_file=request.FILES['original_image'],
                    patient=patient,
                    uploaded_by=request.user,
                    notes=form.cleaned_data.get('notes', '')
                )

                messages.success(
                    request,
                    f'✅ Analysis complete! Diagnosis: {prediction.final_diagnosis}'
                )
                return redirect("view_results", prediction_id=prediction.id)

            except MLInferenceError as e:
                messages.error(request, f"ML analysis failed: {str(e)}")
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")

    else:
        form = XRayUploadForm()

    patients = Patient.objects.all().select_related("user")
    return render(request, "upload.html", {"form": form, "patients": patients})
```

**Benefits:**
- ✅ View is now a thin controller (HTTP handling only)
- ✅ Business logic reusable in API, CLI, Celery tasks
- ✅ Easy to unit test service without HTTP
- ✅ 50% code reduction in view

---

## Section 4: Service Layer Patterns

### Pattern 1: Workflow Orchestration

**Use Case:** Multi-step process involving multiple operations

```python
class WorkflowService:
    @staticmethod
    def execute_workflow(input_data, user):
        """
        Orchestrate multi-step workflow

        Pattern:
        1. Validate inputs
        2. Execute steps in order
        3. Handle inter-step dependencies
        4. Rollback on failure
        5. Log completion
        """
        with transaction.atomic():
            # Step 1
            result1 = StepOneService.execute(input_data)

            # Step 2 (depends on step 1)
            result2 = StepTwoService.execute(result1)

            # Step 3 (depends on step 2)
            final_result = StepThreeService.execute(result2)

            return final_result
```

### Pattern 2: Permission-Aware Data Access

**Use Case:** Filtering data based on user role

```python
class DataAccessService:
    @staticmethod
    def get_data_for_user(user: User, filters: Dict = None):
        """
        Get data filtered by user permissions

        Pattern:
        1. Check user role
        2. Apply role-based filtering
        3. Apply additional filters
        4. Optimize query
        """
        # Role-based filtering
        if user.profile.is_patient():
            queryset = Model.objects.filter(owner=user)
        elif user.profile.is_staff():
            queryset = Model.objects.all()
        else:
            queryset = Model.objects.none()

        # Additional filters
        if filters:
            queryset = queryset.filter(**filters)

        # Optimization
        return queryset.select_related('related_field')
```

### Pattern 3: Statistics Aggregation

**Use Case:** Dashboard metrics and analytics

```python
class StatisticsService:
    @staticmethod
    def get_dashboard_stats(user: User) -> Dict[str, Any]:
        """
        Aggregate all dashboard statistics

        Pattern:
        1. Multiple independent queries
        2. Aggregate results
        3. Return structured data
        """
        return {
            'total_count': Model.objects.count(),
            'active_count': Model.objects.filter(is_active=True).count(),
            'recent_items': Model.objects.order_by('-created_at')[:10],
            'breakdown': Model.objects.values('category').annotate(
                count=Count('id')
            ),
        }
```

### Pattern 4: External Service Integration

**Use Case:** Email, SMS, payment gateways, etc.

```python
class NotificationService:
    @staticmethod
    def send_notification(user: User, message: str, channel: str = 'email'):
        """
        Send notification via external service

        Pattern:
        1. Validate inputs
        2. Call external service
        3. Handle failures gracefully
        4. Log result
        """
        try:
            if channel == 'email':
                EmailBackend.send(user.email, message)
            elif channel == 'sms':
                SMSBackend.send(user.phone, message)

            logger.info(f"Notification sent to {user.username}")

        except Exception as e:
            logger.error(f"Notification failed: {e}")
            # Don't raise - notification failure shouldn't break workflow
```

---

## Section 5: View Refactoring Checklist

When refactoring a view to use services:

### Step 1: Identify Business Logic

- [ ] Find code that does more than HTTP handling
- [ ] Look for multi-step workflows
- [ ] Identify database operations beyond simple queries
- [ ] Find external service calls
- [ ] Locate complex calculations

### Step 2: Extract to Service

- [ ] Create `services/` directory if it doesn't exist
- [ ] Create service class file (`entity_service.py`)
- [ ] Move business logic to service method
- [ ] Add proper type hints and docstrings
- [ ] Add error handling and logging
- [ ] Make method reusable (no request dependency)

### Step 3: Update View

- [ ] Import service at top of views.py
- [ ] Replace business logic with service call
- [ ] Keep only HTTP handling in view
- [ ] Update error handling for service exceptions
- [ ] Test that view still works

### Step 4: Enable Reusability

- [ ] Update API endpoint to use same service
- [ ] Add unit tests for service
- [ ] Document service usage

---

## Section 6: Testing Strategy

### Unit Tests for Services

```python
# tests/test_services/test_prediction_service.py

from django.test import TestCase
from detection.services import PredictionService
from detection.models import Patient
from django.contrib.auth.models import User


class PredictionServiceTest(TestCase):
    """Test PredictionService independently from HTTP layer"""

    def setUp(self):
        self.user = User.objects.create_user('staff', 'staff@test.com', 'pass')
        self.user.profile.role = 'staff'
        self.user.profile.save()

        self.patient = Patient.objects.create(...)

    def test_create_prediction_success(self):
        """Test successful prediction creation"""
        # No HTTP layer needed - test service directly
        prediction = PredictionService.create_prediction_from_xray(
            xray_image_file=self.create_test_image(),
            patient=self.patient,
            uploaded_by=self.user,
            notes="Test"
        )

        self.assertIsNotNone(prediction)
        self.assertEqual(prediction.xray.patient, self.patient)

    def test_create_prediction_permission_denied(self):
        """Test that non-staff cannot create predictions"""
        patient_user = User.objects.create_user('patient', 'p@test.com', 'pass')
        patient_user.profile.role = 'patient'
        patient_user.profile.save()

        with self.assertRaises(PermissionDenied):
            PredictionService.create_prediction_from_xray(
                xray_image_file=self.create_test_image(),
                patient=self.patient,
                uploaded_by=patient_user,  # Patient trying to upload
                notes=""
            )
```

### Integration Tests for Views

```python
# tests/test_views.py

class ViewIntegrationTest(TestCase):
    """Test views using services"""

    def test_upload_xray_view(self):
        """Test upload view integrates with PredictionService"""
        self.client.force_login(self.staff_user)

        response = self.client.post('/upload/', {
            'patient_id': self.patient.id,
            'original_image': self.create_test_image(),
        })

        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertEqual(Prediction.objects.count(), 1)
```

---

## Section 7: Common Pitfalls and Solutions

### Pitfall 1: Creating God Services

**❌ Bad:**
```python
class MegaService:
    """Handles everything"""
    def do_prediction(self): pass
    def send_email(self): pass
    def calculate_stats(self): pass
    def generate_report(self): pass
    # ... 50 more methods
```

**✅ Good:**
```python
# Separate focused services
class PredictionService:
    """Only prediction logic"""

class EmailService:
    """Only email logic"""

class StatisticsService:
    """Only statistics"""
```

### Pitfall 2: Services Depending on Request Object

**❌ Bad:**
```python
class BadService:
    @staticmethod
    def do_something(request):
        # Service depends on HTTP request
        user = request.user
        data = request.POST
```

**✅ Good:**
```python
class GoodService:
    @staticmethod
    def do_something(user: User, data: Dict):
        # Service takes explicit parameters
        # Can be called from anywhere (view, API, CLI, Celery)
```

### Pitfall 3: Duplicating ORM in Services

**❌ Bad:**
```python
class BadService:
    @staticmethod
    def get_patient(patient_id):
        # Don't wrap simple ORM calls
        return Patient.objects.get(id=patient_id)
```

**✅ Good:**
```python
# Just use ORM directly in view
patient = Patient.objects.get(id=patient_id)

# OR if you need permission filtering:
class GoodService:
    @staticmethod
    def get_patients_for_user(user):
        # Add value: permission filtering
        if user.is_staff:
            return Patient.objects.all()
        return Patient.objects.filter(user=user)
```

### Pitfall 4: No Error Handling in Services

**❌ Bad:**
```python
class BadService:
    @staticmethod
    def process():
        result = external_api.call()  # What if this fails?
        return result
```

**✅ Good:**
```python
class GoodService:
    @staticmethod
    def process():
        try:
            result = external_api.call()
            logger.info("API call successful")
            return result
        except APIError as e:
            logger.error(f"API call failed: {e}")
            raise ServiceError(f"Processing failed: {str(e)}")
```

---

## Section 8: Migration Strategy

### Incremental Migration Approach

**Phase 1: Identify Candidates**
1. Find views with >100 lines
2. Find duplicate logic between views/API
3. Find complex workflows

**Phase 2: Create Services**
1. Start with most complex module
2. Create `services/` directory
3. Implement one service at a time
4. Add tests for each service

**Phase 3: Refactor Views**
1. Update one view at a time
2. Test after each refactoring
3. Ensure all tests pass

**Phase 4: Update APIs**
1. Refactor API endpoints to use services
2. Eliminate duplication

**Phase 5: Document**
1. Add docstrings to all services
2. Update project documentation
3. Create examples for team

---

## Section 9: Integration with Existing Skills

This skill **complements** existing skills:

- **django-module-creation**: Services are part of module structure
- **component-reusability**: Services maximize code reuse
- **performance-optimization**: Services can implement caching, query optimization
- **security-best-practices**: Services enforce business rules and permissions
- **code-quality-standards**: Services are easier to test and document

---

## Section 10: Real-World Examples from Codebase

### Example 1: detection/ Module (IMPLEMENTED)

**Services Created:**
- `XRayService` - X-ray upload and preprocessing
- `PredictionService` - Core COVID prediction workflow
- `StatisticsService` - Dashboard statistics

**Results:**
- `upload_xray()` view: 133 lines → 66 lines (50% reduction)
- `staff_dashboard()` view: 27 lines → 18 lines (33% reduction)
- Business logic now reusable in API endpoints

### Example 2: reporting/ Module (ALREADY EXCELLENT)

**Services Implemented:**
- `ReportGenerator` - PDF report generation
- `BatchReportProcessor` - Batch processing
- `ExcelExporter` - Data export

**Pattern Quality:** ⭐⭐⭐⭐⭐
- Views are thin controllers
- Service orchestrates complex PDF generation
- Reusable across interfaces

### Example 3: medical_records/ Module (ALREADY EXCELLENT)

**Services Implemented:**
- `RiskAssessmentService` - Complex COVID risk calculation

**Pattern Quality:** ⭐⭐⭐⭐⭐
- Static methods for pure functions
- Complex multi-step algorithm
- Well-documented with type hints

---

## Quick Reference

### Service Layer Checklist

When creating a new feature:

- [ ] Does it involve >3 steps? → Use service
- [ ] Will it be used by both web and API? → Use service
- [ ] Does it involve multiple models? → Use service
- [ ] Is it complex business logic? → Use service
- [ ] Is it just CRUD? → Keep in view/model
- [ ] Is it a simple query? → Keep in view
- [ ] Is it model-specific behavior? → Keep in model

### Quick Wins

**Immediate refactoring opportunities:**
1. Any view with >100 lines
2. Duplicate logic in views and API
3. Complex workflows (upload → process → save → notify)
4. External API integrations
5. Statistical aggregations

---

## Summary

**Three-Tier Architecture Pattern:**
- **Presentation Tier:** Thin views/APIs (HTTP handling only)
- **Application Tier:** Services (reusable business logic)
- **Data Tier:** Models (data persistence)

**Key Benefits:**
- ✅ Code reusability (web, API, CLI, Celery share logic)
- ✅ Testability (test business logic without HTTP)
- ✅ Maintainability (single source of truth)
- ✅ Separation of concerns (clear layer boundaries)

**When to Use:**
- ✅ Complex workflows
- ✅ Multi-model operations
- ✅ Shared logic (web + API)
- ❌ Simple CRUD
- ❌ Basic queries

**Implementation Pattern:**
```python
# 1. Create service
class MyService:
    @staticmethod
    def do_workflow(params) -> Result:
        # Business logic here
        return result

# 2. Use in view (thin controller)
def my_view(request):
    # HTTP handling only
    result = MyService.do_workflow(params)
    return render(request, 'template.html', {'result': result})

# 3. Reuse in API
class MyViewSet(viewsets.ViewSet):
    def create(self, request):
        # Same service, different interface
        result = MyService.do_workflow(params)
        return Response(serializer.data)
```

---

**Last Updated:** 2025-11-21
**Version:** 1.0.0
**Status:** Active
**Reference Implementation:** `detection/` module
