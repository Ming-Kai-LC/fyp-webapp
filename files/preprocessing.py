# detection/preprocessing.py
"""
Image Preprocessing Module for COVID-19 Detection
Implements CLAHE (Contrast Limited Adaptive Histogram Equalization)
"""

import cv2
import numpy as np
from PIL import Image
import os
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def apply_clahe(image_path, clip_limit=2.0, tile_grid_size=(8, 8)):
    """
    Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to enhance X-ray contrast
    
    Args:
        image_path: str - path to input image
        clip_limit: float - threshold for contrast limiting (default: 2.0)
        tile_grid_size: tuple - size of grid for histogram equalization (default: 8x8)
    
    Returns:
        str - path to processed image
    """
    try:
        logger.info(f"🔧 Applying CLAHE to: {os.path.basename(image_path)}")
        
        # Read image
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        l_clahe = clahe.apply(l)
        
        # Merge channels
        lab_clahe = cv2.merge([l_clahe, a, b])
        
        # Convert back to BGR
        enhanced = cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2BGR)
        
        # Generate output path
        input_filename = os.path.basename(image_path)
        output_dir = os.path.join(settings.MEDIA_ROOT, 'xrays', 'processed')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"clahe_{input_filename}")
        
        # Save enhanced image
        cv2.imwrite(output_path, enhanced)
        
        logger.info(f"   ✅ CLAHE applied successfully: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"   ❌ CLAHE error: {e}")
        # Return original image path if processing fails
        return image_path


def resize_image(image_path, target_size=(224, 224)):
    """
    Resize image to target size
    
    Args:
        image_path: str - path to input image
        target_size: tuple - target (width, height)
    
    Returns:
        np.ndarray - resized image
    """
    image = cv2.imread(str(image_path))
    resized = cv2.resize(image, target_size, interpolation=cv2.INTER_CUBIC)
    return resized


def normalize_image(image):
    """
    Normalize image pixel values to [0, 1]
    
    Args:
        image: np.ndarray - input image
    
    Returns:
        np.ndarray - normalized image
    """
    return image.astype(np.float32) / 255.0


def preprocess_xray_pipeline(image_path, apply_clahe_flag=True):
    """
    Complete preprocessing pipeline for X-ray images
    
    Args:
        image_path: str - path to input X-ray
        apply_clahe_flag: bool - whether to apply CLAHE
    
    Returns:
        str - path to processed image
    """
    if apply_clahe_flag:
        processed_path = apply_clahe(image_path)
        return processed_path
    return image_path
