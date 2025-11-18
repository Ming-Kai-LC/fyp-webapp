"""
Celery Configuration for COVID-19 Detection System
Handles async batch processing, notifications, and scheduled tasks
"""

import os
from celery import Celery
from django.conf import settings

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create Celery app
app = Celery('covid_detection')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

# Optional: Configure Celery Beat for scheduled tasks
app.conf.beat_schedule = {
    'cleanup-old-batch-jobs': {
        'task': 'detection.tasks.cleanup_old_batch_jobs',
        'schedule': 86400.0,  # Run daily
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery"""
    print(f'Request: {self.request!r}')
