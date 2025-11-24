# detection/models.py
"""
COVID-19 Detection System - Database Models
TAR UMT Bachelor of Data Science FYP
Author: Tan Ming Kai (24PMR12003)
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class UserProfile(models.Model):
    """
    Extended user information with role-based access control
    Roles: admin, staff, patient
    """

    ROLE_CHOICES = [
        ("admin", "Administrator"),
        ("staff", "Staff"),
        ("patient", "Patient"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        help_text="Linked Django user account",
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="patient",
        help_text="User role for access control",
    )
    phone = models.CharField(
        max_length=15, blank=True, help_text="Contact phone number"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    def is_admin(self):
        return self.role == "admin"

    def is_staff(self):
        return self.role == "staff"

    def is_patient(self):
        return self.role == "patient"


class Patient(models.Model):
    """
    Patient medical information and demographics
    """

    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="patient_info",
        help_text="Linked user account",
    )
    age = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(120)],
        help_text="Patient age in years",
    )
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, help_text="Patient gender"
    )
    date_of_birth = models.DateField(null=True, blank=True)

    # Medical information
    medical_history = models.TextField(
        blank=True, help_text="Previous medical conditions, allergies, chronic diseases"
    )
    current_medications = models.TextField(
        blank=True, help_text="Current medications and dosages"
    )

    # Contact information
    emergency_contact = models.CharField(
        max_length=100, blank=True, help_text="Emergency contact name and number"
    )
    address = models.TextField(blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Patient"
        verbose_name_plural = "Patients"
        ordering = ["user__last_name", "user__first_name"]

    def __str__(self):
        full_name = self.user.get_full_name()
        if full_name:
            return f"{full_name} - {self.age}yr {self.get_gender_display()}"
        return f"{self.user.username} - {self.age}yr {self.get_gender_display()}"

    def get_total_xrays(self):
        """Count total X-rays uploaded for this patient"""
        return self.xrays.count()

    def get_covid_positive_count(self):
        """Count COVID-19 positive diagnoses"""
        return self.xrays.filter(predictions__final_diagnosis="COVID").count()


class XRayImage(models.Model):
    """
    Uploaded chest X-ray images with preprocessing
    """

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="xrays",
        help_text="Patient this X-ray belongs to",
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_xrays",
        help_text="Doctor/staff who uploaded the image",
    )

    # Images
    original_image = models.ImageField(
        upload_to="xrays/original/%Y/%m/%d/", help_text="Original uploaded X-ray image"
    )
    processed_image = models.ImageField(
        upload_to="xrays/processed/%Y/%m/%d/",
        null=True,
        blank=True,
        help_text="CLAHE-enhanced image for AI analysis",
    )

    # Metadata
    upload_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, help_text="Clinical notes or observations")

    # Image properties (auto-populated)
    image_width = models.IntegerField(null=True, blank=True)
    image_height = models.IntegerField(null=True, blank=True)
    file_size = models.IntegerField(
        null=True, blank=True, help_text="File size in bytes"
    )

    class Meta:
        verbose_name = "X-Ray Image"
        verbose_name_plural = "X-Ray Images"
        ordering = ["-upload_date"]

    def __str__(self):
        return f"X-ray for {self.patient.user.username} - {self.upload_date.strftime('%Y-%m-%d %H:%M')}"

    def save(self, *args, **kwargs):
        """Auto-populate image properties on save"""
        if self.original_image:
            from PIL import Image

            img = Image.open(self.original_image)
            self.image_width, self.image_height = img.size
            self.file_size = self.original_image.size
        super().save(*args, **kwargs)


class Prediction(models.Model):
    """
    🌟 SPOTLIGHT 1: Multi-Model Predictions
    Stores predictions from all 6 AI models for comparison
    """

    CLASS_CHOICES = [
        ("COVID", "COVID-19"),
        ("Normal", "Normal"),
        ("Viral Pneumonia", "Viral Pneumonia"),
        ("Lung Opacity", "Lung Opacity"),
    ]

    xray = models.ForeignKey(
        XRayImage,
        on_delete=models.CASCADE,
        related_name="predictions",
        help_text="X-ray image being analyzed",
    )

    # ===== CrossViT Predictions (YOUR MODEL) =====
    crossvit_prediction = models.CharField(
        max_length=50, help_text="CrossViT model prediction"
    )
    crossvit_confidence = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="CrossViT confidence percentage",
    )

    # ===== ResNet-50 Predictions (Baseline 1) =====
    resnet50_prediction = models.CharField(max_length=50)
    resnet50_confidence = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # ===== DenseNet-121 Predictions (Baseline 2) =====
    densenet121_prediction = models.CharField(max_length=50)
    densenet121_confidence = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # ===== EfficientNet-B0 Predictions (Baseline 3) =====
    efficientnet_prediction = models.CharField(max_length=50)
    efficientnet_confidence = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # ===== ViT-Base Predictions (Baseline 4) =====
    vit_prediction = models.CharField(max_length=50)
    vit_confidence = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # ===== Swin-Tiny Predictions (Baseline 5) =====
    swin_prediction = models.CharField(max_length=50)
    swin_confidence = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # ===== Final Diagnosis (Consensus) =====
    final_diagnosis = models.CharField(
        max_length=50, choices=CLASS_CHOICES, help_text="Final consensus diagnosis"
    )
    consensus_confidence = models.FloatField(
        help_text="Confidence of final diagnosis (average or weighted)"
    )

    # ===== 🌟 SPOTLIGHT 2: Explainability =====
    gradcam_heatmap = models.ImageField(
        upload_to="heatmaps/%Y/%m/%d/",
        null=True,
        blank=True,
        help_text="Grad-CAM visualization showing important regions",
    )
    large_branch_attention = models.ImageField(
        upload_to="attention/large/%Y/%m/%d/",
        null=True,
        blank=True,
        help_text="CrossViT large branch attention map",
    )
    small_branch_attention = models.ImageField(
        upload_to="attention/small/%Y/%m/%d/",
        null=True,
        blank=True,
        help_text="CrossViT small branch attention map",
    )

    # ===== Performance Metrics =====
    inference_time = models.FloatField(
        help_text="Total inference time for all models (seconds)"
    )

    # ===== Review and Validation =====
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_predictions",
        help_text="Doctor who reviewed this prediction",
    )
    doctor_notes = models.TextField(
        blank=True, help_text="Doctor's clinical assessment and notes"
    )
    is_validated = models.BooleanField(
        default=False, help_text="Has this prediction been validated by a doctor?"
    )
    validated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Prediction"
        verbose_name_plural = "Predictions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["final_diagnosis"]),
        ]

    def __str__(self):
        patient_name = self.xray.patient.user.username
        date_str = self.created_at.strftime("%Y-%m-%d %H:%M")
        return f"{self.final_diagnosis} - {patient_name} - {date_str}"

    def get_best_model(self):
        """
        Return the model with highest confidence
        Returns: tuple (model_name, confidence)
        """
        models = [
            ("CrossViT", self.crossvit_confidence),
            ("ResNet-50", self.resnet50_confidence),
            ("DenseNet-121", self.densenet121_confidence),
            ("EfficientNet-B0", self.efficientnet_confidence),
            ("ViT-Base", self.vit_confidence),
            ("Swin-Tiny", self.swin_confidence),
        ]
        return max(models, key=lambda x: x[1])

    def get_model_agreement(self):
        """
        Calculate how many models agree on the diagnosis
        Returns: int (number of models agreeing with final diagnosis)
        """
        predictions = [
            self.crossvit_prediction,
            self.resnet50_prediction,
            self.densenet121_prediction,
            self.efficientnet_prediction,
            self.vit_prediction,
            self.swin_prediction,
        ]
        return predictions.count(self.final_diagnosis)

    def get_all_predictions(self):
        """
        Get all model predictions as a list of dictionaries
        Returns: list of {'model': str, 'prediction': str, 'confidence': float}
        """
        return [
            {
                "model": "CrossViT",
                "prediction": self.crossvit_prediction,
                "confidence": self.crossvit_confidence,
            },
            {
                "model": "ResNet-50",
                "prediction": self.resnet50_prediction,
                "confidence": self.resnet50_confidence,
            },
            {
                "model": "DenseNet-121",
                "prediction": self.densenet121_prediction,
                "confidence": self.densenet121_confidence,
            },
            {
                "model": "EfficientNet-B0",
                "prediction": self.efficientnet_prediction,
                "confidence": self.efficientnet_confidence,
            },
            {
                "model": "ViT-Base",
                "prediction": self.vit_prediction,
                "confidence": self.vit_confidence,
            },
            {
                "model": "Swin-Tiny",
                "prediction": self.swin_prediction,
                "confidence": self.swin_confidence,
            },
        ]

    def mark_as_validated(self, doctor_user):
        """Mark prediction as validated by a doctor"""
        self.is_validated = True
        self.validated_at = timezone.now()
        self.reviewed_by = doctor_user
        self.save()


# Signal to auto-create UserProfile when User is created
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create UserProfile when a new User is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile whenever User is saved"""
    if hasattr(instance, "profile"):
        instance.profile.save()
