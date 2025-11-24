"""
RESTful API Module - Views

ViewSets and API endpoints for the REST API.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, PermissionDenied
from detection.models import Prediction, Patient, XRayImage
from detection.services import PredictionService, MLInferenceError
from appointments.models import Appointment
from .serializers import (
    PredictionSerializer, PatientSerializer, AppointmentSerializer,
    UserRegistrationSerializer, PredictionCreateSerializer
)
from .permissions import IsStaffOrAdmin, IsPatientOwner
import logging

logger = logging.getLogger(__name__)


class PredictionViewSet(viewsets.ModelViewSet):
    """
    API endpoints for predictions

    list: Get all predictions (filtered by user role)
    retrieve: Get a specific prediction
    upload: Upload X-ray image and get prediction
    explain: Get explainability data (Grad-CAM, attention maps)
    validate: Validate prediction (staff only)
    """
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter predictions based on user role (Refactored with Service Layer)

        Uses PredictionService to ensure consistent permission logic
        across web views and API endpoints.
        """
        # ✅ NEW: Use service for consistent permission filtering
        return PredictionService.get_predictions_for_user(self.request.user)

    @action(detail=False, methods=['post'], permission_classes=[IsStaffOrAdmin])
    def upload(self, request):
        """
        Upload X-ray image and get prediction (Implemented with Service Layer)

        Handles complete prediction workflow:
        1. Validate inputs
        2. Save X-ray image
        3. Apply preprocessing (CLAHE)
        4. Run 6 ML models
        5. Calculate consensus diagnosis
        6. Save prediction
        7. Send notification

        Request body:
        - image: X-ray image file (required)
        - patient_id: Patient ID (required)
        - notes: Clinical notes (optional)

        Returns:
        - Prediction object with all model results
        """
        serializer = PredictionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        patient_id = serializer.validated_data.get('patient_id')
        image_file = request.FILES.get('image')
        notes = serializer.validated_data.get('notes', '')

        if not image_file:
            return Response(
                {'error': 'Image file is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get patient
            patient = Patient.objects.get(id=patient_id)

            # ✅ NEW: Use PredictionService for complete workflow
            # Same service used by web views - ensures consistency
            prediction = PredictionService.create_prediction_from_xray(
                xray_image_file=image_file,
                patient=patient,
                uploaded_by=request.user,
                notes=notes
            )

            logger.info(
                f"API prediction created: ID={prediction.id}, "
                f"Diagnosis={prediction.final_diagnosis}, "
                f"User={request.user.username}"
            )

            # Return serialized prediction
            return Response(
                {
                    'message': 'Prediction completed successfully',
                    'prediction': PredictionSerializer(prediction).data
                },
                status=status.HTTP_201_CREATED
            )

        except Patient.DoesNotExist:
            return Response(
                {'error': f'Patient with ID {patient_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionDenied as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except MLInferenceError as e:
            logger.error(f"ML inference error in API: {e}")
            return Response(
                {'error': f'ML analysis failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error in API upload: {e}", exc_info=True)
            return Response(
                {'error': 'An unexpected error occurred during prediction'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def explain(self, request, pk=None):
        """
        Get explainability data for prediction

        Returns Grad-CAM heatmap and attention maps for CrossViT model.
        """
        prediction = self.get_object()

        return Response({
            'gradcam_heatmap': prediction.gradcam_heatmap.url if prediction.gradcam_heatmap else None,
            'large_branch_attention': prediction.large_branch_attention.url if prediction.large_branch_attention else None,
            'small_branch_attention': prediction.small_branch_attention.url if prediction.small_branch_attention else None,
        })

    @action(detail=True, methods=['patch'], permission_classes=[IsStaffOrAdmin])
    def validate(self, request, pk=None):
        """
        Validate prediction (staff only)

        Marks the prediction as validated by staff.
        """
        prediction = self.get_object()
        doctor_notes = request.data.get('doctor_notes', '')

        # Update doctor notes if provided
        if doctor_notes:
            prediction.doctor_notes = doctor_notes

        # Mark as validated
        prediction.mark_as_validated(request.user)

        return Response({
            'message': 'Prediction validated successfully',
            'prediction': PredictionSerializer(prediction).data
        })


class PatientViewSet(viewsets.ModelViewSet):
    """
    API endpoints for patients

    list: Get all patients (staff/admin only)
    retrieve: Get patient details
    me: Get/update own patient profile
    """
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter patients based on user role"""
        user = self.request.user

        # Patients see only their own profile
        if hasattr(user, 'profile') and user.profile.is_patient():
            if hasattr(user, 'patient_info'):
                return Patient.objects.filter(user=user)
            return Patient.objects.none()

        # Staff and admins see all
        return Patient.objects.all()

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        """
        Get or update own patient profile

        GET: Returns the current user's patient profile
        PATCH: Updates the current user's patient profile
        """
        if not hasattr(request.user, 'patient_info'):
            return Response(
                {'error': 'Patient profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.method == 'GET':
            serializer = self.get_serializer(request.user.patient_info)
            return Response(serializer.data)

        elif request.method == 'PATCH':
            serializer = self.get_serializer(
                request.user.patient_info,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def predictions(self, request, pk=None):
        """
        Get all predictions for a specific patient
        """
        patient = self.get_object()
        predictions = Prediction.objects.filter(xray__patient=patient)
        serializer = PredictionSerializer(predictions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def appointments(self, request, pk=None):
        """
        Get all appointments for a specific patient
        """
        patient = self.get_object()
        appointments = Appointment.objects.filter(patient=patient)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    API endpoints for appointments

    list: Get all appointments (filtered by user role)
    create: Book new appointment
    retrieve: Get appointment details
    update: Update appointment
    destroy: Cancel appointment
    available_slots: Get available time slots for booking
    """
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter appointments based on user role"""
        user = self.request.user

        if hasattr(user, 'profile'):
            if user.profile.is_patient() and hasattr(user, 'patient_info'):
                return Appointment.objects.filter(patient=user.patient_info)
            elif user.profile.is_staff():
                return Appointment.objects.filter(doctor=user)

        return Appointment.objects.all()

    @action(detail=False, methods=['get'])
    def available_slots(self, request):
        """
        Get available appointment slots

        Query parameters:
        - doctor_id: ID of the doctor
        - date: Date in YYYY-MM-DD format
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
            doctor = User.objects.get(id=doctor_id)
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except (User.DoesNotExist, ValueError) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        slots = AppointmentScheduler.get_available_slots(doctor, date)

        return Response({'available_slots': slots})


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register new user via API

    Creates a new user account with UserProfile.
    Returns user data and JWT tokens.
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
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.profile.role if hasattr(user, 'profile') else None,
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

    Authenticates user credentials and returns JWT tokens.
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

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
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.profile.role if hasattr(user, 'profile') else None,
        },
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    Logout user by blacklisting refresh token
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logout successful'})
        return Response(
            {'error': 'Refresh token required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
