# detection/ml_engine.py
"""
COVID-19 Detection ML Engine
Manages all 6 AI models with memory optimization for RTX 4060 8GB VRAM

🌟 SPOTLIGHT 1: Multi-Model Comparison
- CrossViT (your model)
- ResNet-50 (baseline 1)
- DenseNet-121 (baseline 2)
- EfficientNet-B0 (baseline 3)
- ViT-Base (baseline 4)
- Swin-Tiny (baseline 5)
"""

import torch
import torch.nn.functional as F
import timm
from PIL import Image
import numpy as np
import time
from torchvision import transforms
from django.conf import settings
import os
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class ModelEnsemble:
    """
    Manages all 6 AI models for COVID-19 detection
    Loads models sequentially to save VRAM (RTX 4060 8GB constraint)
    """
    
    # COVID-19 Radiography Database classes
    CLASS_NAMES = ['COVID', 'Lung Opacity', 'Normal', 'Viral Pneumonia']
    
    def __init__(self):
        """Initialize model ensemble"""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"🔥 ML Engine initialized on device: {self.device}")
        
        if torch.cuda.is_available():
            logger.info(f"   GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
        
        # Model configurations
        self.model_configs = {
            'crossvit': {
                'name': 'crossvit_tiny_240',
                'input_size': 240,
                'weights': 'crossvit_tiny.pth',
                'description': 'CrossViT-Tiny (Dual-branch multi-scale)'
            },
            'resnet50': {
                'name': 'resnet50',
                'input_size': 224,
                'weights': 'resnet50.pth',
                'description': 'ResNet-50 (Deep residual CNN)'
            },
            'densenet121': {
                'name': 'densenet121',
                'input_size': 224,
                'weights': 'densenet121.pth',
                'description': 'DenseNet-121 (Dense connections)'
            },
            'efficientnet': {
                'name': 'efficientnet_b0',
                'input_size': 224,
                'weights': 'efficientnet_b0.pth',
                'description': 'EfficientNet-B0 (Compound scaling)'
            },
            'vit': {
                'name': 'vit_base_patch16_224',
                'input_size': 224,
                'weights': 'vit_base.pth',
                'description': 'ViT-Base (Pure transformer)'
            },
            'swin': {
                'name': 'swin_tiny_patch4_window7_224',
                'input_size': 224,
                'weights': 'swin_tiny.pth',
                'description': 'Swin-Tiny (Shifted window transformer)'
            }
        }
        
        # Current loaded model (we load one at a time to save VRAM)
        self.current_model = None
        self.current_model_name = None
        
        # Image preprocessing transforms
        self.normalize = transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    
    def _get_weights_path(self, weights_filename):
        """Get full path to model weights file"""
        # Try multiple possible locations
        possible_paths = [
            os.path.join(settings.BASE_DIR, 'static', 'ml_models', weights_filename),
            os.path.join(settings.STATIC_ROOT, 'ml_models', weights_filename) if settings.STATIC_ROOT else None,
            os.path.join(settings.BASE_DIR, 'ml_models', weights_filename),
        ]
        
        for path in possible_paths:
            if path and os.path.exists(path):
                return path
        
        logger.warning(f"⚠️ Weights file not found: {weights_filename}")
        return None
    
    def _load_model(self, model_name):
        """
        Load a specific model (unload previous model to save VRAM)
        Args:
            model_name: str - one of ['crossvit', 'resnet50', 'densenet121', 
                                      'efficientnet', 'vit', 'swin']
        """
        if self.current_model_name == model_name:
            logger.info(f"   Model {model_name} already loaded, reusing...")
            return  # Already loaded
        
        # Unload previous model to free VRAM
        if self.current_model is not None:
            logger.info(f"   Unloading {self.current_model_name}...")
            del self.current_model
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        
        config = self.model_configs[model_name]
        logger.info(f"   Loading {model_name}: {config['description']}")
        
        try:
            # Create model architecture
            model = timm.create_model(
                config['name'],
                pretrained=False,  # We'll load our trained weights
                num_classes=4       # 4 classes for COVID-19 detection
            )
            
            # Load trained weights if available
            weights_path = self._get_weights_path(config['weights'])
            if weights_path:
                try:
                    state_dict = torch.load(weights_path, map_location=self.device)
                    model.load_state_dict(state_dict)
                    logger.info(f"   ✅ Loaded trained weights from {weights_path}")
                except Exception as e:
                    logger.warning(f"   ⚠️ Could not load weights: {e}")
                    logger.warning(f"   Using pretrained ImageNet initialization instead")
                    # Fallback: use ImageNet pretrained
                    model = timm.create_model(
                        config['name'],
                        pretrained=True,
                        num_classes=4
                    )
            else:
                logger.warning(f"   ⚠️ No trained weights found for {model_name}")
                logger.warning(f"   Using pretrained ImageNet initialization")
                # Use ImageNet pretrained as fallback
                model = timm.create_model(
                    config['name'],
                    pretrained=True,
                    num_classes=4
                )
            
            # Move to device and set to evaluation mode
            model.to(self.device)
            model.eval()
            
            self.current_model = model
            self.current_model_name = model_name
            
            logger.info(f"   ✅ {model_name} loaded successfully")
            
        except Exception as e:
            logger.error(f"   ❌ Error loading {model_name}: {e}")
            raise
    
    def _preprocess_image(self, image_path, target_size):
        """
        Preprocess image for model input
        Args:
            image_path: str or Path - path to image file
            target_size: int - target image size (224 or 240)
        Returns:
            torch.Tensor - preprocessed image tensor [1, 3, H, W]
        """
        # Load image
        image = Image.open(image_path).convert('RGB')
        
        # Resize and convert to tensor
        transform = transforms.Compose([
            transforms.Resize((target_size, target_size)),
            transforms.ToTensor(),
            self.normalize
        ])
        
        image_tensor = transform(image).unsqueeze(0)  # Add batch dimension
        return image_tensor.to(self.device)
    
    def predict_single_model(self, model_name, image_path):
        """
        Get prediction from a single model
        Args:
            model_name: str - model identifier
            image_path: str - path to X-ray image
        Returns:
            dict with 'prediction', 'confidence', 'all_probabilities'
        """
        logger.info(f"🔍 Running inference with {model_name}...")
        
        # Load model
        self._load_model(model_name)
        config = self.model_configs[model_name]
        
        # Preprocess image
        image_tensor = self._preprocess_image(image_path, config['input_size'])
        
        # Run inference
        start_time = time.time()
        with torch.no_grad():
            output = self.current_model(image_tensor)
            probabilities = F.softmax(output, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
        
        inference_time = time.time() - start_time
        
        result = {
            'prediction': self.CLASS_NAMES[predicted.item()],
            'confidence': confidence.item() * 100,
            'all_probabilities': {
                self.CLASS_NAMES[i]: probabilities[0][i].item() * 100 
                for i in range(len(self.CLASS_NAMES))
            },
            'inference_time': inference_time
        }
        
        logger.info(f"   ✅ {model_name}: {result['prediction']} ({result['confidence']:.2f}%) in {inference_time:.3f}s")
        
        return result
    
    def predict_all_models(self, image_path):
        """
        🌟 SPOTLIGHT 1: Multi-Model Comparison
        Get predictions from all 6 models for comparison
        
        Args:
            image_path: str - path to X-ray image
            
        Returns:
            dict containing:
                - individual_results: dict of results for each model
                - consensus_diagnosis: most common prediction
                - best_model: model with highest confidence
                - best_confidence: highest confidence score
                - inference_time: total time for all models
                - model_agreement: number of models agreeing
        """
        logger.info("=" * 80)
        logger.info("🚀 Starting multi-model prediction ensemble...")
        logger.info(f"   Image: {os.path.basename(image_path)}")
        logger.info("=" * 80)
        
        start_time = time.time()
        results = {}
        
        # Run inference with each model
        for model_name in self.model_configs.keys():
            try:
                results[model_name] = self.predict_single_model(model_name, image_path)
            except Exception as e:
                logger.error(f"   ❌ Error with {model_name}: {e}")
                # Use a fallback result
                results[model_name] = {
                    'prediction': 'Normal',
                    'confidence': 0.0,
                    'all_probabilities': {cls: 0.0 for cls in self.CLASS_NAMES},
                    'inference_time': 0.0,
                    'error': str(e)
                }
        
        # Calculate consensus diagnosis (majority vote)
        predictions_list = [results[m]['prediction'] for m in results]
        prediction_counts = Counter(predictions_list)
        consensus = prediction_counts.most_common(1)[0][0]
        
        # Find model with highest confidence
        best_model = max(results.items(), key=lambda x: x[1]['confidence'])
        
        # Calculate total inference time
        total_time = time.time() - start_time
        
        # Calculate model agreement
        agreement_count = predictions_list.count(consensus)
        
        summary = {
            'individual_results': results,
            'consensus_diagnosis': consensus,
            'best_model': best_model[0],
            'best_confidence': best_model[1]['confidence'],
            'inference_time': total_time,
            'model_agreement': agreement_count,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        logger.info("=" * 80)
        logger.info("📊 ENSEMBLE RESULTS SUMMARY:")
        logger.info(f"   Consensus Diagnosis: {consensus}")
        logger.info(f"   Model Agreement: {agreement_count}/6 models")
        logger.info(f"   Best Model: {best_model[0]} ({best_model[1]['confidence']:.2f}%)")
        logger.info(f"   Total Inference Time: {total_time:.3f}s")
        logger.info("=" * 80)
        
        return summary
    
    def get_model_info(self, model_name):
        """Get information about a specific model"""
        if model_name in self.model_configs:
            config = self.model_configs[model_name]
            weights_path = self._get_weights_path(config['weights'])
            return {
                'name': model_name,
                'architecture': config['name'],
                'description': config['description'],
                'input_size': config['input_size'],
                'weights_available': weights_path is not None,
                'weights_path': weights_path
            }
        return None
    
    def get_all_models_info(self):
        """Get information about all models"""
        return {
            model_name: self.get_model_info(model_name)
            for model_name in self.model_configs.keys()
        }


# Global singleton instance
# This is loaded once when Django starts
try:
    model_ensemble = ModelEnsemble()
    logger.info("✅ Global ModelEnsemble initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize ModelEnsemble: {e}")
    model_ensemble = None
