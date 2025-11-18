# detection/tasks.py
"""
Celery Tasks for Batch X-ray Processing
Handles asynchronous batch upload and processing of X-ray images
"""

import os
import time
import logging
from typing import List, Dict, Any
from datetime import timedelta
from django.utils import timezone
from django.core.files.base import ContentFile
from django.db import transaction
from celery import shared_task, current_task
from PIL import Image
import cv2
import numpy as np

from .models import (
    XRayImage, Patient, Prediction,
    BatchUploadJob, BatchUploadImage
)
from .services.preprocessing import apply_clahe_preprocessing

logger = logging.getLogger(__name__)


@shared_task(bind=True, name='detection.tasks.process_batch_upload')
def process_batch_upload(self, batch_job_id: int) -> Dict[str, Any]:
    """
    Process a batch upload job asynchronously

    Args:
        batch_job_id: ID of the BatchUploadJob to process

    Returns:
        dict: Summary of batch processing results
    """
    try:
        # Get the batch job
        batch_job = BatchUploadJob.objects.get(id=batch_job_id)

        # Update job status to processing
        batch_job.mark_as_processing()
        batch_job.celery_task_id = self.request.id
        batch_job.save()

        logger.info(f"Starting batch job {batch_job.job_id} with {batch_job.total_images} images")

        # Get all images in this batch ordered by their sequence
        batch_images = batch_job.images.order_by('order')

        results = {
            'successful': 0,
            'failed': 0,
            'errors': []
        }

        # Process each image
        for idx, batch_image in enumerate(batch_images):
            try:
                # Update task progress
                progress = int((idx / batch_job.total_images) * 100)
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'current': idx + 1,
                        'total': batch_job.total_images,
                        'percent': progress,
                        'status': f'Processing image {idx + 1} of {batch_job.total_images}'
                    }
                )

                # Process individual image
                success = process_single_batch_image(batch_image, batch_job)

                if success:
                    results['successful'] += 1
                    batch_job.increment_progress(success=True)
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Failed to process {batch_image.original_filename}")
                    batch_job.increment_progress(success=False)

            except Exception as e:
                logger.error(f"Error processing batch image {batch_image.id}: {str(e)}")
                results['failed'] += 1
                results['errors'].append(f"{batch_image.original_filename}: {str(e)}")
                batch_job.increment_progress(success=False)

        # Update final job status
        if results['failed'] == 0:
            batch_job.mark_as_completed()
        elif results['successful'] > 0:
            batch_job.status = 'partial'
            batch_job.save()
        else:
            batch_job.mark_as_failed(error_message="All images failed to process")

        batch_job.completed_at = timezone.now()
        batch_job.save()

        logger.info(
            f"Completed batch job {batch_job.job_id}: "
            f"{results['successful']} successful, {results['failed']} failed"
        )

        return {
            'job_id': str(batch_job.job_id),
            'status': batch_job.status,
            'successful': results['successful'],
            'failed': results['failed'],
            'total': batch_job.total_images,
            'errors': results['errors'][:10]  # Limit error list
        }

    except BatchUploadJob.DoesNotExist:
        logger.error(f"Batch job {batch_job_id} not found")
        return {'error': 'Batch job not found'}

    except Exception as e:
        logger.error(f"Fatal error processing batch job {batch_job_id}: {str(e)}")
        try:
            batch_job = BatchUploadJob.objects.get(id=batch_job_id)
            batch_job.mark_as_failed(error_message=str(e))
        except:
            pass
        return {'error': str(e)}


def process_single_batch_image(batch_image: BatchUploadImage, batch_job: BatchUploadJob) -> bool:
    """
    Process a single image from a batch upload

    Args:
        batch_image: BatchUploadImage instance to process
        batch_job: Parent BatchUploadJob instance

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        batch_image.mark_as_processing()
        start_time = time.time()

        # Get patient
        patient = batch_job.patient
        if not patient:
            raise ValueError("No patient assigned to batch job")

        # Create XRayImage instance
        xray = XRayImage.objects.create(
            patient=patient,
            uploaded_by=batch_job.created_by,
            original_image=batch_image.image_file,
            notes=batch_job.notes or f"Batch upload: {batch_job.job_id}"
        )

        # Apply CLAHE preprocessing if requested
        if batch_job.apply_clahe:
            try:
                processed_image = apply_clahe_preprocessing(xray.original_image.path)

                # Save processed image
                if processed_image is not None:
                    # Convert back to bytes
                    is_success, buffer = cv2.imencode('.jpg', processed_image)
                    if is_success:
                        xray.processed_image.save(
                            f'processed_{os.path.basename(xray.original_image.name)}',
                            ContentFile(buffer.tobytes()),
                            save=False
                        )
                        xray.save()
                        logger.debug(f"Applied CLAHE to {batch_image.original_filename}")

            except Exception as e:
                logger.warning(f"CLAHE preprocessing failed for {batch_image.original_filename}: {e}")
                # Continue without CLAHE - not a fatal error

        # TODO: Run ML model inference when models are available
        # For now, we'll create a placeholder prediction
        # prediction = run_ml_inference(xray)

        # Link the XRayImage to the batch image
        batch_image.xray_image = xray
        batch_image.processing_time = time.time() - start_time
        batch_image.mark_as_completed()

        logger.debug(
            f"Processed {batch_image.original_filename} in "
            f"{batch_image.processing_time:.2f}s"
        )

        return True

    except Exception as e:
        logger.error(f"Error processing single batch image {batch_image.id}: {str(e)}")
        batch_image.mark_as_failed(error_message=str(e))
        return False


def apply_clahe_preprocessing(image_path: str) -> np.ndarray:
    """
    Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to X-ray image

    Args:
        image_path: Path to the image file

    Returns:
        numpy.ndarray: Preprocessed image
    """
    try:
        # Read image
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

        if img is None:
            raise ValueError(f"Could not read image: {image_path}")

        # Apply CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(img)

        # Resize to standard size (224x224 for most models)
        enhanced = cv2.resize(enhanced, (224, 224), interpolation=cv2.INTER_AREA)

        return enhanced

    except Exception as e:
        logger.error(f"CLAHE preprocessing error: {str(e)}")
        raise


@shared_task(name='detection.tasks.cleanup_old_batch_jobs')
def cleanup_old_batch_jobs(days: int = 30) -> Dict[str, int]:
    """
    Clean up old completed batch jobs and their associated files
    Runs daily via Celery Beat

    Args:
        days: Delete jobs older than this many days (default: 30)

    Returns:
        dict: Number of jobs and files deleted
    """
    try:
        cutoff_date = timezone.now() - timedelta(days=days)

        # Find old completed or failed jobs
        old_jobs = BatchUploadJob.objects.filter(
            created_at__lt=cutoff_date,
            status__in=['completed', 'failed']
        )

        jobs_deleted = 0
        files_deleted = 0

        for job in old_jobs:
            try:
                # Delete associated image files
                for batch_image in job.images.all():
                    if batch_image.image_file:
                        try:
                            if os.path.exists(batch_image.image_file.path):
                                os.remove(batch_image.image_file.path)
                                files_deleted += 1
                        except Exception as e:
                            logger.warning(f"Could not delete file: {e}")

                # Delete the job (cascade will delete BatchUploadImage records)
                job.delete()
                jobs_deleted += 1

            except Exception as e:
                logger.error(f"Error deleting batch job {job.id}: {e}")

        logger.info(f"Cleanup: Deleted {jobs_deleted} jobs and {files_deleted} files")

        return {
            'jobs_deleted': jobs_deleted,
            'files_deleted': files_deleted
        }

    except Exception as e:
        logger.error(f"Error in cleanup task: {e}")
        return {'error': str(e)}


@shared_task(name='detection.tasks.retry_failed_batch_images')
def retry_failed_batch_images(batch_job_id: int) -> Dict[str, Any]:
    """
    Retry processing failed images in a batch job

    Args:
        batch_job_id: ID of the BatchUploadJob

    Returns:
        dict: Results of retry operation
    """
    try:
        batch_job = BatchUploadJob.objects.get(id=batch_job_id)

        # Get all failed images
        failed_images = batch_job.images.filter(status='failed')

        if not failed_images.exists():
            return {
                'message': 'No failed images to retry',
                'retried': 0
            }

        results = {
            'retried': 0,
            'successful': 0,
            'still_failed': 0
        }

        # Reset images to pending and retry
        for batch_image in failed_images:
            batch_image.status = 'pending'
            batch_image.error_message = None
            batch_image.save()

            success = process_single_batch_image(batch_image, batch_job)

            results['retried'] += 1
            if success:
                results['successful'] += 1
            else:
                results['still_failed'] += 1

        # Update batch job status if needed
        if results['still_failed'] == 0:
            batch_job.mark_as_completed()
        elif results['successful'] > 0:
            batch_job.status = 'partial'
            batch_job.save()

        logger.info(
            f"Retry batch job {batch_job.job_id}: "
            f"{results['successful']}/{results['retried']} successful"
        )

        return results

    except BatchUploadJob.DoesNotExist:
        return {'error': 'Batch job not found'}

    except Exception as e:
        logger.error(f"Error retrying failed images: {e}")
        return {'error': str(e)}


# TODO: Implement ML inference task when models are ready
# @shared_task(name='detection.tasks.run_ml_inference')
# def run_ml_inference(xray_id: int) -> Dict[str, Any]:
#     """
#     Run ML model inference on an X-ray image
#
#     Args:
#         xray_id: ID of the XRayImage
#
#     Returns:
#         dict: Prediction results from all models
#     """
#     pass
