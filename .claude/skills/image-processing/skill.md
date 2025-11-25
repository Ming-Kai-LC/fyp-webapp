# Image Processing & Display Skill

## Overview

This skill defines comprehensive patterns for handling medical images (X-rays) in the COVID-19 Detection System, covering:
- Server-side image processing (validation, enhancement, transformation)
- Client-side image display (viewer, zoom, pan, comparison)
- Performance optimization (thumbnails, lazy loading, caching)
- Medical imaging standards (DICOM, Window/Level)

---

## 1. Server-Side Image Validation

### 1.1 Comprehensive Image Validation

```python
# common/validators.py

import os
import magic
from PIL import Image
from io import BytesIO
from django.core.exceptions import ValidationError
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class ImageValidator:
    """
    Comprehensive image validation for medical images.

    Features:
    - File extension validation
    - MIME type validation (magic bytes)
    - File size limits
    - Image dimension validation
    - Image quality assessment
    - EXIF orientation detection
    """

    # Allowed formats for X-ray images
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.dcm'}
    ALLOWED_MIME_TYPES = {
        'image/jpeg',
        'image/png',
        'application/dicom'
    }

    # Size limits
    MAX_FILE_SIZE_MB = 10
    MIN_DIMENSION = 224  # Minimum for ML models
    MAX_DIMENSION = 4096  # Reasonable upper limit

    @classmethod
    def validate_file(cls, file, max_size_mb: int = None) -> dict:
        """
        Comprehensive file validation.

        Args:
            file: Django UploadedFile
            max_size_mb: Override default max size

        Returns:
            dict with validation results and metadata

        Raises:
            ValidationError: If validation fails
        """
        max_size = (max_size_mb or cls.MAX_FILE_SIZE_MB) * 1024 * 1024

        # 1. File size validation
        if file.size > max_size:
            raise ValidationError(
                f"File size ({file.size / 1024 / 1024:.2f}MB) exceeds "
                f"maximum allowed ({max_size / 1024 / 1024}MB)."
            )

        # 2. Extension validation
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            raise ValidationError(
                f"File extension '{ext}' not allowed. "
                f"Allowed: {', '.join(cls.ALLOWED_EXTENSIONS)}"
            )

        # 3. MIME type validation (magic bytes)
        file.seek(0)
        mime_type = magic.from_buffer(file.read(2048), mime=True)
        file.seek(0)

        if mime_type not in cls.ALLOWED_MIME_TYPES:
            raise ValidationError(
                f"File type '{mime_type}' not allowed. "
                f"Only medical images (JPEG, PNG, DICOM) accepted."
            )

        # 4. Image validation (for non-DICOM)
        metadata = {'mime_type': mime_type, 'file_size': file.size}

        if mime_type != 'application/dicom':
            metadata.update(cls._validate_image_content(file))

        return metadata

    @classmethod
    def _validate_image_content(cls, file) -> dict:
        """Validate image content using PIL."""
        try:
            file.seek(0)
            img = Image.open(file)
            img.verify()  # Verify it's a valid image

            # Re-open for dimension check (verify() invalidates)
            file.seek(0)
            img = Image.open(file)
            width, height = img.size

            # Dimension validation
            if width < cls.MIN_DIMENSION or height < cls.MIN_DIMENSION:
                raise ValidationError(
                    f"Image too small ({width}x{height}). "
                    f"Minimum: {cls.MIN_DIMENSION}x{cls.MIN_DIMENSION}px."
                )

            if width > cls.MAX_DIMENSION or height > cls.MAX_DIMENSION:
                raise ValidationError(
                    f"Image too large ({width}x{height}). "
                    f"Maximum: {cls.MAX_DIMENSION}x{cls.MAX_DIMENSION}px."
                )

            # Extract metadata
            metadata = {
                'width': width,
                'height': height,
                'format': img.format,
                'mode': img.mode,
                'has_exif': hasattr(img, '_getexif') and img._getexif() is not None,
            }

            # Check EXIF orientation
            if metadata['has_exif']:
                metadata['orientation'] = cls._get_exif_orientation(img)

            file.seek(0)
            return metadata

        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Invalid or corrupted image file: {str(e)}")

    @classmethod
    def _get_exif_orientation(cls, img) -> int:
        """Get EXIF orientation tag (1-8)."""
        try:
            from PIL.ExifTags import TAGS
            exif = img._getexif()
            if exif:
                for tag, value in exif.items():
                    if TAGS.get(tag) == 'Orientation':
                        return value
        except Exception:
            pass
        return 1  # Default: normal orientation

    @classmethod
    def assess_quality(cls, file) -> dict:
        """
        Assess image quality for X-ray analysis.

        Returns:
            dict with quality metrics and warnings
        """
        file.seek(0)
        img = Image.open(file)

        quality = {
            'is_acceptable': True,
            'warnings': [],
            'score': 100
        }

        # Check if grayscale (preferred for X-rays)
        if img.mode not in ('L', 'LA'):
            quality['warnings'].append("Image is not grayscale. X-rays should be grayscale.")
            quality['score'] -= 10

        # Check aspect ratio (X-rays are typically square-ish)
        width, height = img.size
        aspect_ratio = max(width, height) / min(width, height)
        if aspect_ratio > 2.0:
            quality['warnings'].append(
                f"Unusual aspect ratio ({aspect_ratio:.2f}). "
                "X-rays are typically square."
            )
            quality['score'] -= 15

        # Check resolution
        if width < 512 or height < 512:
            quality['warnings'].append(
                f"Low resolution ({width}x{height}). "
                "Recommended: 512x512 or higher."
            )
            quality['score'] -= 20

        # Calculate blur score (Laplacian variance)
        import numpy as np
        import cv2

        file.seek(0)
        img_array = np.array(Image.open(file).convert('L'))
        laplacian_var = cv2.Laplacian(img_array, cv2.CV_64F).var()

        if laplacian_var < 100:
            quality['warnings'].append(
                f"Image appears blurry (variance: {laplacian_var:.2f}). "
                "Consider re-uploading a clearer image."
            )
            quality['score'] -= 25
            quality['blur_score'] = laplacian_var

        quality['is_acceptable'] = quality['score'] >= 60
        file.seek(0)

        return quality
```

### 1.2 Form Integration

```python
# detection/forms.py

from django import forms
from common.validators import ImageValidator


class XRayUploadForm(forms.ModelForm):
    """X-Ray upload form with comprehensive validation."""

    class Meta:
        model = XRayImage
        fields = ['patient', 'original_image', 'notes']
        widgets = {
            'original_image': BootstrapFileInput(
                attrs={
                    'accept': 'image/jpeg,image/png,.dcm',
                    'data-max-size': '10485760',  # 10MB in bytes
                    'data-min-width': '224',
                    'data-min-height': '224',
                }
            ),
        }

    def clean_original_image(self):
        """Validate uploaded X-ray image."""
        image = self.cleaned_data.get('original_image')

        if not image:
            raise forms.ValidationError("Please select an X-ray image to upload.")

        # Comprehensive validation
        try:
            metadata = ImageValidator.validate_file(image, max_size_mb=10)

            # Store metadata for later use
            self._image_metadata = metadata

        except ValidationError as e:
            raise forms.ValidationError(str(e))

        # Quality assessment (warning only, not blocking)
        quality = ImageValidator.assess_quality(image)
        if quality['warnings']:
            for warning in quality['warnings']:
                # Store warnings to display to user
                if not hasattr(self, '_quality_warnings'):
                    self._quality_warnings = []
                self._quality_warnings.append(warning)

        return image

    def get_quality_warnings(self) -> list:
        """Get quality warnings for display."""
        return getattr(self, '_quality_warnings', [])
```

---

## 2. Image Preprocessing Pipeline

### 2.1 Complete Preprocessing Service

```python
# detection/services/image_processing_service.py

import os
import cv2
import numpy as np
from PIL import Image, ImageOps
from django.conf import settings
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


class ImageProcessingService:
    """
    Comprehensive image preprocessing for X-ray analysis.

    Preprocessing Steps:
    1. EXIF orientation correction
    2. Color mode conversion (to grayscale)
    3. Resize to standard dimensions
    4. CLAHE enhancement
    5. Normalization
    6. Optional: Noise reduction, edge enhancement
    """

    # Default preprocessing parameters
    DEFAULT_TARGET_SIZE = (224, 224)
    CLAHE_CLIP_LIMIT = 2.0
    CLAHE_TILE_SIZE = (8, 8)

    @classmethod
    def preprocess_xray(
        cls,
        image_path: str,
        output_dir: str = None,
        apply_clahe: bool = True,
        apply_denoise: bool = False,
        target_size: tuple = None,
    ) -> dict:
        """
        Complete X-ray preprocessing pipeline.

        Args:
            image_path: Path to original image
            output_dir: Output directory (default: media/xrays/processed)
            apply_clahe: Apply CLAHE enhancement
            apply_denoise: Apply noise reduction
            target_size: Target dimensions for resize

        Returns:
            dict with paths to processed images and metadata
        """
        target_size = target_size or cls.DEFAULT_TARGET_SIZE
        output_dir = output_dir or os.path.join(
            settings.MEDIA_ROOT, 'xrays', 'processed'
        )
        os.makedirs(output_dir, exist_ok=True)

        logger.info(f"Starting preprocessing: {os.path.basename(image_path)}")

        result = {
            'original_path': image_path,
            'steps_applied': [],
        }

        # Load image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")

        # 1. Fix EXIF orientation
        img = cls._fix_orientation(image_path, img)
        result['steps_applied'].append('orientation_fix')

        # 2. Convert to grayscale
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            result['steps_applied'].append('grayscale_conversion')

        # 3. Apply CLAHE
        if apply_clahe:
            img = cls._apply_clahe(img)
            result['steps_applied'].append('clahe_enhancement')

        # 4. Apply noise reduction (optional)
        if apply_denoise:
            img = cls._apply_denoise(img)
            result['steps_applied'].append('noise_reduction')

        # 5. Save processed image
        filename = os.path.basename(image_path)
        name, ext = os.path.splitext(filename)
        processed_filename = f"{name}_processed{ext}"
        processed_path = os.path.join(output_dir, processed_filename)

        cv2.imwrite(processed_path, img)
        result['processed_path'] = processed_path

        # 6. Generate thumbnail
        thumbnail_path = cls._generate_thumbnail(img, output_dir, name)
        result['thumbnail_path'] = thumbnail_path

        # 7. Resize for ML inference
        ml_ready = cv2.resize(img, target_size, interpolation=cv2.INTER_CUBIC)
        ml_ready = ml_ready.astype(np.float32) / 255.0
        result['ml_ready_shape'] = ml_ready.shape

        logger.info(f"Preprocessing complete: {result['steps_applied']}")

        return result

    @classmethod
    def _fix_orientation(cls, image_path: str, img: np.ndarray) -> np.ndarray:
        """Fix image orientation based on EXIF data."""
        try:
            pil_img = Image.open(image_path)
            pil_img = ImageOps.exif_transpose(pil_img)
            return np.array(pil_img)
        except Exception:
            return img  # Return original if EXIF fix fails

    @classmethod
    def _apply_clahe(
        cls,
        img: np.ndarray,
        clip_limit: float = None,
        tile_size: tuple = None
    ) -> np.ndarray:
        """
        Apply CLAHE (Contrast Limited Adaptive Histogram Equalization).

        CLAHE is essential for X-ray images because:
        - Enhances local contrast
        - Preserves details in both bright and dark regions
        - Improves feature visibility for ML models
        """
        clip_limit = clip_limit or cls.CLAHE_CLIP_LIMIT
        tile_size = tile_size or cls.CLAHE_TILE_SIZE

        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_size)
        return clahe.apply(img)

    @classmethod
    def _apply_denoise(cls, img: np.ndarray) -> np.ndarray:
        """Apply Non-local Means Denoising."""
        return cv2.fastNlMeansDenoising(img, None, h=10, templateWindowSize=7, searchWindowSize=21)

    @classmethod
    def _generate_thumbnail(
        cls,
        img: np.ndarray,
        output_dir: str,
        name: str,
        size: tuple = (150, 150)
    ) -> str:
        """Generate thumbnail for list views."""
        thumbnail = cv2.resize(img, size, interpolation=cv2.INTER_AREA)
        thumbnail_path = os.path.join(output_dir, f"{name}_thumb.jpg")
        cv2.imwrite(thumbnail_path, thumbnail, [cv2.IMWRITE_JPEG_QUALITY, 80])
        return thumbnail_path

    # =========================================================================
    # Image Transformation Methods
    # =========================================================================

    @classmethod
    def rotate_image(cls, image_path: str, angle: int) -> str:
        """
        Rotate image by specified angle.

        Args:
            image_path: Path to image
            angle: Rotation angle (90, 180, 270, or -90)

        Returns:
            Path to rotated image
        """
        valid_angles = {90, 180, 270, -90}
        if angle not in valid_angles:
            raise ValueError(f"Invalid rotation angle. Allowed: {valid_angles}")

        img = cv2.imread(image_path)

        if angle == 90:
            rotated = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        elif angle == -90 or angle == 270:
            rotated = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif angle == 180:
            rotated = cv2.rotate(img, cv2.ROTATE_180)

        # Save rotated image
        name, ext = os.path.splitext(image_path)
        output_path = f"{name}_rotated{ext}"
        cv2.imwrite(output_path, rotated)

        return output_path

    @classmethod
    def crop_image(
        cls,
        image_path: str,
        x: int,
        y: int,
        width: int,
        height: int
    ) -> str:
        """
        Crop image to specified region.

        Args:
            image_path: Path to image
            x, y: Top-left corner coordinates
            width, height: Crop dimensions

        Returns:
            Path to cropped image
        """
        img = cv2.imread(image_path)
        h, w = img.shape[:2]

        # Validate crop region
        if x < 0 or y < 0 or x + width > w or y + height > h:
            raise ValueError("Invalid crop region")

        cropped = img[y:y+height, x:x+width]

        name, ext = os.path.splitext(image_path)
        output_path = f"{name}_cropped{ext}"
        cv2.imwrite(output_path, cropped)

        return output_path

    @classmethod
    def adjust_brightness_contrast(
        cls,
        image_path: str,
        brightness: int = 0,
        contrast: float = 1.0
    ) -> str:
        """
        Adjust image brightness and contrast.

        Args:
            image_path: Path to image
            brightness: Brightness adjustment (-100 to 100)
            contrast: Contrast multiplier (0.5 to 2.0)

        Returns:
            Path to adjusted image
        """
        img = cv2.imread(image_path)

        # Apply contrast and brightness
        adjusted = cv2.convertScaleAbs(img, alpha=contrast, beta=brightness)

        name, ext = os.path.splitext(image_path)
        output_path = f"{name}_adjusted{ext}"
        cv2.imwrite(output_path, adjusted)

        return output_path

    @classmethod
    @lru_cache(maxsize=50)
    def get_image_histogram(cls, image_path: str) -> dict:
        """
        Calculate image histogram for display.

        Returns:
            dict with histogram data for visualization
        """
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        hist = cv2.calcHist([img], [0], None, [256], [0, 256])

        return {
            'values': hist.flatten().tolist(),
            'bins': list(range(256)),
            'mean': float(np.mean(img)),
            'std': float(np.std(img)),
            'min': int(np.min(img)),
            'max': int(np.max(img)),
        }
```

### 2.2 Window/Level Adjustment (Medical Imaging Standard)

```python
# detection/services/image_processing_service.py (continued)

class WindowLevelService:
    """
    Window/Level adjustment for medical imaging.

    Window/Level (also called Window Width/Window Center) is the standard
    way to adjust contrast in medical imaging:
    - Window Width: Range of pixel values displayed
    - Window Center: Center of the displayed range
    """

    # Preset window/level values for chest X-rays
    PRESETS = {
        'default': {'width': 400, 'center': 40},
        'lung': {'width': 1500, 'center': -600},
        'bone': {'width': 2000, 'center': 300},
        'mediastinum': {'width': 350, 'center': 50},
    }

    @classmethod
    def apply_window_level(
        cls,
        image_path: str,
        window_width: int,
        window_center: int
    ) -> np.ndarray:
        """
        Apply window/level adjustment.

        Args:
            image_path: Path to image
            window_width: Window width (contrast)
            window_center: Window center (brightness)

        Returns:
            Adjusted image as numpy array
        """
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE).astype(np.float32)

        # Calculate min and max display values
        min_value = window_center - (window_width / 2)
        max_value = window_center + (window_width / 2)

        # Apply window/level
        img = np.clip(img, min_value, max_value)
        img = ((img - min_value) / (max_value - min_value) * 255).astype(np.uint8)

        return img

    @classmethod
    def apply_preset(cls, image_path: str, preset_name: str) -> np.ndarray:
        """Apply a preset window/level configuration."""
        if preset_name not in cls.PRESETS:
            raise ValueError(f"Unknown preset: {preset_name}")

        preset = cls.PRESETS[preset_name]
        return cls.apply_window_level(
            image_path,
            preset['width'],
            preset['center']
        )
```

---

## 3. Client-Side Image Display

### 3.1 Interactive Image Viewer Component

```html
<!-- templates/components/image_viewer.html -->

<!--
  Interactive X-Ray Image Viewer

  Features:
  - Zoom in/out with mousewheel and buttons
  - Pan by dragging
  - Fullscreen mode
  - Side-by-side comparison
  - Window/Level presets
  - Rotation controls
  - Metadata display

  Usage:
  {% include 'components/image_viewer.html' with
     image_url=xray.original_image.url
     processed_url=xray.processed_image.url
     metadata=xray_metadata
  %}
-->

<div id="image-viewer-container" class="card shadow-sm">
    <div class="card-header bg-dark text-white d-flex justify-content-between align-items-center">
        <h5 class="mb-0">
            <i class="bi bi-image"></i> X-Ray Viewer
        </h5>

        <!-- View Mode Tabs -->
        <ul class="nav nav-pills" id="viewTabs" role="tablist">
            <li class="nav-item">
                <button class="nav-link active text-white" data-view="single">
                    <i class="bi bi-image"></i> Single
                </button>
            </li>
            <li class="nav-item">
                <button class="nav-link text-white" data-view="compare">
                    <i class="bi bi-layout-split"></i> Compare
                </button>
            </li>
        </ul>
    </div>

    <div class="card-body bg-dark p-0 position-relative" style="min-height: 400px;">
        <!-- Single View -->
        <div id="single-view" class="viewer-panel">
            <div id="image-container"
                 class="position-relative overflow-hidden"
                 style="cursor: grab;">
                <img id="main-image"
                     src="{{ image_url }}"
                     class="img-fluid"
                     alt="X-Ray Image"
                     draggable="false"
                     style="transform-origin: center center; transition: transform 0.1s;">
            </div>
        </div>

        <!-- Comparison View -->
        <div id="compare-view" class="viewer-panel d-none">
            <div class="row g-0 h-100">
                <div class="col-6 border-end border-secondary">
                    <div class="text-center text-white py-1 bg-secondary">Original</div>
                    <img id="compare-original"
                         src="{{ image_url }}"
                         class="img-fluid w-100"
                         alt="Original">
                </div>
                <div class="col-6">
                    <div class="text-center text-white py-1 bg-success">Processed (CLAHE)</div>
                    <img id="compare-processed"
                         src="{{ processed_url|default:image_url }}"
                         class="img-fluid w-100"
                         alt="Processed">
                </div>
            </div>
        </div>

        <!-- Floating Controls -->
        <div class="position-absolute top-0 end-0 m-3" id="viewer-controls">
            <div class="btn-group-vertical bg-white rounded shadow" role="group">
                <!-- Zoom Controls -->
                <button class="btn btn-light btn-sm" id="btn-zoom-in" title="Zoom In">
                    <i class="bi bi-zoom-in"></i>
                </button>
                <button class="btn btn-light btn-sm" id="btn-zoom-out" title="Zoom Out">
                    <i class="bi bi-zoom-out"></i>
                </button>
                <button class="btn btn-light btn-sm" id="btn-reset" title="Reset View">
                    <i class="bi bi-arrow-repeat"></i>
                </button>

                <div class="dropdown-divider m-0"></div>

                <!-- Rotation Controls -->
                <button class="btn btn-light btn-sm" id="btn-rotate-left" title="Rotate Left">
                    <i class="bi bi-arrow-counterclockwise"></i>
                </button>
                <button class="btn btn-light btn-sm" id="btn-rotate-right" title="Rotate Right">
                    <i class="bi bi-arrow-clockwise"></i>
                </button>

                <div class="dropdown-divider m-0"></div>

                <!-- Fullscreen -->
                <button class="btn btn-light btn-sm" id="btn-fullscreen" title="Fullscreen">
                    <i class="bi bi-fullscreen"></i>
                </button>
            </div>
        </div>

        <!-- Window/Level Presets (for medical imaging) -->
        <div class="position-absolute bottom-0 start-0 m-3" id="wl-presets">
            <div class="btn-group bg-white rounded shadow" role="group">
                <button class="btn btn-sm btn-outline-secondary active" data-preset="default">
                    Default
                </button>
                <button class="btn btn-sm btn-outline-secondary" data-preset="lung">
                    Lung
                </button>
                <button class="btn btn-sm btn-outline-secondary" data-preset="bone">
                    Bone
                </button>
            </div>
        </div>

        <!-- Zoom Level Indicator -->
        <div class="position-absolute bottom-0 end-0 m-3">
            <span id="zoom-level" class="badge bg-dark">100%</span>
        </div>
    </div>

    <!-- Metadata Footer -->
    {% if metadata %}
    <div class="card-footer bg-light">
        <div class="row g-2 small">
            <div class="col-6 col-md-3">
                <strong>Resolution:</strong> {{ metadata.width }}x{{ metadata.height }}
            </div>
            <div class="col-6 col-md-3">
                <strong>Size:</strong> {{ metadata.file_size|filesizeformat }}
            </div>
            <div class="col-6 col-md-3">
                <strong>Format:</strong> {{ metadata.format }}
            </div>
            <div class="col-6 col-md-3">
                <strong>Uploaded:</strong> {{ metadata.uploaded_at|date:"d M Y H:i" }}
            </div>
        </div>
    </div>
    {% endif %}
</div>

<script>
/**
 * Interactive Image Viewer
 *
 * Features:
 * - Mousewheel zoom (centered on cursor)
 * - Pan by dragging
 * - Pinch-to-zoom on touch devices
 * - Keyboard shortcuts
 * - Rotation
 * - Fullscreen mode
 */
class ImageViewer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.image = document.getElementById('main-image');
        this.zoomLevel = 1;
        this.rotation = 0;
        this.panX = 0;
        this.panY = 0;
        this.isDragging = false;
        this.lastX = 0;
        this.lastY = 0;

        this.MIN_ZOOM = 0.5;
        this.MAX_ZOOM = 5;
        this.ZOOM_STEP = 0.25;

        this.init();
    }

    init() {
        this.bindEvents();
        this.bindKeyboardShortcuts();
    }

    bindEvents() {
        const container = document.getElementById('image-container');

        // Mousewheel zoom
        container.addEventListener('wheel', (e) => {
            e.preventDefault();
            const delta = e.deltaY > 0 ? -this.ZOOM_STEP : this.ZOOM_STEP;
            this.zoom(delta, e.offsetX, e.offsetY);
        });

        // Pan (drag)
        container.addEventListener('mousedown', (e) => {
            if (this.zoomLevel > 1) {
                this.isDragging = true;
                this.lastX = e.clientX;
                this.lastY = e.clientY;
                container.style.cursor = 'grabbing';
            }
        });

        document.addEventListener('mousemove', (e) => {
            if (this.isDragging) {
                const deltaX = e.clientX - this.lastX;
                const deltaY = e.clientY - this.lastY;
                this.pan(deltaX, deltaY);
                this.lastX = e.clientX;
                this.lastY = e.clientY;
            }
        });

        document.addEventListener('mouseup', () => {
            this.isDragging = false;
            container.style.cursor = this.zoomLevel > 1 ? 'grab' : 'zoom-in';
        });

        // Touch events for mobile
        container.addEventListener('touchstart', this.handleTouchStart.bind(this));
        container.addEventListener('touchmove', this.handleTouchMove.bind(this));
        container.addEventListener('touchend', this.handleTouchEnd.bind(this));

        // Button controls
        document.getElementById('btn-zoom-in').addEventListener('click', () => this.zoom(this.ZOOM_STEP));
        document.getElementById('btn-zoom-out').addEventListener('click', () => this.zoom(-this.ZOOM_STEP));
        document.getElementById('btn-reset').addEventListener('click', () => this.reset());
        document.getElementById('btn-rotate-left').addEventListener('click', () => this.rotate(-90));
        document.getElementById('btn-rotate-right').addEventListener('click', () => this.rotate(90));
        document.getElementById('btn-fullscreen').addEventListener('click', () => this.toggleFullscreen());

        // View mode tabs
        document.querySelectorAll('[data-view]').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchView(e.target.dataset.view));
        });

        // Window/Level presets
        document.querySelectorAll('[data-preset]').forEach(btn => {
            btn.addEventListener('click', (e) => this.applyPreset(e.target.dataset.preset));
        });
    }

    bindKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

            switch(e.key) {
                case '+':
                case '=':
                    this.zoom(this.ZOOM_STEP);
                    break;
                case '-':
                    this.zoom(-this.ZOOM_STEP);
                    break;
                case '0':
                    this.reset();
                    break;
                case 'r':
                    this.rotate(90);
                    break;
                case 'f':
                    this.toggleFullscreen();
                    break;
            }
        });
    }

    zoom(delta, centerX = null, centerY = null) {
        const newZoom = Math.max(this.MIN_ZOOM, Math.min(this.MAX_ZOOM, this.zoomLevel + delta));

        if (newZoom !== this.zoomLevel) {
            this.zoomLevel = newZoom;
            this.updateTransform();
            this.updateZoomIndicator();
        }
    }

    pan(deltaX, deltaY) {
        this.panX += deltaX;
        this.panY += deltaY;
        this.updateTransform();
    }

    rotate(angle) {
        this.rotation = (this.rotation + angle) % 360;
        this.updateTransform();
    }

    reset() {
        this.zoomLevel = 1;
        this.rotation = 0;
        this.panX = 0;
        this.panY = 0;
        this.updateTransform();
        this.updateZoomIndicator();
    }

    updateTransform() {
        const transform = `scale(${this.zoomLevel}) rotate(${this.rotation}deg) translate(${this.panX / this.zoomLevel}px, ${this.panY / this.zoomLevel}px)`;
        this.image.style.transform = transform;
    }

    updateZoomIndicator() {
        document.getElementById('zoom-level').textContent = `${Math.round(this.zoomLevel * 100)}%`;
    }

    toggleFullscreen() {
        const container = this.container;
        if (!document.fullscreenElement) {
            container.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    }

    switchView(view) {
        document.querySelectorAll('[data-view]').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.view === view);
        });

        document.getElementById('single-view').classList.toggle('d-none', view !== 'single');
        document.getElementById('compare-view').classList.toggle('d-none', view !== 'compare');
    }

    applyPreset(preset) {
        document.querySelectorAll('[data-preset]').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.preset === preset);
        });

        // Call API to get processed image with preset
        fetch(`/api/xray/apply-preset/?preset=${preset}&image_id=${this.imageId}`)
            .then(response => response.json())
            .then(data => {
                if (data.image_url) {
                    this.image.src = data.image_url;
                }
            });
    }

    // Touch event handlers for mobile
    handleTouchStart(e) {
        if (e.touches.length === 2) {
            this.initialPinchDistance = this.getPinchDistance(e.touches);
        }
    }

    handleTouchMove(e) {
        if (e.touches.length === 2) {
            e.preventDefault();
            const currentDistance = this.getPinchDistance(e.touches);
            const delta = (currentDistance - this.initialPinchDistance) / 100;
            this.zoom(delta);
            this.initialPinchDistance = currentDistance;
        }
    }

    handleTouchEnd(e) {
        this.initialPinchDistance = null;
    }

    getPinchDistance(touches) {
        const dx = touches[0].clientX - touches[1].clientX;
        const dy = touches[0].clientY - touches[1].clientY;
        return Math.sqrt(dx * dx + dy * dy);
    }
}

// Initialize viewer
document.addEventListener('DOMContentLoaded', function() {
    window.imageViewer = new ImageViewer('image-viewer-container');
});
</script>

<style>
/* Image Viewer Styles */
#image-container {
    min-height: 400px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #000;
}

#main-image {
    max-width: 100%;
    max-height: 70vh;
    user-select: none;
}

.viewer-panel {
    min-height: 400px;
}

/* Fullscreen styles */
#image-viewer-container:fullscreen {
    background: #000;
}

#image-viewer-container:fullscreen #main-image {
    max-height: 90vh;
}

/* Touch device optimizations */
@media (pointer: coarse) {
    #viewer-controls .btn {
        padding: 0.75rem;
        font-size: 1.25rem;
    }
}
</style>
```

### 3.2 Lazy Loading for Image Lists

```html
<!-- templates/detection/prediction_list.html -->

<!-- Lazy loading images for performance -->
<div class="row g-3">
    {% for prediction in predictions %}
    <div class="col-12 col-md-6 col-lg-4">
        <div class="card h-100">
            <div class="position-relative">
                <!-- Placeholder while loading -->
                <div class="placeholder-glow ratio ratio-1x1" id="placeholder-{{ prediction.id }}">
                    <div class="placeholder bg-secondary"></div>
                </div>

                <!-- Actual image (lazy loaded) -->
                <img src="{{ prediction.xray.thumbnail.url|default:'' }}"
                     data-src="{{ prediction.xray.original_image.url }}"
                     class="card-img-top lazy-image d-none"
                     alt="X-Ray for {{ prediction.xray.patient.user.get_full_name }}"
                     loading="lazy"
                     onload="this.classList.remove('d-none'); document.getElementById('placeholder-{{ prediction.id }}').remove();">
            </div>
            <div class="card-body">
                <h6>{{ prediction.xray.patient.user.get_full_name }}</h6>
                {% diagnosis_badge prediction.diagnosis %}
            </div>
        </div>
    </div>
    {% endfor %}
</div>

<script>
// Intersection Observer for lazy loading
document.addEventListener('DOMContentLoaded', function() {
    const lazyImages = document.querySelectorAll('.lazy-image');

    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                observer.unobserve(img);
            }
        });
    }, {
        rootMargin: '100px'  // Start loading 100px before visible
    });

    lazyImages.forEach(img => imageObserver.observe(img));
});
</script>
```

---

## 4. Client-Side Image Validation

```javascript
// static/js/image_validation.js

/**
 * Client-side image validation for X-ray uploads.
 *
 * Validates:
 * - File type (JPEG, PNG)
 * - File size (max 10MB)
 * - Image dimensions (min 224x224)
 * - Image quality (blur detection)
 */
class ImageUploadValidator {
    constructor(options = {}) {
        this.maxSizeMB = options.maxSizeMB || 10;
        this.minWidth = options.minWidth || 224;
        this.minHeight = options.minHeight || 224;
        this.maxWidth = options.maxWidth || 4096;
        this.maxHeight = options.maxHeight || 4096;
        this.allowedTypes = options.allowedTypes || ['image/jpeg', 'image/png'];
        this.onValidationStart = options.onValidationStart || (() => {});
        this.onValidationEnd = options.onValidationEnd || (() => {});
    }

    async validate(file) {
        this.onValidationStart();
        const errors = [];
        const warnings = [];

        // 1. File type validation
        if (!this.allowedTypes.includes(file.type)) {
            errors.push(`Invalid file type: ${file.type}. Allowed: JPEG, PNG.`);
        }

        // 2. File size validation
        const sizeMB = file.size / (1024 * 1024);
        if (sizeMB > this.maxSizeMB) {
            errors.push(`File too large: ${sizeMB.toFixed(2)}MB. Maximum: ${this.maxSizeMB}MB.`);
        }

        // 3. Image dimension validation
        if (errors.length === 0) {
            try {
                const dimensions = await this.getImageDimensions(file);

                if (dimensions.width < this.minWidth || dimensions.height < this.minHeight) {
                    errors.push(
                        `Image too small: ${dimensions.width}x${dimensions.height}. ` +
                        `Minimum: ${this.minWidth}x${this.minHeight}px.`
                    );
                }

                if (dimensions.width > this.maxWidth || dimensions.height > this.maxHeight) {
                    errors.push(
                        `Image too large: ${dimensions.width}x${dimensions.height}. ` +
                        `Maximum: ${this.maxWidth}x${this.maxHeight}px.`
                    );
                }

                // 4. Aspect ratio check
                const aspectRatio = Math.max(dimensions.width, dimensions.height) /
                                   Math.min(dimensions.width, dimensions.height);
                if (aspectRatio > 2.0) {
                    warnings.push('Unusual aspect ratio. X-rays are typically square.');
                }

            } catch (e) {
                errors.push('Could not read image file. File may be corrupted.');
            }
        }

        this.onValidationEnd();

        return {
            isValid: errors.length === 0,
            errors,
            warnings
        };
    }

    getImageDimensions(file) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => {
                resolve({ width: img.width, height: img.height });
                URL.revokeObjectURL(img.src);
            };
            img.onerror = reject;
            img.src = URL.createObjectURL(file);
        });
    }

    generatePreview(file, previewElement) {
        const reader = new FileReader();
        reader.onload = (e) => {
            previewElement.src = e.target.result;
            previewElement.classList.remove('d-none');
        };
        reader.readAsDataURL(file);
    }
}

// Usage
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('id_original_image');
    const previewImg = document.getElementById('image-preview');
    const feedbackEl = document.getElementById('image-feedback');

    const validator = new ImageUploadValidator({
        maxSizeMB: 10,
        minWidth: 224,
        minHeight: 224,
        onValidationStart: () => {
            feedbackEl.innerHTML = '<span class="text-muted">Validating image...</span>';
        }
    });

    fileInput.addEventListener('change', async function(e) {
        const file = e.target.files[0];
        if (!file) return;

        const result = await validator.validate(file);

        if (result.isValid) {
            // Show preview
            validator.generatePreview(file, previewImg);

            // Show warnings if any
            if (result.warnings.length > 0) {
                feedbackEl.innerHTML = result.warnings.map(w =>
                    `<div class="text-warning small"><i class="bi bi-exclamation-triangle"></i> ${w}</div>`
                ).join('');
            } else {
                feedbackEl.innerHTML = '<span class="text-success"><i class="bi bi-check-circle"></i> Image looks good!</span>';
            }

            fileInput.classList.remove('is-invalid');
            fileInput.classList.add('is-valid');
        } else {
            feedbackEl.innerHTML = result.errors.map(err =>
                `<div class="text-danger small"><i class="bi bi-x-circle"></i> ${err}</div>`
            ).join('');

            fileInput.classList.remove('is-valid');
            fileInput.classList.add('is-invalid');
            previewImg.classList.add('d-none');
        }
    });
});
```

---

## 5. API Endpoints for Image Processing

```python
# api/views/image_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from detection.services.image_processing_service import ImageProcessingService, WindowLevelService
from detection.models import XRayImage


class ImageRotateView(APIView):
    """Rotate X-ray image."""
    permission_classes = [IsAuthenticated]

    def post(self, request, xray_id):
        angle = request.data.get('angle', 90)

        try:
            xray = XRayImage.objects.get(id=xray_id)
            rotated_path = ImageProcessingService.rotate_image(
                xray.original_image.path,
                int(angle)
            )
            return Response({'success': True, 'path': rotated_path})
        except Exception as e:
            return Response({'error': str(e)}, status=400)


class ImagePresetView(APIView):
    """Apply window/level preset to X-ray."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        preset = request.query_params.get('preset', 'default')
        image_id = request.query_params.get('image_id')

        try:
            xray = XRayImage.objects.get(id=image_id)
            processed = WindowLevelService.apply_preset(
                xray.original_image.path,
                preset
            )

            # Save and return URL
            # (implementation details omitted for brevity)
            return Response({'image_url': processed_url})
        except Exception as e:
            return Response({'error': str(e)}, status=400)


class ImageHistogramView(APIView):
    """Get image histogram data for visualization."""
    permission_classes = [IsAuthenticated]

    def get(self, request, xray_id):
        try:
            xray = XRayImage.objects.get(id=xray_id)
            histogram = ImageProcessingService.get_image_histogram(
                xray.original_image.path
            )
            return Response(histogram)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
```

---

## 6. Image Processing Checklist

### When Implementing Image Upload:
- [ ] Server-side validation with `ImageValidator.validate_file()`
- [ ] Client-side validation with `ImageUploadValidator` class
- [ ] File type check (extension + MIME type + magic bytes)
- [ ] File size limit enforced (default: 10MB)
- [ ] Image dimensions validated (min 224x224)
- [ ] Quality assessment with warnings (blur, aspect ratio)
- [ ] EXIF orientation auto-correction
- [ ] Preview displayed before upload
- [ ] Progress indicator during upload

### When Implementing Image Processing:
- [ ] Use `ImageProcessingService.preprocess_xray()` pipeline
- [ ] CLAHE enhancement applied for X-rays
- [ ] Thumbnails generated for list views
- [ ] Original image preserved (never overwrite)
- [ ] Processed images stored in separate directory
- [ ] Processing errors handled gracefully

### When Implementing Image Display:
- [ ] Use `image_viewer.html` component for detailed view
- [ ] Zoom controls (buttons + mousewheel)
- [ ] Pan/drag for zoomed images
- [ ] Rotation controls
- [ ] Fullscreen capability
- [ ] Side-by-side comparison (original vs processed)
- [ ] Lazy loading for image lists
- [ ] Responsive images (`img-fluid` class)
- [ ] Dark background for medical images
- [ ] Metadata display (resolution, size, date)

### When Implementing Medical Imaging Features:
- [ ] Window/Level adjustment available
- [ ] Presets for different views (lung, bone, default)
- [ ] Histogram display option
- [ ] DICOM support (if applicable)

---

## 7. Anti-Patterns to Avoid

```python
# ❌ BAD: No validation
def upload_xray(request):
    file = request.FILES['image']
    xray = XRayImage.objects.create(original_image=file)  # No validation!

# ✅ GOOD: Comprehensive validation
def upload_xray(request):
    file = request.FILES['image']
    ImageValidator.validate_file(file)  # Validate first
    xray = XRayImage.objects.create(original_image=file)

# ❌ BAD: Overwriting original image
def preprocess(xray):
    processed = apply_clahe(xray.original_image.path)
    cv2.imwrite(xray.original_image.path, processed)  # Destroys original!

# ✅ GOOD: Preserve original, save processed separately
def preprocess(xray):
    processed_path = apply_clahe(xray.original_image.path)  # Saves to new file
    xray.processed_image = processed_path
    xray.save()

# ❌ BAD: No lazy loading for image lists
<img src="{{ xray.original_image.url }}">  <!-- Loads all images immediately -->

# ✅ GOOD: Lazy loading with thumbnails
<img src="{{ xray.thumbnail.url }}" loading="lazy" data-src="{{ xray.original_image.url }}">

# ❌ BAD: Fixed-size images
<img src="..." width="500" height="500">  <!-- Not responsive -->

# ✅ GOOD: Responsive images
<img src="..." class="img-fluid" alt="X-ray">  <!-- Scales with container -->
```

---

## Summary

This skill covers the complete image processing lifecycle:

1. **Validation**: Server-side and client-side validation with comprehensive checks
2. **Processing**: CLAHE, rotation, cropping, brightness/contrast, Window/Level
3. **Display**: Interactive viewer with zoom, pan, rotation, fullscreen, comparison
4. **Performance**: Thumbnails, lazy loading, caching
5. **Medical Standards**: Window/Level presets, DICOM support considerations

**Key Files:**
- `common/validators.py` - `ImageValidator` class
- `detection/services/image_processing_service.py` - `ImageProcessingService`, `WindowLevelService`
- `static/js/image_validation.js` - `ImageUploadValidator` class
- `templates/components/image_viewer.html` - `ImageViewer` component
