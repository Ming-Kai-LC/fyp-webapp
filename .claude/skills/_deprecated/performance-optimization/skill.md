---
name: Performance Optimization
description: Optimizes database queries, ML inference for RTX 4060 8GB VRAM, and caching strategies. Auto-applies N+1 prevention, select_related/prefetch_related, and memory management.
---

Ensures optimal performance for the COVID-19 Detection webapp, especially for ML inference on RTX 4060 8GB.

## Core Principles

1. **Measure First**: Profile before optimizing
2. **N+1 Queries**: Avoid with select_related/prefetch_related
3. **Caching**: Cache expensive operations
4. **Lazy Loading**: Load data only when needed
5. **Pagination**: Never load unlimited data
6. **Async Where Possible**: Use async for I/O operations

## Database Query Optimization

### Avoid N+1 Queries

```python
# ❌ BAD: N+1 query problem
predictions = Prediction.objects.all()
for pred in predictions:
    print(pred.xray.patient.user.username)  # New query each iteration!

# ✅ GOOD: Use select_related for ForeignKey/OneToOne
predictions = Prediction.objects.select_related(
    'xray__patient__user'
).all()
for pred in predictions:
    print(pred.xray.patient.user.username)  # No additional queries!

# ✅ GOOD: Use prefetch_related for ManyToMany/Reverse FK
patients = Patient.objects.prefetch_related('xrays__predictions').all()
for patient in patients:
    for xray in patient.xrays.all():  # Prefetched!
        for pred in xray.predictions.all():  # Prefetched!
            print(pred.final_diagnosis)
```

### Query Optimization Patterns

```python
# QuerySet Optimization
class PredictionListView(ListView):
    def get_queryset(self):
        return Prediction.objects.select_related(
            'xray__patient__user',
            'reviewed_by'
        ).prefetch_related(
            'xray__predictions'
        ).only(  # Load only needed fields
            'id',
            'final_diagnosis',
            'consensus_confidence',
            'created_at',
            'is_validated',
            'xray__patient__user__username'
        )

# Use .values() for large datasets (if you don't need model instances)
stats = Prediction.objects.values('final_diagnosis').annotate(
    count=Count('id'),
    avg_confidence=Avg('consensus_confidence')
)

# Use .exists() instead of .count() for boolean checks
# ❌ BAD
if Prediction.objects.filter(is_validated=False).count() > 0:
    pass

# ✅ GOOD
if Prediction.objects.filter(is_validated=False).exists():
    pass

# Use .iterator() for very large querysets (streaming)
for prediction in Prediction.objects.iterator(chunk_size=100):
    # Process one at a time without loading all into memory
    process_prediction(prediction)
```

### Database Indexes

```python
# models.py
class Prediction(models.Model):
    # ... fields ...

    class Meta:
        indexes = [
            # Index frequently filtered fields
            models.Index(fields=['-created_at']),
            models.Index(fields=['final_diagnosis']),
            models.Index(fields=['is_validated']),
            # Compound index for common filter combinations
            models.Index(fields=['final_diagnosis', '-created_at']),
            models.Index(fields=['is_validated', '-created_at']),
        ]
```

## Caching

### Django Cache Framework

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT': 300,  # 5 minutes default
    }
}

# For development (memory cache)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
```

### View-Level Caching

```python
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

# Cache view for 15 minutes
@method_decorator(cache_page(60 * 15), name='dispatch')
class PredictionStatsView(View):
    def get(self, request):
        # Expensive aggregation query
        stats = Prediction.objects.aggregate(
            total=Count('id'),
            covid_cases=Count('id', filter=Q(final_diagnosis='COVID')),
            avg_confidence=Avg('consensus_confidence')
        )
        return JsonResponse(stats)
```

### Low-Level Caching

```python
from django.core.cache import cache
from typing import Optional

class PredictionService:
    @staticmethod
    def get_statistics() -> dict:
        """Get prediction statistics with caching"""
        cache_key = 'prediction_statistics'
        stats = cache.get(cache_key)

        if stats is None:
            # Expensive query
            stats = Prediction.objects.aggregate(
                total=Count('id'),
                covid_cases=Count('id', filter=Q(final_diagnosis='COVID')),
                normal_cases=Count('id', filter=Q(final_diagnosis='Normal')),
                avg_confidence=Avg('consensus_confidence')
            )
            # Cache for 5 minutes
            cache.set(cache_key, stats, 300)

        return stats

    @staticmethod
    def invalidate_statistics_cache():
        """Call this when creating new predictions"""
        cache.delete('prediction_statistics')

# In save/create methods
def create_prediction(xray):
    prediction = Prediction.objects.create(...)
    PredictionService.invalidate_statistics_cache()  # Clear cache
    return prediction
```

### Template Fragment Caching

```django
{% load cache %}

{% cache 900 sidebar request.user.id %}
    <!-- Expensive sidebar rendering -->
    <div class="sidebar">
        {% for item in navigation_items %}
            ...
        {% endfor %}
    </div>
{% endcache %}
```

## ML Inference Optimization (RTX 4060 8GB)

### Memory Management

```python
# ml_engine.py
import torch
import gc

class ModelEnsemble:
    def predict_all_models(self, image_path: str) -> dict:
        """
        Predict with all models sequentially to manage VRAM.
        Optimized for RTX 4060 8GB.
        """
        results = {}

        # Load and predict one model at a time
        for model_name in self.model_names:
            # 1. Load model
            model = self.load_model(model_name)

            # 2. Run prediction
            with torch.no_grad():  # Disable gradient computation
                with torch.cuda.amp.autocast():  # Mixed precision
                    result = self.predict_single(model, image_path)

            results[model_name] = result

            # 3. Unload model and free VRAM
            del model
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()

        return results

    @torch.no_grad()  # Decorator for inference
    def predict_single(self, model, image_path: str):
        """Single model prediction"""
        # Process image
        image = self.preprocess(image_path)

        # Move to GPU
        image = image.to(self.device)

        # Predict
        output = model(image)

        # Move back to CPU immediately
        output = output.cpu()

        return self.postprocess(output)
```

### Batch Processing Optimization

```python
class PredictionService:
    @staticmethod
    def process_batch(xray_ids: list[int]) -> list[Prediction]:
        """
        Process multiple X-rays efficiently.
        For RTX 4060 8GB, batch_size=1 is safest.
        """
        predictions = []

        # Process in chunks to manage memory
        chunk_size = 1  # For 8GB VRAM
        for i in range(0, len(xray_ids), chunk_size):
            chunk = xray_ids[i:i + chunk_size]

            for xray_id in chunk:
                xray = XRayImage.objects.get(id=xray_id)
                prediction = PredictionService.create_prediction(xray)
                predictions.append(prediction)

                # Clear CUDA cache between predictions
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

        return predictions
```

### Image Preprocessing Optimization

```python
# preprocessing.py
from PIL import Image
import cv2
import numpy as np
from functools import lru_cache

@lru_cache(maxsize=100)  # Cache processed images
def apply_clahe(image_path: str, output_path: str = None) -> str:
    """
    Apply CLAHE with caching for frequently accessed images.

    Args:
        image_path: Path to input image
        output_path: Path to save processed image

    Returns:
        Path to processed image
    """
    # Load image
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Apply CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(img)

    # Save
    if output_path is None:
        output_path = image_path.replace('.jpg', '_clahe.jpg')

    cv2.imwrite(output_path, enhanced, [cv2.IMWRITE_JPEG_QUALITY, 95])

    return output_path

# Clear cache when needed
def clear_preprocessing_cache():
    apply_clahe.cache_clear()
```

## Static Files Optimization

### Compression

```python
# settings.py
# Use WhiteNoise for static file serving
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Must be after SecurityMiddleware
    # ... other middleware
]

# Enable compression and caching
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Aggressive caching
WHITENOISE_MAX_AGE = 31536000  # 1 year
```

### CDN for External Resources

```html
<!-- ✅ Use CDN for Bootstrap, jQuery, etc. -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

<!-- ✅ Add integrity checks -->
<link rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
      integrity="sha384-..."
      crossorigin="anonymous">
```

## Template Optimization

### Minimize Database Queries in Templates

```django
<!-- ❌ BAD: Query in template -->
{% for prediction in predictions %}
    <p>{{ prediction.xray.patient.user.username }}</p>  <!-- N+1 query! -->
{% endfor %}

<!-- ✅ GOOD: Prefetch in view -->
<!-- predictions = Prediction.objects.select_related('xray__patient__user') -->
{% for prediction in predictions %}
    <p>{{ prediction.xray.patient.user.username }}</p>  <!-- No query! -->
{% endfor %}
```

### Template Fragment Caching

```django
<!-- Cache expensive sidebar -->
{% load cache %}
{% cache 600 doctor_stats user.id %}
    <div class="stats">
        <h4>Statistics</h4>
        <p>Total Predictions: {{ total_predictions }}</p>
        <p>COVID Cases: {{ covid_cases }}</p>
    </div>
{% endcache %}
```

## Async Views (Django 4.2+)

```python
# views.py
from django.http import JsonResponse
from asgiref.sync import sync_to_async
import asyncio

class AsyncPredictionView(View):
    """Async view for long-running predictions"""

    async def post(self, request):
        xray_id = request.POST.get('xray_id')

        # Run ML prediction asynchronously
        prediction = await self.run_prediction_async(xray_id)

        return JsonResponse({
            'prediction_id': prediction.id,
            'status': 'completed'
        })

    @sync_to_async
    def run_prediction_async(self, xray_id: int):
        """Run prediction in async context"""
        xray = XRayImage.objects.get(id=xray_id)
        return PredictionService.create_prediction(xray)
```

## Pagination

```python
# views.py
from django.core.paginator import Paginator

class PredictionListView(ListView):
    model = Prediction
    paginate_by = 25  # Always paginate!
    template_name = 'detection/prediction_list.html'

    def get_queryset(self):
        return Prediction.objects.select_related(
            'xray__patient__user'
        ).order_by('-created_at')

# Template
```django
<!-- Pagination controls -->
<nav>
    <ul class="pagination">
        {% if page_obj.has_previous %}
            <li class="page-item">
                <a class="page-link" href="?page={{ page_obj.previous_page_number }}">Previous</a>
            </li>
        {% endif %}

        <li class="page-item active">
            <span class="page-link">Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}</span>
        </li>

        {% if page_obj.has_next %}
            <li class="page-item">
                <a class="page-link" href="?page={{ page_obj.next_page_number }}">Next</a>
            </li>
        {% endif %}
    </ul>
</nav>
```

## Performance Monitoring

### Django Debug Toolbar (Development Only)

```python
# settings.py (Development)
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']
```

### Custom Profiling

```python
# utils/profiling.py
import time
import functools
import logging

logger = logging.getLogger(__name__)

def profile_execution_time(func):
    """Decorator to profile function execution time"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time

        logger.info(
            f"{func.__name__} executed in {execution_time:.4f} seconds"
        )

        return result
    return wrapper

# Usage
@profile_execution_time
def create_prediction(xray):
    # ... prediction logic
    pass
```

## Performance Checklist

Before completing any feature:

- ✅ Database queries optimized (no N+1)
- ✅ Proper indexes on filtered/ordered fields
- ✅ select_related/prefetch_related used
- ✅ Expensive operations cached
- ✅ Large querysets paginated
- ✅ Static files compressed and cached
- ✅ ML inference uses CUDA efficiently
- ✅ Memory cleared after each prediction
- ✅ Images optimized (compressed, proper size)
- ✅ No database queries in templates
- ✅ Async used for I/O-bound operations
- ✅ Template fragments cached where appropriate

## Performance Targets

For RTX 4060 8GB system:

- **Single prediction**: < 10 seconds (all 6 models)
- **Page load**: < 2 seconds (with caching)
- **Database query**: < 100ms (with proper indexes)
- **VRAM usage**: < 8GB (sequential loading)
- **Pagination**: 25-50 items per page max

## Auto-Apply This Skill When:
- Creating new views or queries
- Adding ML inference
- Working with large datasets
- Implementing new features
- Optimizing existing code
- Preparing for production
