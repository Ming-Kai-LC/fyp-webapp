# RESTful API Module - Detailed Specification

## Module Information
- **Module Name:** api
- **Priority:** MEDIUM (Phase 3)
- **Estimated Effort:** 2-3 days
- **Dependencies:** All modules (provides API access to all features)

## Purpose
Provide RESTful API endpoints for mobile app integration, third-party integrations, and programmatic access to the COVID-19 Detection system.

## Features

### Core Features
1. JWT authentication for API access
2. API versioning (v1, v2)
3. RESTful endpoints for all major entities
4. Rate limiting and throttling
5. API documentation (Swagger/OpenAPI)
6. Pagination for list endpoints
7. Filtering and search
8. CORS configuration

### Advanced Features
9. Webhook support for real-time updates
10. Batch operations
11. API key management
12. GraphQL endpoint (optional)
13. WebSocket support for real-time features

---

## Technology Stack

- **Django REST Framework** 3.14.0
- **djangorestframework-simplejwt** 5.3.0 (JWT authentication)
- **drf-yasg** 1.21.7 (Swagger documentation)
- **django-cors-headers** 4.3.0 (CORS support)
- **django-ratelimit** 4.1.0 (Rate limiting)

---

## API Endpoints Overview

### Authentication
- `POST /api/v1/auth/register/` - User registration
- `POST /api/v1/auth/login/` - Login (get JWT tokens)
- `POST /api/v1/auth/logout/` - Logout
- `POST /api/v1/auth/refresh/` - Refresh JWT token
- `POST /api/v1/auth/password/change/` - Change password

### Predictions
- `GET /api/v1/predictions/` - List all predictions
- `GET /api/v1/predictions/{id}/` - Get prediction details
- `POST /api/v1/predictions/upload/` - Upload X-ray and get prediction
- `GET /api/v1/predictions/{id}/explain/` - Get explainability data
- `PATCH /api/v1/predictions/{id}/validate/` - Validate prediction (doctor only)

### Patients
- `GET /api/v1/patients/` - List patients (doctor/admin only)
- `GET /api/v1/patients/{id}/` - Get patient details
- `GET /api/v1/patients/me/` - Get own patient profile
- `PATCH /api/v1/patients/me/` - Update own profile
- `GET /api/v1/patients/{id}/predictions/` - Get patient's predictions
- `GET /api/v1/patients/{id}/appointments/` - Get patient's appointments

### Appointments
- `GET /api/v1/appointments/` - List appointments
- `POST /api/v1/appointments/` - Book appointment
- `GET /api/v1/appointments/{id}/` - Get appointment details
- `PATCH /api/v1/appointments/{id}/` - Update appointment
- `DELETE /api/v1/appointments/{id}/` - Cancel appointment
- `GET /api/v1/appointments/available-slots/` - Get available time slots

### Medical Records
- `GET /api/v1/medical-records/conditions/` - List medical conditions
- `POST /api/v1/medical-records/conditions/` - Add condition
- `GET /api/v1/medical-records/medications/` - List medications
- `GET /api/v1/medical-records/vaccinations/` - List vaccinations
- `POST /api/v1/medical-records/documents/upload/` - Upload document

### Notifications
- `GET /api/v1/notifications/` - List notifications
- `GET /api/v1/notifications/unread/` - Get unread count
- `PATCH /api/v1/notifications/{id}/read/` - Mark as read
- `PATCH /api/v1/notifications/mark-all-read/` - Mark all as read

### Reports
- `POST /api/v1/reports/generate/` - Generate report
- `GET /api/v1/reports/{id}/` - Get report details
- `GET /api/v1/reports/{id}/download/` - Download report PDF

### Analytics (Admin/Doctor only)
- `GET /api/v1/analytics/dashboard/` - Get dashboard statistics
- `GET /api/v1/analytics/trends/` - Get trend data
- `GET /api/v1/analytics/models/` - Get model performance

---

## Implementation

### File: `api/serializers.py`

```python
from rest_framework import serializers
from django.contrib.auth.models import User
from detection.models import UserProfile, Patient, XRayImage, Prediction
from appointments.models import Appointment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['user', 'role', 'phone', 'created_at']


class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    total_xrays = serializers.IntegerField(read_only=True, source='get_total_xrays')
    covid_positive_count = serializers.IntegerField(read_only=True, source='get_covid_positive_count')

    class Meta:
        model = Patient
        fields = [
            'id', 'user', 'age', 'gender', 'date_of_birth',
            'medical_history', 'current_medications', 'emergency_contact',
            'address', 'total_xrays', 'covid_positive_count'
        ]
        read_only_fields = ['id', 'user']


class XRayImageSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)

    class Meta:
        model = XRayImage
        fields = [
            'id', 'patient', 'patient_name', 'uploaded_by', 'uploaded_by_name',
            'original_image', 'processed_image', 'upload_date', 'notes',
            'image_width', 'image_height'
        ]
        read_only_fields = ['id', 'upload_date', 'processed_image']


class PredictionSerializer(serializers.ModelSerializer):
    xray = XRayImageSerializer(read_only=True)
    best_model = serializers.CharField(source='get_best_model', read_only=True)
    model_agreement = serializers.IntegerField(source='get_model_agreement', read_only=True)
    all_predictions = serializers.JSONField(source='get_all_predictions', read_only=True)

    class Meta:
        model = Prediction
        fields = [
            'id', 'xray', 'final_diagnosis', 'consensus_confidence',
            'crossvit_prediction', 'crossvit_confidence',
            'resnet50_prediction', 'resnet50_confidence',
            'densenet121_prediction', 'densenet121_confidence',
            'efficientnet_prediction', 'efficientnet_confidence',
            'vit_prediction', 'vit_confidence',
            'swin_prediction', 'swin_confidence',
            'best_model', 'model_agreement', 'all_predictions',
            'inference_time', 'is_validated', 'validated_at',
            'doctor_notes', 'gradcam_heatmap'
        ]
        read_only_fields = ['id', 'inference_time', 'validated_at']


class PredictionCreateSerializer(serializers.Serializer):
    """
    Serializer for uploading X-ray and creating prediction
    """
    image = serializers.ImageField()
    notes = serializers.CharField(required=False, allow_blank=True)


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'appointment_id', 'patient', 'patient_name',
            'doctor', 'doctor_name', 'appointment_date', 'appointment_time',
            'duration', 'appointment_type', 'reason', 'notes',
            'status', 'is_virtual', 'video_link'
        ]
        read_only_fields = ['id', 'appointment_id', 'booked_at']


class UserRegistrationSerializer(serializers.Serializer):
    """
    Serializer for user registration via API
    """
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    role = serializers.ChoiceField(choices=['patient', 'doctor'])
    phone = serializers.CharField(max_length=20, required=False)

    def create(self, validated_data):
        phone = validated_data.pop('phone', '')
        role = validated_data.pop('role')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        UserProfile.objects.create(user=user, role=role, phone=phone)

        return user
```

---

### File: `api/views.py`

```python
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from detection.models import Prediction, Patient, XRayImage
from appointments.models import Appointment
from .serializers import (
    PredictionSerializer, PatientSerializer, AppointmentSerializer,
    UserRegistrationSerializer, PredictionCreateSerializer
)
from .permissions import IsDoctorOrAdmin, IsPatientOwner


class PredictionViewSet(viewsets.ModelViewSet):
    """
    API endpoints for predictions
    """
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Patients see only their own predictions
        if user.profile.is_patient() and hasattr(user, 'patient'):
            return Prediction.objects.filter(xray__patient=user.patient)

        # Doctors and admins see all
        return Prediction.objects.all()

    @action(detail=False, methods=['post'])
    def upload(self, request):
        """
        Upload X-ray image and get prediction
        """
        serializer = PredictionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Process similar to web view
        # Upload image, run prediction, return result
        # Implementation here...

        return Response({'message': 'Prediction created'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def explain(self, request, pk=None):
        """
        Get explainability data for prediction
        """
        prediction = self.get_object()

        return Response({
            'gradcam_heatmap': prediction.gradcam_heatmap.url if prediction.gradcam_heatmap else None,
            'large_branch_attention': prediction.large_branch_attention.url if prediction.large_branch_attention else None,
            'small_branch_attention': prediction.small_branch_attention.url if prediction.small_branch_attention else None,
        })

    @action(detail=True, methods=['patch'], permission_classes=[IsDoctorOrAdmin])
    def validate(self, request, pk=None):
        """
        Validate prediction (doctor only)
        """
        prediction = self.get_object()
        doctor_notes = request.data.get('doctor_notes', '')

        prediction.mark_as_validated(request.user, doctor_notes)

        return Response({'message': 'Prediction validated successfully'})


class PatientViewSet(viewsets.ModelViewSet):
    """
    API endpoints for patients
    """
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Patients see only their own profile
        if user.profile.is_patient():
            return Patient.objects.filter(user=user)

        # Doctors and admins see all
        return Patient.objects.all()

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        """
        Get or update own patient profile
        """
        if not hasattr(request.user, 'patient'):
            return Response(
                {'error': 'Patient profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.method == 'GET':
            serializer = self.get_serializer(request.user.patient)
            return Response(serializer.data)

        elif request.method == 'PATCH':
            serializer = self.get_serializer(
                request.user.patient,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    API endpoints for appointments
    """
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.profile.is_patient() and hasattr(user, 'patient'):
            return Appointment.objects.filter(patient=user.patient)
        elif user.profile.is_doctor():
            return Appointment.objects.filter(doctor=user)

        return Appointment.objects.all()

    @action(detail=False, methods=['get'])
    def available_slots(self, request):
        """
        Get available appointment slots
        """
        from appointments.services import AppointmentScheduler
        from datetime import datetime

        doctor_id = request.query_params.get('doctor_id')
        date_str = request.query_params.get('date')

        if not doctor_id or not date_str:
            return Response(
                {'error': 'doctor_id and date parameters required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from django.contrib.auth.models import User
            doctor = User.objects.get(id=doctor_id)
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except (User.DoesNotExist, ValueError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        slots = AppointmentScheduler.get_available_slots(doctor, date)

        return Response({'available_slots': slots})


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register new user via API
    """
    serializer = UserRegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)

    return Response({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        },
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Login and get JWT tokens
    """
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user is None:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    refresh = RefreshToken.for_user(user)

    return Response({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.profile.role if hasattr(user, 'profile') else None,
        },
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    })
```

---

### File: `api/permissions.py`

```python
from rest_framework import permissions


class IsDoctorOrAdmin(permissions.BasePermission):
    """
    Permission check for doctor or admin role
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if not hasattr(request.user, 'profile'):
            return False

        return request.user.profile.is_doctor() or request.user.profile.is_admin()


class IsPatientOwner(permissions.BasePermission):
    """
    Permission check for patient accessing their own data
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        # Check if user is the owner
        if hasattr(obj, 'patient'):
            return obj.patient.user == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user

        return False
```

---

### File: `api/urls.py`

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'predictions', views.PredictionViewSet, basename='prediction')
router.register(r'patients', views.PatientViewSet, basename='patient')
router.register(r'appointments', views.AppointmentViewSet, basename='appointment')

app_name = 'api'

urlpatterns = [
    # Auth endpoints
    path('auth/register/', views.register_user, name='register'),
    path('auth/login/', views.login_user, name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Router URLs
    path('', include(router.urls)),
]
```

---

## Configuration

### File: `config/settings.py`

```python
INSTALLED_APPS = [
    # ... existing apps ...
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_yasg',  # Swagger documentation
    'corsheaders',  # CORS support
    'api',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Add at top
    # ... existing middleware ...
]

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    }
}

# JWT settings
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React app
    "http://localhost:8080",  # Vue app
]

# Or allow all origins in development (NOT for production!)
# CORS_ALLOW_ALL_ORIGINS = True
```

---

### File: `config/urls.py`

```python
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger documentation schema
schema_view = get_schema_view(
   openapi.Info(
      title="COVID-19 Detection API",
      default_version='v1',
      description="RESTful API for COVID-19 Detection System",
      terms_of_service="https://www.example.com/policies/terms/",
      contact=openapi.Contact(email="contact@example.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # ... existing patterns ...

    # API
    path('api/v1/', include('api.urls')),

    # Swagger documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
```

---

## Dependencies

```
# Add to requirements.txt
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.0
drf-yasg==1.21.7
django-cors-headers==4.3.0
django-filter==23.5
```

---

## API Documentation

Access Swagger documentation at: `http://localhost:8000/api/docs/`

---

## Example API Usage

### Authentication

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"patient1","password":"secure123","email":"patient@example.com","first_name":"John","last_name":"Doe","role":"patient"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"patient1","password":"secure123"}'

# Response: {"tokens": {"access": "...", "refresh": "..."}}
```

### Get Predictions

```bash
curl -X GET http://localhost:8000/api/v1/predictions/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Upload X-ray

```bash
curl -X POST http://localhost:8000/api/v1/predictions/upload/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "image=@xray.jpg" \
  -F "notes=Patient experiencing symptoms"
```

---

## Success Criteria

- ✅ JWT authentication works securely
- ✅ All major entities have CRUD endpoints
- ✅ API documentation is auto-generated and accessible
- ✅ Rate limiting prevents abuse
- ✅ CORS configured for mobile/web clients
- ✅ Pagination handles large datasets
- ✅ Proper permission checks for role-based access
