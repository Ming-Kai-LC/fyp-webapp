# detection/ml_engine_stub.py
"""
STUB VERSION - ML Engine for COVID-19 Detection
This is a placeholder to allow the Django app to run without PyTorch installed.
Replace this with the real ml_engine.py when PyTorch and model weights are available.
"""

import logging
import random
import time

logger = logging.getLogger(__name__)


class ModelEnsemble:
    """
    STUB: Manages all 6 AI models for COVID-19 detection
    This is a mock version for testing the web interface without GPU/PyTorch
    """

    CLASS_NAMES = ["COVID", "Lung Opacity", "Normal", "Viral Pneumonia"]

    def __init__(self):
        """Initialize stub model ensemble"""
        logger.warning("⚠️  Using STUB ML Engine - Install PyTorch and model weights for real predictions")

    def predict_all_models(self, image_path):
        """
        STUB: Generate mock predictions for all 6 models
        Returns dictionary with all model predictions
        """
        logger.info(f"STUB: Generating mock predictions for {image_path}")

        # Simulate inference time
        time.sleep(0.5)

        # Generate random but consistent mock predictions
        random.seed(hash(image_path) % 1000)

        all_predictions = {}

        # Mock CrossViT prediction
        all_predictions['crossvit'] = {
            'class': random.choice(self.CLASS_NAMES),
            'confidence': random.uniform(85, 98),
            'probabilities': [random.random() for _ in range(4)]
        }

        # Mock baseline models
        for model in ['resnet50', 'densenet121', 'efficientnet', 'vit', 'swin']:
            all_predictions[model] = {
                'class': random.choice(self.CLASS_NAMES),
                'confidence': random.uniform(75, 95),
                'probabilities': [random.random() for _ in range(4)]
            }

        # Calculate consensus
        predictions = [p['class'] for p in all_predictions.values()]
        consensus_class = max(set(predictions), key=predictions.count)
        consensus_confidence = sum(p['confidence'] for p in all_predictions.values()) / len(all_predictions)

        all_predictions['consensus'] = {
            'class': consensus_class,
            'confidence': consensus_confidence,
            'model_agreement': predictions.count(consensus_class)
        }

        all_predictions['inference_time'] = 0.5

        return all_predictions

    def get_all_models_info(self):
        """STUB: Return model information"""
        return {
            'crossvit': 'CrossViT-Tiny (STUB)',
            'resnet50': 'ResNet-50 (STUB)',
            'densenet121': 'DenseNet-121 (STUB)',
            'efficientnet': 'EfficientNet-B0 (STUB)',
            'vit': 'ViT-Base (STUB)',
            'swin': 'Swin-Tiny (STUB)',
        }


# Create global instance
model_ensemble = ModelEnsemble()
