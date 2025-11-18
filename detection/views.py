# detection/views.py
"""
COVID-19 Detection System - Main Views
Handles all user interactions and ML predictions
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from django.utils import timezone

from .models import XRayImage, Prediction, Patient, UserProfile, BatchUploadJob, BatchUploadImage
from .forms import (
    XRayUploadForm,
    UserRegistrationForm,
    PatientProfileForm,
    DoctorNotesForm,
    BatchXRayUploadForm,
)
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
    """User registration"""
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Set user profile role
            profile = user.profile
            profile.role = form.cleaned_data.get("role")
            profile.save()

            # If patient, create patient profile
            if profile.role == "patient":
                Patient.objects.create(
                    user=user, age=18, gender="O"  # Default, can be updated later
                )

            login(request, user)
            messages.success(
                request, f"Welcome {user.username}! Your account has been created."
            )

            # Redirect based on role
            if profile.role == "doctor":
                return redirect("detection:doctor_dashboard")
            elif profile.role == "patient":
                return redirect("detection:patient_dashboard")
            else:
                return redirect("home")
    else:
        form = UserRegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


# ============================================================================
# DOCTOR VIEWS
# ============================================================================


@login_required
def doctor_dashboard(request):
    """Doctor dashboard with recent predictions and quick stats"""
    if not request.user.profile.is_doctor():
        messages.error(request, "Access denied. Doctors only.")
        return redirect("home")

    recent_predictions = (
        Prediction.objects.all()
        .select_related("xray__patient__user")
        .order_by("-created_at")[:10]
    )

    # Statistics
    total_predictions = Prediction.objects.count()
    covid_cases = Prediction.objects.filter(final_diagnosis="COVID").count()
    normal_cases = Prediction.objects.filter(final_diagnosis="Normal").count()
    pending_validation = Prediction.objects.filter(is_validated=False).count()

    context = {
        "recent_predictions": recent_predictions,
        "total_predictions": total_predictions,
        "covid_cases": covid_cases,
        "normal_cases": normal_cases,
        "pending_validation": pending_validation,
    }

    return render(request, "dashboards/doctor_dashboard.html", context)


@login_required
def upload_xray(request):
    """
    🌟 MAIN VIEW: Upload X-ray and run multi-model predictions
    """
    if not request.user.profile.is_doctor():
        messages.error(request, "Access denied. Doctors only.")
        return redirect("home")

    if request.method == "POST":
        form = XRayUploadForm(request.POST, request.FILES)

        # Get patient ID from form or default to first patient
        patient_id = request.POST.get("patient_id")

        if form.is_valid():
            try:
                # Get or create patient
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

                # Save uploaded image
                xray = form.save(commit=False)
                xray.patient = patient
                xray.uploaded_by = request.user
                xray.save()

                logger.info(f"✅ X-ray uploaded: {xray.original_image.path}")

                # Apply CLAHE preprocessing
                logger.info("🔧 Applying CLAHE preprocessing...")
                processed_path = apply_clahe(xray.original_image.path)

                # Update xray with processed image path
                # Convert absolute path to relative media path
                from django.conf import settings

                relative_path = os.path.relpath(processed_path, settings.MEDIA_ROOT)
                xray.processed_image = relative_path
                xray.save()

                # 🔥 RUN ALL 6 MODELS - SPOTLIGHT 1
                logger.info("🚀 Running multi-model prediction ensemble...")

                if model_ensemble is None:
                    messages.error(
                        request, "ML Engine not initialized. Please contact admin."
                    )
                    return redirect("detection:doctor_dashboard")

                results = model_ensemble.predict_all_models(processed_path)

                # Save predictions to database
                prediction = Prediction.objects.create(
                    xray=xray,
                    # CrossViT
                    crossvit_prediction=results["individual_results"]["crossvit"][
                        "prediction"
                    ],
                    crossvit_confidence=results["individual_results"]["crossvit"][
                        "confidence"
                    ],
                    # ResNet-50
                    resnet50_prediction=results["individual_results"]["resnet50"][
                        "prediction"
                    ],
                    resnet50_confidence=results["individual_results"]["resnet50"][
                        "confidence"
                    ],
                    # DenseNet-121
                    densenet121_prediction=results["individual_results"]["densenet121"][
                        "prediction"
                    ],
                    densenet121_confidence=results["individual_results"]["densenet121"][
                        "confidence"
                    ],
                    # EfficientNet-B0
                    efficientnet_prediction=results["individual_results"][
                        "efficientnet"
                    ]["prediction"],
                    efficientnet_confidence=results["individual_results"][
                        "efficientnet"
                    ]["confidence"],
                    # ViT-Base
                    vit_prediction=results["individual_results"]["vit"]["prediction"],
                    vit_confidence=results["individual_results"]["vit"]["confidence"],
                    # Swin-Tiny
                    swin_prediction=results["individual_results"]["swin"]["prediction"],
                    swin_confidence=results["individual_results"]["swin"]["confidence"],
                    # Final diagnosis
                    final_diagnosis=results["consensus_diagnosis"],
                    consensus_confidence=results["best_confidence"],
                    inference_time=results["inference_time"],
                )

                logger.info(f"✅ Prediction saved: ID={prediction.id}")

                # Send notification to patient
                try:
                    NotificationService.send_prediction_notification(prediction)
                    logger.info(f"📧 Notification sent for prediction ID={prediction.id}")
                except Exception as e:
                    logger.error(f"❌ Failed to send notification: {e}")

                messages.success(
                    request,
                    f'✅ Analysis complete! Consensus: {results["consensus_diagnosis"]} '
                    f'({results["model_agreement"]}/6 models agree)',
                )

                return redirect("detection:view_results", prediction_id=prediction.id)

            except Exception as e:
                logger.error(f"❌ Error during prediction: {e}", exc_info=True)
                messages.error(request, f"Error during analysis: {str(e)}")
                return render(request, "detection/upload.html", {"form": form})
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
    if request.user.profile.is_doctor():
        # Doctors see all predictions
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
    if not request.user.profile.is_doctor():
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

    return render(request, "dashboards/patient_dashboard.html", context)


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
# BATCH UPLOAD VIEWS
# ============================================================================


@login_required
def batch_upload(request):
    """
    Batch upload multiple X-ray images for processing
    Doctors only - allows uploading 1-50 images at once
    """
    if not request.user.profile.is_doctor():
        messages.error(request, "Access denied. Doctors only.")
        return redirect("home")

    if request.method == "POST":
        form = BatchXRayUploadForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                # Get form data
                patient = form.cleaned_data['patient']
                apply_clahe = form.cleaned_data['apply_clahe']
                notes = form.cleaned_data.get('notes', '')

                # Get uploaded files (Django handles multiple files)
                files = request.FILES.getlist('images')

                # Validate number of files
                if not files:
                    messages.error(request, "No images were uploaded.")
                    return render(request, "detection/batch_upload.html", {"form": form})

                if len(files) > 50:
                    messages.error(request, "Maximum 50 images allowed per batch.")
                    return render(request, "detection/batch_upload.html", {"form": form})

                # Create batch job
                batch_job = BatchUploadJob.objects.create(
                    created_by=request.user,
                    patient=patient,
                    total_images=len(files),
                    apply_clahe=apply_clahe,
                    notes=notes
                )

                # Save uploaded files as BatchUploadImage records
                for idx, file in enumerate(files):
                    BatchUploadImage.objects.create(
                        batch_job=batch_job,
                        image_file=file,
                        original_filename=file.name,
                        order=idx
                    )

                logger.info(
                    f"Created batch job {batch_job.job_id} with {len(files)} images "
                    f"for patient {patient.id}"
                )

                # Queue the batch processing task
                from .tasks import process_batch_upload
                task = process_batch_upload.delay(batch_job.id)

                batch_job.celery_task_id = task.id
                batch_job.save()

                messages.success(
                    request,
                    f"Batch upload started! Processing {len(files)} images. "
                    f"Job ID: {batch_job.job_id}"
                )

                return redirect("detection:batch_job_detail", job_id=batch_job.job_id)

            except Exception as e:
                logger.error(f"Error creating batch job: {e}", exc_info=True)
                messages.error(request, f"Error creating batch upload: {str(e)}")
                return render(request, "detection/batch_upload.html", {"form": form})
    else:
        form = BatchXRayUploadForm()

    # Get list of patients for dropdown
    patients = Patient.objects.all().select_related("user")

    context = {
        "form": form,
        "patients": patients
    }

    return render(request, "detection/batch_upload.html", context)


@login_required
def batch_job_list(request):
    """
    List all batch upload jobs
    Doctors see all jobs, patients see their own
    """
    if request.user.profile.is_doctor():
        batch_jobs = BatchUploadJob.objects.all().select_related(
            'created_by', 'patient__user'
        ).order_by('-created_at')
    elif request.user.profile.is_patient():
        # Patients see jobs for their X-rays
        batch_jobs = BatchUploadJob.objects.filter(
            patient__user=request.user
        ).select_related('created_by', 'patient__user').order_by('-created_at')
    else:
        messages.error(request, "Access denied")
        return redirect("home")

    # Apply filters
    status_filter = request.GET.get('status')
    if status_filter:
        batch_jobs = batch_jobs.filter(status=status_filter)

    context = {
        'batch_jobs': batch_jobs,
        'status_filter': status_filter
    }

    return render(request, "detection/batch_job_list.html", context)


@login_required
def batch_job_detail(request, job_id):
    """
    View details of a specific batch upload job with progress tracking
    """
    batch_job = get_object_or_404(
        BatchUploadJob.objects.select_related('created_by', 'patient__user'),
        job_id=job_id
    )

    # Check permissions
    if request.user.profile.is_patient():
        if batch_job.patient.user != request.user:
            messages.error(request, "Access denied")
            return redirect("home")

    # Get all images in this batch
    batch_images = batch_job.images.all().select_related(
        'xray_image__patient'
    ).order_by('order')

    # Calculate statistics
    stats = {
        'total': batch_job.total_images,
        'processed': batch_job.images_processed,
        'successful': batch_job.images_successful,
        'failed': batch_job.images_failed,
        'pending': batch_job.total_images - batch_job.images_processed,
        'progress_percentage': batch_job.get_progress_percentage()
    }

    context = {
        'batch_job': batch_job,
        'batch_images': batch_images,
        'stats': stats
    }

    return render(request, "detection/batch_job_detail.html", context)


@login_required
def batch_job_progress(request, job_id):
    """
    API endpoint to get batch job progress (for AJAX polling)
    Returns JSON with current progress
    """
    batch_job = get_object_or_404(BatchUploadJob, job_id=job_id)

    # Check permissions
    if request.user.profile.is_patient():
        if batch_job.patient.user != request.user:
            return JsonResponse({"error": "Access denied"}, status=403)

    # Get Celery task status if task is running
    task_status = None
    if batch_job.celery_task_id:
        from celery.result import AsyncResult
        result = AsyncResult(batch_job.celery_task_id)
        task_status = {
            'state': result.state,
            'info': result.info if result.info else {}
        }

    data = {
        'job_id': str(batch_job.job_id),
        'status': batch_job.status,
        'total_images': batch_job.total_images,
        'images_processed': batch_job.images_processed,
        'images_successful': batch_job.images_successful,
        'images_failed': batch_job.images_failed,
        'progress_percentage': batch_job.get_progress_percentage(),
        'created_at': batch_job.created_at.isoformat(),
        'started_at': batch_job.started_at.isoformat() if batch_job.started_at else None,
        'completed_at': batch_job.completed_at.isoformat() if batch_job.completed_at else None,
        'error_message': batch_job.error_message,
        'task_status': task_status
    }

    return JsonResponse(data)


@login_required
@require_POST
def batch_job_retry(request, job_id):
    """
    Retry failed images in a batch job
    """
    if not request.user.profile.is_doctor():
        messages.error(request, "Access denied. Doctors only.")
        return redirect("home")

    batch_job = get_object_or_404(BatchUploadJob, job_id=job_id)

    # Check if there are failed images
    failed_count = batch_job.images.filter(status='failed').count()

    if failed_count == 0:
        messages.info(request, "No failed images to retry.")
        return redirect("detection:batch_job_detail", job_id=job_id)

    try:
        # Queue retry task
        from .tasks import retry_failed_batch_images
        task = retry_failed_batch_images.delay(batch_job.id)

        messages.success(
            request,
            f"Retrying {failed_count} failed images..."
        )

    except Exception as e:
        logger.error(f"Error retrying batch job: {e}", exc_info=True)
        messages.error(request, f"Error retrying: {str(e)}")

    return redirect("detection:batch_job_detail", job_id=job_id)


@login_required
def batch_job_cancel(request, job_id):
    """
    Cancel a pending or processing batch job
    """
    if not request.user.profile.is_doctor():
        messages.error(request, "Access denied. Doctors only.")
        return redirect("home")

    batch_job = get_object_or_404(BatchUploadJob, job_id=job_id)

    if batch_job.status in ['completed', 'failed']:
        messages.info(request, "Cannot cancel completed or failed jobs.")
        return redirect("detection:batch_job_detail", job_id=job_id)

    try:
        # Revoke Celery task if it exists
        if batch_job.celery_task_id:
            from celery import current_app
            current_app.control.revoke(batch_job.celery_task_id, terminate=True)

        # Mark as failed with cancellation message
        batch_job.mark_as_failed(error_message="Job cancelled by user")

        messages.success(request, "Batch job cancelled successfully.")

    except Exception as e:
        logger.error(f"Error cancelling batch job: {e}", exc_info=True)
        messages.error(request, f"Error cancelling job: {str(e)}")

    return redirect("detection:batch_job_detail", job_id=job_id)


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
