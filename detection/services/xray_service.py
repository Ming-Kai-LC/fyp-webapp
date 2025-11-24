"""
X-Ray Service
Handles X-ray image upload, validation, and preprocessing
"""

from typing import Optional
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.conf import settings
from detection.models import XRayImage, Patient
import os
import logging

try:
    from detection.preprocessing import apply_clahe
except ImportError:
    from detection.preprocessing_stub import apply_clahe

logger = logging.getLogger(__name__)


class XRayService:
    """
    Service for handling X-ray image operations

    Responsibilities:
    - Validate and save uploaded X-ray images
    - Apply CLAHE preprocessing
    - Manage image file paths
    """

    @staticmethod
    def save_xray(
        image_file,
        patient: Patient,
        uploaded_by: User,
        notes: str = ""
    ) -> XRayImage:
        """
        Save uploaded X-ray image with validation

        Args:
            image_file: Django UploadedFile instance
            patient: Patient instance
            uploaded_by: User who uploaded the image (must be staff)
            notes: Optional clinical notes

        Returns:
            Saved XRayImage instance

        Raises:
            ValidationError: If validation fails

        Example:
            >>> xray = XRayService.save_xray(
            ...     image_file=request.FILES['image'],
            ...     patient=patient,
            ...     uploaded_by=request.user,
            ...     notes="Patient reports cough"
            ... )
        """
        # Validate inputs
        if not patient:
            raise ValidationError("Patient is required")

        if not uploaded_by:
            raise ValidationError("Uploaded by user is required")

        if not image_file:
            raise ValidationError("Image file is required")

        # Create XRay instance
        xray = XRayImage(
            patient=patient,
            uploaded_by=uploaded_by,
            notes=notes
        )

        # Save the image file
        xray.original_image = image_file
        xray.save()

        logger.info(f"X-ray uploaded: {xray.original_image.path} for patient {patient.user.username}")

        return xray

    @staticmethod
    def apply_preprocessing(xray: XRayImage) -> str:
        """
        Apply CLAHE preprocessing to X-ray image

        Args:
            xray: XRayImage instance with original_image

        Returns:
            Absolute path to processed image

        Raises:
            ValidationError: If preprocessing fails

        Example:
            >>> processed_path = XRayService.apply_preprocessing(xray)
            >>> print(processed_path)
            '/path/to/media/xrays/processed/image_clahe.jpg'
        """
        if not xray.original_image:
            raise ValidationError("Original image not found")

        try:
            logger.info(f"Applying CLAHE preprocessing to X-ray ID={xray.id}")

            # Apply CLAHE preprocessing
            processed_path = apply_clahe(xray.original_image.path)

            # Convert absolute path to relative media path
            relative_path = os.path.relpath(processed_path, settings.MEDIA_ROOT)

            # Update xray with processed image path
            xray.processed_image = relative_path
            xray.save()

            logger.info(f"Preprocessing complete: {relative_path}")

            return processed_path

        except Exception as e:
            logger.error(f"Preprocessing failed for X-ray ID={xray.id}: {e}", exc_info=True)
            raise ValidationError(f"Preprocessing failed: {str(e)}")

    @staticmethod
    def validate_image_file(file) -> bool:
        """
        Validate uploaded image file

        Args:
            file: Django UploadedFile instance

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """
        # Check file size (10MB limit)
        max_size = 10 * 1024 * 1024  # 10MB
        if file.size > max_size:
            raise ValidationError(
                f"File size ({file.size / 1024 / 1024:.2f}MB) exceeds maximum "
                f"allowed size ({max_size / 1024 / 1024}MB)"
            )

        # Check file extension
        allowed_extensions = ['.jpg', '.jpeg', '.png']
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in allowed_extensions:
            raise ValidationError(
                f"File extension '{ext}' not allowed. "
                f"Allowed: {', '.join(allowed_extensions)}"
            )

        # Check content type
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
        if file.content_type not in allowed_types:
            raise ValidationError(
                f"File type '{file.content_type}' not allowed. "
                f"Expected image file."
            )

        return True

    @staticmethod
    def get_xray_by_id(xray_id: int) -> Optional[XRayImage]:
        """
        Get X-ray by ID with related data

        Args:
            xray_id: X-ray image ID

        Returns:
            XRayImage instance or None
        """
        try:
            return XRayImage.objects.select_related(
                'patient__user',
                'uploaded_by'
            ).get(id=xray_id)
        except XRayImage.DoesNotExist:
            return None
