# detection/explainability.py
"""
Explainability Engine for COVID-19 Detection
🌟 SPOTLIGHT 2: Generates visual explanations using Grad-CAM

Provides interpretable AI by showing which regions of X-ray influenced the prediction
"""

import torch
import torch.nn.functional as F
import numpy as np
import cv2
from PIL import Image
from torchvision import transforms
import os
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Try to import pytorch_grad_cam, install if not available
try:
    from pytorch_grad_cam import GradCAM
    from pytorch_grad_cam.utils.image import show_cam_on_image
    from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget

    GRADCAM_AVAILABLE = True
except ImportError:
    logger.warning(
        "⚠️ pytorch-grad-cam not installed. Run: pip install pytorch-grad-cam"
    )
    GRADCAM_AVAILABLE = False


class ExplainabilityEngine:
    """
    🌟 SPOTLIGHT 2: Explainable AI Engine
    Generates visual explanations for model predictions using Grad-CAM
    """

    def __init__(self, model, device):
        """
        Initialize explainability engine

        Args:
            model: PyTorch model to explain
            device: torch.device (cuda or cpu)
        """
        self.model = model
        self.device = device
        self.model.eval()

        logger.info("🔍 Explainability Engine initialized")

    def _get_target_layer(self, model_name="crossvit"):
        """
        Get appropriate target layer for Grad-CAM based on architecture

        Args:
            model_name: str - model architecture name

        Returns:
            list of target layers for Grad-CAM
        """
        model_type = str(type(self.model).__name__).lower()

        # CrossViT: use last transformer block
        if "crossvit" in model_type or "crossvit" in model_name.lower():
            # For CrossViT, target the last cross-attention layer
            try:
                return [self.model.blocks[-1]]
            except:
                return [self.model.patch_embed]

        # ResNet: use last convolutional layer
        elif "resnet" in model_type:
            return [self.model.layer4[-1]]

        # DenseNet: use final dense block
        elif "densenet" in model_type:
            return [self.model.features[-1]]

        # EfficientNet: use last block
        elif "efficientnet" in model_type:
            return [self.model.blocks[-1]]

        # Vision Transformer: use last attention layer
        elif "vit" in model_type or "vision" in model_type:
            try:
                return [self.model.blocks[-1].norm1]
            except:
                return [self.model.blocks[-1]]

        # Swin Transformer: use last layer
        elif "swin" in model_type:
            try:
                return [self.model.layers[-1]]
            except:
                return [self.model.patch_embed]

        # Default fallback
        else:
            logger.warning(f"Unknown model type: {model_type}, using default layer")
            # Try to find the last convolutional or attention layer
            for name, module in reversed(list(self.model.named_modules())):
                if isinstance(module, (torch.nn.Conv2d, torch.nn.Linear)):
                    return [module]

            # Ultimate fallback
            return [list(self.model.children())[-1]]

    def generate_gradcam(
        self, image_path, target_class_idx, model_name="crossvit", save_path=None
    ):
        """
        Generate Grad-CAM heatmap visualization

        Args:
            image_path: str - path to X-ray image
            target_class_idx: int - index of target class
            model_name: str - model architecture name
            save_path: str - optional path to save visualization

        Returns:
            np.ndarray - Grad-CAM visualization (RGB image)
        """
        if not GRADCAM_AVAILABLE:
            logger.error("❌ pytorch-grad-cam not installed!")
            return None

        try:
            logger.info(f"🔍 Generating Grad-CAM for class index {target_class_idx}...")

            # Get target layer
            target_layers = self._get_target_layer(model_name)

            # Initialize Grad-CAM
            cam = GradCAM(model=self.model, target_layers=target_layers)

            # Load and preprocess image
            image = Image.open(image_path).convert("RGB")
            image_np = np.array(image) / 255.0  # Normalize to [0, 1]

            # Resize for visualization
            image_np_resized = cv2.resize(image_np, (224, 224))

            # Prepare input tensor
            transform = transforms.Compose(
                [
                    transforms.Resize((224, 224)),
                    transforms.ToTensor(),
                    transforms.Normalize(
                        mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                    ),
                ]
            )

            input_tensor = transform(image).unsqueeze(0).to(self.device)

            # Generate CAM
            targets = [ClassifierOutputTarget(target_class_idx)]
            grayscale_cam = cam(input_tensor=input_tensor, targets=targets)
            grayscale_cam = grayscale_cam[0, :]

            # Overlay CAM on image
            visualization = show_cam_on_image(
                image_np_resized, grayscale_cam, use_rgb=True
            )

            # Save if path provided
            if save_path:
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                cv2.imwrite(save_path, cv2.cvtColor(visualization, cv2.COLOR_RGB2BGR))
                logger.info(f"   ✅ Grad-CAM saved to: {save_path}")

            return visualization

        except Exception as e:
            logger.error(f"   ❌ Grad-CAM generation failed: {e}")
            return None

    def generate_dual_branch_visualization(self, image_path, save_dir=None):
        """
        CrossViT-specific: Visualize large and small branch processing
        Shows how CrossViT processes images at multiple scales

        Args:
            image_path: str - path to X-ray image
            save_dir: str - directory to save visualizations

        Returns:
            dict with 'large_branch' and 'small_branch' numpy arrays
        """
        try:
            logger.info("🔍 Generating dual-branch visualization for CrossViT...")

            # Load image
            image = Image.open(image_path).convert("RGB")
            image_np = np.array(image)

            # CrossViT processes at different scales
            # Large branch: 16x16 patches (coarser)
            large_scale = cv2.resize(image_np, (240, 240))

            # Small branch: 12x12 patches (finer)
            small_scale = cv2.resize(image_np, (240, 240))

            # Add visual indicators for patch sizes
            # This is a simplified visualization
            large_with_grid = self._add_patch_grid(large_scale, patch_size=16)
            small_with_grid = self._add_patch_grid(small_scale, patch_size=12)

            # Save if directory provided
            if save_dir:
                os.makedirs(save_dir, exist_ok=True)

                large_path = os.path.join(save_dir, "large_branch.jpg")
                small_path = os.path.join(save_dir, "small_branch.jpg")

                cv2.imwrite(
                    large_path, cv2.cvtColor(large_with_grid, cv2.COLOR_RGB2BGR)
                )
                cv2.imwrite(
                    small_path, cv2.cvtColor(small_with_grid, cv2.COLOR_RGB2BGR)
                )

                logger.info(f"   ✅ Dual-branch visualizations saved to: {save_dir}")

            return {
                "large_branch": large_with_grid,
                "small_branch": small_with_grid,
                "large_path": large_path if save_dir else None,
                "small_path": small_path if save_dir else None,
            }

        except Exception as e:
            logger.error(f"   ❌ Dual-branch visualization failed: {e}")
            return None

    def _add_patch_grid(self, image, patch_size=16):
        """
        Add grid overlay to show patch divisions

        Args:
            image: np.ndarray - input image
            patch_size: int - size of patches

        Returns:
            np.ndarray - image with grid overlay
        """
        image_with_grid = image.copy()
        h, w = image_with_grid.shape[:2]

        # Draw grid lines
        for i in range(0, h, patch_size):
            cv2.line(image_with_grid, (0, i), (w, i), (255, 255, 0), 1)
        for j in range(0, w, patch_size):
            cv2.line(image_with_grid, (j, 0), (j, h), (255, 255, 0), 1)

        return image_with_grid

    def generate_comparison_visualization(
        self, image_path, predictions, save_path=None
    ):
        """
        Create a comprehensive visualization showing original image,
        processed image, and predictions

        Args:
            image_path: str - path to X-ray
            predictions: dict - prediction results
            save_path: str - path to save visualization

        Returns:
            np.ndarray - combined visualization
        """
        try:
            # Load original image
            original = cv2.imread(image_path)
            original = cv2.resize(original, (300, 300))

            # Create text overlay with predictions
            prediction_text = f"Prediction: {predictions.get('prediction', 'N/A')}"
            confidence_text = f"Confidence: {predictions.get('confidence', 0):.2f}%"

            # Add text to image
            cv2.putText(
                original,
                prediction_text,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )
            cv2.putText(
                original,
                confidence_text,
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

            if save_path:
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                cv2.imwrite(save_path, original)
                logger.info(f"   ✅ Comparison visualization saved: {save_path}")

            return original

        except Exception as e:
            logger.error(f"   ❌ Comparison visualization failed: {e}")
            return None


def generate_explainability_report(
    model, device, image_path, prediction_result, model_name="crossvit"
):
    """
    Generate complete explainability report with all visualizations

    Args:
        model: PyTorch model
        device: torch.device
        image_path: str - path to X-ray
        prediction_result: dict - prediction results
        model_name: str - model architecture

    Returns:
        dict containing paths to all generated visualizations
    """
    try:
        # Initialize engine
        engine = ExplainabilityEngine(model, device)

        # Get predicted class index
        class_names = ["COVID", "Lung Opacity", "Normal", "Viral Pneumonia"]
        predicted_class = prediction_result.get("prediction", "Normal")
        class_idx = (
            class_names.index(predicted_class) if predicted_class in class_names else 2
        )

        # Generate save directory
        save_dir = os.path.join(
            settings.MEDIA_ROOT,
            "explainability",
            os.path.basename(image_path).split(".")[0],
        )
        os.makedirs(save_dir, exist_ok=True)

        # Generate Grad-CAM
        gradcam_path = os.path.join(save_dir, "gradcam.jpg")
        gradcam_viz = engine.generate_gradcam(
            image_path, class_idx, model_name, gradcam_path
        )

        # Generate dual-branch visualization (CrossViT specific)
        dual_branch = None
        if "crossvit" in model_name.lower():
            dual_branch = engine.generate_dual_branch_visualization(
                image_path, save_dir
            )

        # Generate comparison
        comparison_path = os.path.join(save_dir, "comparison.jpg")
        comparison = engine.generate_comparison_visualization(
            image_path, prediction_result, comparison_path
        )

        return {
            "gradcam_path": gradcam_path if gradcam_viz is not None else None,
            "large_branch_path": dual_branch["large_path"] if dual_branch else None,
            "small_branch_path": dual_branch["small_path"] if dual_branch else None,
            "comparison_path": comparison_path if comparison is not None else None,
            "save_directory": save_dir,
        }

    except Exception as e:
        logger.error(f"❌ Explainability report generation failed: {e}")
        return {}
