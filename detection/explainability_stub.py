# detection/explainability_stub.py
"""
STUB VERSION - Explainability module for COVID-19 detection
This is a placeholder to allow the Django app to run without PyTorch Grad-CAM.
"""

import logging

logger = logging.getLogger(__name__)


def generate_explainability_report(xray_image, prediction, output_dir):
    """
    STUB: Generate Grad-CAM and attention visualizations
    In production, this generates heatmaps and attention maps
    """
    logger.warning(f"STUB: Skipping explainability generation for prediction {prediction.id}")
    return {
        'gradcam_path': None,
        'large_branch_path': None,
        'small_branch_path': None
    }
