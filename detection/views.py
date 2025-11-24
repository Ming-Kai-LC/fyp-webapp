# detection/views.py
"""
COVID-19 Detection System - Main Views
Handles all user interactions and ML predictions
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from django.utils import timezone

from .models import XRayImage, Prediction, Patient, UserProfile
from .forms import (
    XRayUploadForm,
    UserRegistrationForm,
    PatientProfileForm,
    DoctorNotesForm,
)
from .services import PredictionService, StatisticsService, MLInferenceError
try:
    # Try to import real ML engine if PyTorch is available
    from .ml_engine import model_ensemble
    from .preprocessing import apply_clahe
    from .explainability import generate_explainability_report
except ImportError:
    # Fall back to stub if PyTorch not installed or model weights missing
    from .ml_engine_stub import model_ensemble
    from .preprocessing_stub import apply_clahe
    from .explainability_stub import generate_explainability_report
from notifications.services import NotificationService

import os
import logging

logger = logging.getLogger(__name__)


def home(request):
    """Landing page"""
    context = {
        "total_predictions": (
            Prediction.objects.count() if request.user.is_authenticated else 0
        ),
        "total_patients": (
            Patient.objects.count() if request.user.is_authenticated else 0
        ),
    }
    return render(request, "home.html", context)


def register(request):
    """
    Patient self-registration for public access.

    Security Policy (user-role-permissions skill):
    - Public registration creates PATIENT accounts ONLY
    - Staff/Admin accounts must be created through admin panel
    - Role is hardcoded to 'patient' - no user input accepted
    - Patient profile automatically created for all registrations
    """
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Create user account
            user = form.save()

            # SECURITY: Enforce patient role (defense in depth)
            # Profile is auto-created via signal with role='patient'
            # Explicitly set to 'patient' to prevent any bypass attempts
            profile = user.profile
            profile.role = "patient"  # ALWAYS patient for public registration
            profile.save()

            # Create patient medical profile with defaults
            # User can update their profile after login
            Patient.objects.create(
                user=user,
                age=18,  # Default age, to be updated by user
                gender="O"  # Default gender, to be updated by user
            )

            # Log user in automatically
            login(request, user)
            messages.success(
                request,
                f"Welcome {user.username}! Your patient account has been created successfully."
            )

            # Redirect to patient dashboard
            return redirect("detection:patient_dashboard")
    else:
        form = UserRegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


class CustomLoginView(LoginView):
    """
    Custom login view with "Remember me" functionality.

    Session behavior:
    - If "remember_me" is checked: Session expires after 14 days (2 weeks)
    - If unchecked: Session expires when browser closes (default behavior)
    """
    template_name = 'registration/login.html'

    def form_valid(self, form):
        """Handle successful login with remember me functionality."""
        remember_me = self.request.POST.get('remember_me')

        # Call parent form_valid to log the user in
        response = super().form_valid(form)

        if remember_me:
            # Remember me is checked - keep session for 14 days
            # 14 days * 24 hours * 60 minutes * 60 seconds = 1209600 seconds
            self.request.session.set_expiry(1209600)
            logger.info(f"User {self.request.user.username} logged in with 'Remember me' (14 days)")
        else:
            # Remember me is NOT checked - session expires on browser close
            self.request.session.set_expiry(0)
            logger.info(f"User {self.request.user.username} logged in without 'Remember me' (browser close)")

        return response


# ============================================================================
# STAFF VIEWS
# ============================================================================


@login_required
def staff_dashboard(request):
    """Staff dashboard with recent predictions and quick stats (Refactored with Service Layer)"""
    if not request.user.profile.is_staff():
        messages.error(request, "Access denied. Staff only.")
        return redirect("home")

    # ✅ NEW: Single service call aggregates all dashboard data
    stats = StatisticsService.get_staff_dashboard_stats(request.user)

    context = {
        "recent_predictions": stats['recent_predictions'],
        "total_predictions": stats['total_predictions'],
        "covid_cases": stats['covid_cases'],
        "normal_cases": stats['normal_cases'],
        "pending_validation": stats['pending_validation'],
    }

    return render(request, "detection/staff_dashboard.html", context)


@login_required
def upload_xray(request):
    """
    🌟 MAIN VIEW: Upload X-ray and run multi-model predictions (Refactored with Service Layer)
    """
    if not request.user.profile.is_staff():
        messages.error(request, "Access denied. Staff only.")
        return redirect("home")

    if request.method == "POST":
        form = XRayUploadForm(request.POST, request.FILES)
        patient_id = request.POST.get("patient_id")

        if form.is_valid():
            try:
                # Get patient
                if patient_id:
                    patient = get_object_or_404(Patient, id=patient_id)
                else:
                    # Use logged-in user as patient if they have patient info
                    if hasattr(request.user, "patient_info"):
                        patient = request.user.patient_info
                    else:
                        messages.error(
                            request,
                            "Please select a patient or create patient profile.",
                        )
                        return render(request, "detection/upload.html", {"form": form})

                # ✅ NEW: Single service call handles entire workflow
                # - Save X-ray image
                # - Apply preprocessing
                # - Run 6 ML models
                # - Save prediction
                # - Send notification
                prediction = PredictionService.create_prediction_from_xray(
                    xray_image_file=request.FILES['original_image'],
                    patient=patient,
                    uploaded_by=request.user,
                    notes=form.cleaned_data.get('notes', '')
                )

                messages.success(
                    request,
                    f'✅ Analysis complete! Diagnosis: {prediction.final_diagnosis} '
                    f'(Confidence: {prediction.consensus_confidence:.1f}%)'
                )

                return redirect("detection:view_results", prediction_id=prediction.id)

            except MLInferenceError as e:
                logger.error(f"ML inference error: {e}")
                messages.error(request, f"ML analysis failed: {str(e)}")
            except Exception as e:
                logger.error(f"❌ Error during prediction: {e}", exc_info=True)
                messages.error(request, f"Error during analysis: {str(e)}")

    else:
        form = XRayUploadForm()

    # Get list of patients for dropdown
    patients = Patient.objects.all().select_related("user")

    context = {"form": form, "patients": patients}

    return render(request, "detection/upload.html", context)


@login_required
def view_results(request, prediction_id):
    """
    🌟 SPOTLIGHT 1: Display multi-model comparison results
    """
    prediction = get_object_or_404(Prediction, id=prediction_id)

    # Check access permissions
    if request.user.profile.is_patient():
        # Patients can only see their own results
        if prediction.xray.patient.user != request.user:
            messages.error(request, "Access denied.")
            return redirect("detection:patient_dashboard")

    # Prepare data for visualization
    model_results = prediction.get_all_predictions()

    # Sort by confidence (highest first)
    model_results_sorted = sorted(
        model_results, key=lambda x: x["confidence"], reverse=True
    )

    # Get best model and agreement
    best_model_name, best_confidence = prediction.get_best_model()
    agreement_count = prediction.get_model_agreement()

    # Check if explainability has been generated
    has_explainability = bool(prediction.gradcam_heatmap)

    context = {
        "prediction": prediction,
        "model_results": model_results_sorted,
        "best_model_name": best_model_name,
        "best_confidence": best_confidence,
        "agreement_count": agreement_count,
        "has_explainability": has_explainability,
    }

    return render(request, "detection/results.html", context)


@login_required
def explain_prediction(request, prediction_id):
    """
    🌟 SPOTLIGHT 2: Generate and display explainability visualizations
    """
    prediction = get_object_or_404(Prediction, id=prediction_id)

    # Check access
    if request.user.profile.is_patient():
        if prediction.xray.patient.user != request.user:
            messages.error(request, "Access denied.")
            return redirect("detection:patient_dashboard")

    # Generate explainability if not already generated
    if not prediction.gradcam_heatmap:
        try:
            logger.info(
                f"🔍 Generating explainability for prediction {prediction_id}..."
            )

            # Load CrossViT model
            if model_ensemble:
                model_ensemble._load_model("crossvit")

                # Generate explainability report
                explainability_paths = generate_explainability_report(
                    model=model_ensemble.current_model,
                    device=model_ensemble.device,
                    image_path=prediction.xray.processed_image.path,
                    prediction_result={
                        "prediction": prediction.crossvit_prediction,
                        "confidence": prediction.crossvit_confidence,
                    },
                    model_name="crossvit",
                )

                # Update prediction with explainability paths
                from django.conf import settings

                if explainability_paths.get("gradcam_path"):
                    prediction.gradcam_heatmap = os.path.relpath(
                        explainability_paths["gradcam_path"], settings.MEDIA_ROOT
                    )
                if explainability_paths.get("large_branch_path"):
                    prediction.large_branch_attention = os.path.relpath(
                        explainability_paths["large_branch_path"], settings.MEDIA_ROOT
                    )
                if explainability_paths.get("small_branch_path"):
                    prediction.small_branch_attention = os.path.relpath(
                        explainability_paths["small_branch_path"], settings.MEDIA_ROOT
                    )

                prediction.save()
                logger.info("✅ Explainability generated successfully")
                messages.success(request, "Explainability visualization generated!")
            else:
                messages.error(request, "ML Engine not available")

        except Exception as e:
            logger.error(f"❌ Explainability generation error: {e}", exc_info=True)
            messages.error(request, f"Error generating explainability: {str(e)}")

    context = {
        "prediction": prediction,
    }

    return render(request, "detection/explain.html", context)


@login_required
def prediction_history(request):
    """View all past predictions"""
    if request.user.profile.is_staff():
        # Staff see all predictions
        predictions = (
            Prediction.objects.all()
            .select_related("xray__patient__user", "reviewed_by")
            .order_by("-created_at")
        )
    else:
        # Patients see only their own
        predictions = (
            Prediction.objects.filter(xray__patient__user=request.user)
            .select_related("reviewed_by")
            .order_by("-created_at")
        )

    # Add filters
    diagnosis_filter = request.GET.get("diagnosis")
    if diagnosis_filter:
        predictions = predictions.filter(final_diagnosis=diagnosis_filter)

    context = {"predictions": predictions, "diagnosis_filter": diagnosis_filter}

    return render(request, "detection/history.html", context)


@login_required
@require_POST
def add_doctor_notes(request, prediction_id):
    """Add doctor notes to a prediction"""
    if not request.user.profile.is_staff():
        return JsonResponse({"error": "Access denied"}, status=403)

    prediction = get_object_or_404(Prediction, id=prediction_id)
    form = DoctorNotesForm(request.POST)

    if form.is_valid():
        prediction.doctor_notes = form.cleaned_data["notes"]

        if form.cleaned_data.get("is_validated"):
            prediction.mark_as_validated(request.user)

        prediction.save()
        messages.success(request, "Notes saved successfully")
        return redirect("detection:view_results", prediction_id=prediction_id)

    messages.error(request, "Invalid form data")
    return redirect("detection:view_results", prediction_id=prediction_id)


# ============================================================================
# PATIENT VIEWS
# ============================================================================


@login_required
def patient_dashboard(request):
    """Patient dashboard showing their own results"""
    if not request.user.profile.is_patient():
        messages.error(request, "Access denied. Patients only.")
        return redirect("home")

    if not hasattr(request.user, "patient_info"):
        messages.warning(request, "Please complete your patient profile")
        return redirect("detection:patient_profile")

    patient = request.user.patient_info

    # Get patient's predictions
    my_predictions = (
        Prediction.objects.filter(xray__patient=patient)
        .select_related("xray", "reviewed_by")
        .order_by("-created_at")[:10]
    )

    # Statistics
    total_xrays = patient.get_total_xrays()
    covid_positive = patient.get_covid_positive_count()

    context = {
        "patient": patient,
        "my_predictions": my_predictions,
        "total_xrays": total_xrays,
        "covid_positive": covid_positive,
    }

    return render(request, "detection/patient_dashboard.html", context)


@login_required
def patient_profile(request):
    """View/edit patient profile"""
    if not request.user.profile.is_patient():
        messages.error(request, "Access denied")
        return redirect("home")

    # Get or create patient info
    patient, created = Patient.objects.get_or_create(
        user=request.user, defaults={"age": 18, "gender": "O"}
    )

    if request.method == "POST":
        form = PatientProfileForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully")
            return redirect("detection:patient_dashboard")
    else:
        form = PatientProfileForm(instance=patient)

    return render(request, "detection/patient_profile.html", {"form": form})


# ============================================================================
# API ENDPOINTS (Optional - for AJAX calls)
# ============================================================================


@login_required
def api_model_info(request):
    """Get information about all models (for displaying in UI)"""
    if model_ensemble:
        info = model_ensemble.get_all_models_info()
        return JsonResponse(info)
    return JsonResponse({"error": "Model ensemble not available"}, status=500)
