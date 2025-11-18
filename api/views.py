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

    list: Get all predictions (filtered by user role)
    retrieve: Get a specific prediction
    upload: Upload X-ray image and get prediction
    explain: Get explainability data (Grad-CAM, attention maps)
    validate: Validate prediction (doctor only)
    """
    queryset = Prediction.objects.all()
    serializer_class = PredictionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter predictions based on user role"""
        user = self.request.user

        # Patients see only their own predictions
        if hasattr(user, 'profile') and user.profile.is_patient():
            if hasattr(user, 'patient_info'):
                return Prediction.objects.filter(xray__patient=user.patient_info)
            return Prediction.objects.none()

        # Doctors and admins see all
        return Prediction.objects.all()

    @action(detail=False, methods=['post'])
    def upload(self, request):
        """
        Upload X-ray image and get prediction

        This endpoint handles image upload and runs the prediction pipeline.
        The actual prediction logic should be implemented using the detection module.
        """
        serializer = PredictionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # TODO: Implement prediction pipeline integration
        # This would involve:
        # 1. Creating XRayImage instance
        # 2. Running image preprocessing
        # 3. Running all 6 AI models
        # 4. Creating Prediction instance with results
        # 5. Generating explainability visualizations

        return Response(
            {'message': 'Prediction upload endpoint - implementation pending'},
            status=status.HTTP_501_NOT_IMPLEMENTED
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

    @action(detail=True, methods=['patch'], permission_classes=[IsDoctorOrAdmin])
    def validate(self, request, pk=None):
        """
        Validate prediction (doctor only)

        Marks the prediction as validated by a doctor.
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

    list: Get all patients (doctor/admin only)
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

        # Doctors and admins see all
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
            elif user.profile.is_doctor():
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
