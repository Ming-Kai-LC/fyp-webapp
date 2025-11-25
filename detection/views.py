# detection/views.py
"""
COVID-19 Detection System - Main Views
Handles all user interactions and ML predictions
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, FormView
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.utils import timezone

from common.mixins import (
    PageTitleMixin,
    ProfileContextMixin,
    MultiFormMixin,
    SuccessMessageMixin,
)

from .models import XRayImage, Prediction, Patient, UserProfile
from .forms import (
    XRayUploadForm,
    UserRegistrationForm,
    NormalizedAuthenticationForm,
    PatientProfileForm,
    UserBasicInfoForm,
    ProfilePictureForm,
    DoctorNotesForm,
)
from .services import (
    PredictionService,
    StatisticsService,
    MLInferenceError,
    ProfileService,
    ProfileServiceError,
)
from .decorators import profile_completion_required
from .constants import RoleChoices, GenderChoices, ValidationLimits
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


class PatientRegistrationView(PageTitleMixin, SuccessMessageMixin, FormView):
    """
    Class-based patient self-registration view.

    Security Policy (user-role-permissions skill):
    - Public registration creates PATIENT accounts ONLY
    - Staff/Admin accounts must be created through admin panel
    - Role is hardcoded to 'patient' - no user input accepted
    - Patient profile automatically created for all registrations

    Follows full-stack-django-patterns skill:
    - Class-based view with mixins for reusability
    - Thin view (business logic in form_valid)
    - Uses PageTitleMixin and SuccessMessageMixin from common.mixins

    Attributes:
        template_name: Path to registration template.
        form_class: The form class for user registration.
        success_url: URL to redirect after successful registration.
        page_title: Title displayed on the page.
        success_message: Message shown after successful registration.
    """

    template_name: str = "accounts/register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("detection:patient_dashboard")
    page_title: str = "Patient Registration"
    success_message: str = "Welcome {username}! Your patient account has been created successfully."

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Redirect authenticated users to dashboard.

        Args:
            request: The HTTP request object.
            *args: Variable positional arguments.
            **kwargs: Variable keyword arguments.

        Returns:
            HttpResponse: Redirect to dashboard if authenticated, otherwise
                         continues to normal dispatch.
        """
        if request.user.is_authenticated:
            messages.info(request, "You are already logged in.")
            return redirect("detection:patient_dashboard")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: UserRegistrationForm) -> HttpResponse:
        """
        Handle successful form submission.

        Creates user, enforces patient role, creates patient profile,
        and logs user in automatically.

        Args:
            form: The validated registration form.

        Returns:
            HttpResponse: Redirect to success_url.
        """
        # Create user account
        user = form.save()

        # SECURITY: Enforce patient role (defense in depth)
        # Profile is auto-created via signal with role='patient'
        # Explicitly set to 'patient' to prevent any bypass attempts
        profile = user.profile
        profile.role = RoleChoices.PATIENT  # ALWAYS patient for public registration
        profile.save()

        # Create patient medical profile with defaults
        # User can update their profile after login
        Patient.objects.create(
            user=user,
            age=ValidationLimits.MIN_AGE + 18,  # Default age (18), to be updated by user
            gender=GenderChoices.OTHER,  # Default gender, to be updated by user
        )

        # Log user in automatically
        login(self.request, user)

        # Store username for success message (used by get_success_message)
        self._registered_username = user.username

        logger.info(f"New patient registered: {user.username}")

        return super().form_valid(form)

    def get_success_message(self) -> str:
        """
        Return formatted success message with username.

        Overrides SuccessMessageMixin.get_success_message() to format
        the message with the registered user's username.

        Returns:
            str: Formatted welcome message.
        """
        return self.success_message.format(username=self._registered_username)


# Keep function alias for backwards compatibility with existing URL configs
def register(request):
    """
    Function wrapper for PatientRegistrationView.

    Deprecated: Use PatientRegistrationView.as_view() in urls.py instead.
    Kept for backwards compatibility.
    """
    return PatientRegistrationView.as_view()(request)


class CustomLoginView(LoginView):
    """
    Custom login view with "Remember me" functionality and input normalization.

    Features:
        - Username normalization (strip whitespace, lowercase)
        - Remember me functionality (14 days session)

    Session behavior:
        - If "remember_me" is checked: Session expires after 14 days (2 weeks)
        - If unchecked: Session expires when browser closes (default behavior)

    Follows dual-layer-validation skill:
        - Server-side: NormalizedAuthenticationForm normalizes username
        - Client-side: JavaScript normalizes on blur (in template)
    """

    template_name = 'registration/login.html'
    form_class = NormalizedAuthenticationForm

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
@profile_completion_required(allow_partial=True)
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
@profile_completion_required(allow_partial=True)
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
def user_profile(request):
    """
    Comprehensive user profile view for all roles (admin, staff, patient).

    Handles basic info (name, email, phone) and patient-specific medical data.
    Uses ProfileService for business logic (three-tier architecture).

    Forms:
        - basic_info: Name, email, phone (all roles)
        - patient_info: Age, gender, DOB, medical history (patients only)
        - profile_picture: Profile image upload (all roles)
    """
    user = request.user
    profile = user.profile

    # Initialize forms
    basic_form = None
    patient_form = None
    picture_form = None

    # Get or create patient info for patients
    patient = None
    if profile.is_patient():
        patient, created = Patient.objects.get_or_create(
            user=user,
            defaults={"age": 18, "gender": GenderChoices.OTHER},
        )

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "basic_info":
            basic_form = UserBasicInfoForm(
                request.POST, instance=profile, user=user
            )
            if basic_form.is_valid():
                try:
                    basic_form.save()
                    messages.success(request, "Profile updated successfully!")
                    return redirect("detection:user_profile")
                except Exception as e:
                    logger.error(f"Error saving basic info: {e}")
                    messages.error(request, "Failed to save profile. Please try again.")

        elif form_type == "patient_info" and profile.is_patient():
            patient_form = PatientProfileForm(request.POST, instance=patient)
            if patient_form.is_valid():
                try:
                    patient_form.save()
                    messages.success(request, "Medical information updated successfully!")
                    return redirect("detection:user_profile")
                except Exception as e:
                    logger.error(f"Error saving patient info: {e}")
                    messages.error(request, "Failed to save medical information. Please try again.")

        elif form_type == "profile_picture":
            picture_form = ProfilePictureForm(
                request.POST, request.FILES, instance=profile
            )
            if picture_form.is_valid():
                try:
                    picture_form.save()
                    messages.success(request, "Profile picture updated successfully!")
                    return redirect("detection:user_profile")
                except Exception as e:
                    logger.error(f"Error saving profile picture: {e}")
                    messages.error(request, "Failed to upload picture. Please try again.")

    # Initialize forms for GET request
    if not basic_form:
        basic_form = UserBasicInfoForm(instance=profile, user=user)

    if not patient_form and profile.is_patient():
        patient_form = PatientProfileForm(instance=patient)

    if not picture_form:
        picture_form = ProfilePictureForm(instance=profile)

    # Get profile context from service (includes completion status)
    profile_context = ProfileService.get_profile_context(user)

    # Build context
    context = {
        "basic_form": basic_form,
        "patient_form": patient_form,
        "picture_form": picture_form,
        **profile_context,  # Includes user, profile, is_patient, is_staff, is_admin, completion
    }

    return render(request, "detection/user_profile.html", context)


# ============================================================================
# CLASS-BASED VIEWS
# ============================================================================


class UserProfileView(
    LoginRequiredMixin,
    PageTitleMixin,
    ProfileContextMixin,
    MultiFormMixin,
    TemplateView,
):
    """
    Class-based view for user profile management.

    Features:
        - Multi-form handling (basic info, patient info, profile picture)
        - Role-based form display (patient-only forms hidden for staff)
        - Profile completion tracking
        - Reusable mixins for common functionality

    Mixins used:
        - LoginRequiredMixin: Requires authentication
        - PageTitleMixin: Adds page_title to context
        - ProfileContextMixin: Adds profile data to context
        - MultiFormMixin: Handles multiple forms

    Usage:
        # In urls.py
        path('profile/', UserProfileView.as_view(), name='user_profile_cbv'),
    """

    template_name = "detection/user_profile.html"
    page_title = "My Profile"
    page_subtitle = "Manage your account settings and information"
    success_url = reverse_lazy("detection:user_profile")
    form_type_field = "form_type"

    # Form classes (dynamically built based on user role)
    form_classes = {
        "basic_info": UserBasicInfoForm,
        "patient_info": PatientProfileForm,
        "profile_picture": ProfilePictureForm,
    }

    def get_form_classes(self):
        """Return form classes based on user role."""
        classes = {
            "basic_info": UserBasicInfoForm,
            "profile_picture": ProfilePictureForm,
        }

        # Only add patient form for patients
        if self.request.user.profile.is_patient():
            classes["patient_info"] = PatientProfileForm

        return classes

    def get_form_kwargs(self, form_name: str):
        """Provide custom kwargs for each form."""
        kwargs = super().get_form_kwargs(form_name)
        user = self.request.user
        profile = user.profile

        if form_name == "basic_info":
            kwargs["instance"] = profile
            kwargs["user"] = user

        elif form_name == "patient_info":
            if profile.is_patient():
                patient, _ = Patient.objects.get_or_create(
                    user=user,
                    defaults={"age": 18, "gender": GenderChoices.OTHER},
                )
                kwargs["instance"] = patient

        elif form_name == "profile_picture":
            kwargs["instance"] = profile

        return kwargs

    def get_context_data(self, **kwargs):
        """Add additional context data."""
        context = super().get_context_data(**kwargs)

        user = self.request.user
        profile = user.profile

        # Add patient data if applicable
        if profile.is_patient():
            try:
                patient = user.patient_info
                context["patient"] = patient
                context["total_xrays"] = patient.get_total_xrays()
                context["covid_positive_count"] = patient.get_covid_positive_count()
            except Patient.DoesNotExist:
                context["patient"] = None
                context["total_xrays"] = 0
                context["covid_positive_count"] = 0

        # Rename form context keys to match template expectations
        if "basic_info_form" in context:
            context["basic_form"] = context.pop("basic_info_form")
        if "patient_info_form" in context:
            context["patient_form"] = context.pop("patient_info_form")
        if "profile_picture_form" in context:
            context["picture_form"] = context.pop("profile_picture_form")

        return context

    def form_valid(self, form_name: str, form) -> HttpResponse:
        """Handle successful form submission."""
        try:
            form.save()
            messages.success(self.request, self._get_success_message(form_name))
        except Exception as e:
            logger.error(f"Error saving {form_name}: {e}")
            messages.error(self.request, f"Failed to save. Please try again.")
            return self.form_invalid(form_name, form)

        return redirect(self.success_url)

    def form_invalid(self, form_name: str, form) -> HttpResponse:
        """Handle invalid form submission."""
        messages.error(self.request, "Please correct the errors below.")
        return self.render_to_response(self.get_context_data())

    def _get_success_message(self, form_name: str) -> str:
        """Get success message based on form type."""
        messages_map = {
            "basic_info": "Profile updated successfully!",
            "patient_info": "Medical information updated successfully!",
            "profile_picture": "Profile picture updated successfully!",
        }
        return messages_map.get(form_name, "Changes saved successfully!")


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
