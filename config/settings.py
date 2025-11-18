# config/settings.py
"""
Django Settings for COVID-19 Detection System
CRITICAL configurations for ML models, media files, and security
"""

import os
from pathlib import Path

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key secret in production!
SECRET_KEY = "django-insecure-CHANGE-THIS-IN-PRODUCTION-xyz123abc456"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "crispy_forms",
    "crispy_bootstrap5",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_yasg",
    "corsheaders",
    "django_celery_results",
    "django_celery_beat",
    # Your apps
    "accounts",
    "detection",
    "dashboards",
    "medical_records",
    "reporting",
    "audit",
    "notifications",
    "appointments",
    "analytics",
    "api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # Add CORS support
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "audit.middleware.AuditMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",  # For media files
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# SQLite for development (easy setup, no installation required)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# For production, you can use PostgreSQL:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'covid_detection_db',
#         'USER': 'your_username',
#         'PASSWORD': 'your_password',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kuala_Lumpur"  # Malaysian timezone
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]


# Media files (Uploaded X-rays, predictions, heatmaps)
# 🔥 CRITICAL: This is where all uploaded X-rays and generated visualizations are stored
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Ensure media directories exist
os.makedirs(MEDIA_ROOT / "xrays" / "original", exist_ok=True)
os.makedirs(MEDIA_ROOT / "xrays" / "processed", exist_ok=True)
os.makedirs(MEDIA_ROOT / "heatmaps", exist_ok=True)
os.makedirs(MEDIA_ROOT / "attention" / "large", exist_ok=True)
os.makedirs(MEDIA_ROOT / "attention" / "small", exist_ok=True)
os.makedirs(MEDIA_ROOT / "medical_records" / "documents", exist_ok=True)
os.makedirs(MEDIA_ROOT / "medical_records" / "vaccination_certificates", exist_ok=True)
os.makedirs(MEDIA_ROOT / "reports" / "pdf", exist_ok=True)
os.makedirs(MEDIA_ROOT / "reports" / "batch", exist_ok=True)
os.makedirs(MEDIA_ROOT / "signatures", exist_ok=True)
os.makedirs(MEDIA_ROOT / "compliance_reports", exist_ok=True)
os.makedirs(MEDIA_ROOT / "analytics" / "exports", exist_ok=True)


# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Authentication URLs
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
LOGIN_URL = "/accounts/login/"


# Crispy Forms (for beautiful forms with Bootstrap 5)
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"


# File Upload Settings
# Maximum upload size: 10MB (adjust based on your X-ray image sizes)
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB in bytes
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB in bytes

# Allowed image formats
ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".dcm"]


# Logging Configuration
# 🔥 CRITICAL: This helps you debug issues
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "detection": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# Create logs directory
os.makedirs(BASE_DIR / "logs", exist_ok=True)


# ===========================================================================
# 🔥 ML MODEL SETTINGS (Placeholder - PyTorch not installed yet)
# ===========================================================================

# Model weights directory
MODEL_WEIGHTS_DIR = BASE_DIR / "static" / "ml_models"
os.makedirs(MODEL_WEIGHTS_DIR, exist_ok=True)

# Batch size for inference (adjusted for RTX 4060 8GB)
INFERENCE_BATCH_SIZE = 1  # Process one image at a time to save VRAM

# Enable mixed precision for memory efficiency
USE_MIXED_PRECISION = True

# Number of workers for data loading (0 for Windows, 2-4 for Linux)
NUM_WORKERS = 0 if os.name == "nt" else 2


# ===========================================================================
# SECURITY SETTINGS (FOR PRODUCTION)
# ===========================================================================

# SECURITY WARNING: Update these for production!
if not DEBUG:
    # HTTPS settings
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # HSTS settings
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Content Security Policy
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = "DENY"


# ===========================================================================
# CUSTOM SETTINGS FOR YOUR FYP
# ===========================================================================

# Project metadata
PROJECT_NAME = "COVID-19 Detection using CrossViT"
PROJECT_VERSION = "1.0.0"
STUDENT_NAME = "Tan Ming Kai"
STUDENT_ID = "24PMR12003"
SUPERVISOR = "Angkay A/P Subramaniam"
UNIVERSITY = "TAR UMT"

# Model names for display
MODEL_DISPLAY_NAMES = {
    "crossvit": "CrossViT-Tiny (Dual-Branch)",
    "resnet50": "ResNet-50",
    "densenet121": "DenseNet-121",
    "efficientnet": "EfficientNet-B0",
    "vit": "ViT-Base/16",
    "swin": "Swin-Tiny",
}

# Class names
COVID_CLASSES = ["COVID", "Lung Opacity", "Normal", "Viral Pneumonia"]

# Feature flags
ENABLE_EXPLAINABILITY = True  # Spotlight 2
ENABLE_MULTI_MODEL_COMPARISON = True  # Spotlight 1
ENABLE_CLAHE_PREPROCESSING = True

# ===========================================================================
# REPORTING MODULE SETTINGS
# ===========================================================================

# Report settings
SITE_URL = os.environ.get('SITE_URL', 'http://localhost:8000')  # Change in production
REPORT_LOGO_PATH = BASE_DIR / 'static' / 'images' / 'hospital_logo.png'
REPORT_SIGNATURE_PATH = MEDIA_ROOT / 'signatures'


# ===========================================================================
# NOTIFICATION SYSTEM SETTINGS
# ===========================================================================

# Email settings (for development - using console backend)
# For production, configure SMTP settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Development: prints to console
# For production with Gmail:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'your-email@gmail.com')
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'your-app-password')
DEFAULT_FROM_EMAIL = 'COVID-19 Detection System <noreply@covid19detection.local>'

# SMS settings (Twilio) - Optional
# TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
# TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
# TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '')


# ===========================================================================
# REST API SETTINGS
# ===========================================================================

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    },
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

# JWT settings
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React app
    "http://localhost:8080",  # Vue app
    "http://localhost:8081",  # Mobile dev server
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8081",
]

# For development: Allow all origins (NOT for production!)
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True

# CORS settings for credentials
CORS_ALLOW_CREDENTIALS = True

# Allow these headers in CORS requests
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Swagger/OpenAPI settings
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
}


# ===========================================================================
# CELERY SETTINGS (Async Task Processing)
# ===========================================================================

# Celery broker settings (using Redis)
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = 'django-db'  # Store results in Django database
CELERY_CACHE_BACKEND = 'django-cache'

# Celery task settings
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes max per task
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # Soft limit at 25 minutes

# Celery result backend settings
CELERY_RESULT_EXTENDED = True
CELERY_RESULT_EXPIRES = 3600  # Results expire after 1 hour

# Celery worker settings
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # Process one task at a time
CELERY_WORKER_MAX_TASKS_PER_CHILD = 50  # Restart worker after 50 tasks (memory cleanup)

# Celery beat schedule (for periodic tasks)
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'


print(
    f"""
{'='*80}
🎓 {PROJECT_NAME}
   Version: {PROJECT_VERSION}
   Student: {STUDENT_NAME} ({STUDENT_ID})
   Supervisor: {SUPERVISOR}
   Institution: {UNIVERSITY}

🔧 System Configuration:
   - Debug Mode: {DEBUG}
   - Database: {DATABASES['default']['ENGINE']}
   - Media Root: {MEDIA_ROOT}
   - Static Root: {STATIC_ROOT}
   - API Enabled: True (REST + JWT + Swagger)

✅ Ready to start!
{'='*80}
"""
)
