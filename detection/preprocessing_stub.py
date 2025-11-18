# detection/preprocessing_stub.py
"""
STUB VERSION - Image preprocessing for COVID-19 detection
This is a placeholder to allow the Django app to run without OpenCV/Pillow processing.
"""

import logging

logger = logging.getLogger(__name__)


def apply_clahe(image_path, output_path=None):
    """
    STUB: CLAHE preprocessing
    In production, this applies Contrast Limited Adaptive Histogram Equalization
    """
    logger.warning(f"STUB: Skipping CLAHE preprocessing for {image_path}")
    return image_path  # Return original path
