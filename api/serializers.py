"""
RESTful API Module - Serializers

Serializers for converting Django models to JSON and vice versa.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from detection.models import UserProfile, Patient, XRayImage, Prediction
from appointments.models import Appointment


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model
    """
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['user', 'role', 'phone', 'created_at']


class PatientSerializer(serializers.ModelSerializer):
    """
    Serializer for Patient model
    """
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
    """
    Serializer for XRayImage model
    """
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
    """
    Serializer for Prediction model
    """
    xray = XRayImageSerializer(read_only=True)
    best_model = serializers.SerializerMethodField()
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

    def get_best_model(self, obj):
        """Get the best model name and confidence"""
        model_name, confidence = obj.get_best_model()
        return {'model': model_name, 'confidence': confidence}


class PredictionCreateSerializer(serializers.Serializer):
    """
    Serializer for uploading X-ray and creating prediction
    """
    image = serializers.ImageField()
    notes = serializers.CharField(required=False, allow_blank=True)


class AppointmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Appointment model
    """
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

    def validate_username(self, value):
        """Check if username already exists"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        """Check if email already exists"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def create(self, validated_data):
        """Create new user with profile"""
        phone = validated_data.pop('phone', '')
        role = validated_data.pop('role')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        # Update the auto-created profile with role and phone
        user.profile.role = role
        user.profile.phone = phone
        user.profile.save()

        return user
