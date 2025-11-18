# COVID-19 Detection Web Application

Final Year Project - Bachelor of Data Science
**Student:** Tan Ming Kai (24PMR12003)
**Supervisor:** Angkay A/P Subramaniam
**Institution:** TAR UMT

## Project Overview

This Django web application provides a comprehensive COVID-19 detection system using chest X-ray analysis with multiple AI models.

### Key Features

1. **Spotlight Feature #1: Multi-Model Comparison**
   - Analyzes X-rays using 6 state-of-the-art models:
     - CrossViT-Tiny (Dual-Branch)
     - ResNet-50
     - DenseNet-121
     - EfficientNet-B0
     - ViT-Base/16
     - Swin-Tiny
   - Provides consensus prediction with confidence scores
   - Shows model agreement statistics

2. **Spotlight Feature #2: Explainable AI**
   - Grad-CAM heatmaps showing important image regions
   - CrossViT dual-branch attention visualization
   - Helps doctors understand AI decisions

3. **Role-Based Access Control**
   - **Admin:** Full system management via Django admin panel
   - **Doctor:** Upload X-rays, view predictions, add clinical notes
   - **Patient:** View own results and history

4. **Comprehensive Admin Panel**
   - User management
   - Prediction review and validation
   - Beautiful data visualization
   - Filter, search, and export capabilities

## Current Status

✅ **COMPLETED:**
- Django project structure
- Database models and migrations
- URL routing configuration
- Views and forms
- HTML templates (Bootstrap 5)
- Admin panel configuration
- Authentication system
- Role-based dashboards

⚠️ **USING STUB VERSION:**
The application currently uses **stub/mock versions** of the ML components to allow the web interface to run without PyTorch and model weights. The stub versions generate random predictions for demonstration purposes.

## Installation

### 1. Prerequisites
- Python 3.8 or higher
- Virtual environment (recommended)
- For production: PyTorch with CUDA support (if using GPU)

### 2. Setup

```bash
# Clone the repository
cd fyp-webapp

# Activate virtual environment
source venv/bin/activate

# The basic dependencies are already installed:
# - Django 4.2.7
# - django-crispy-forms
# - crispy-bootstrap5
# - Pillow
# - python-decouple

# Apply migrations (already done)
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### 3. Access the Application

- **Main site:** http://localhost:8000/
- **Admin panel:** http://localhost:8000/admin/
- **Login:** http://localhost:8000/accounts/login/
- **Register:** http://localhost:8000/register/

## Adding Real ML Models

To enable actual COVID-19 detection (not stub predictions), follow these steps:

### 1. Install PyTorch and Dependencies

```bash
# For GPU (RTX 4060 with CUDA 11.8)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CPU only
pip install torch torchvision torchaudio

# Install ML dependencies
pip install timm pytorch-grad-cam opencv-python albumentations scikit-image numpy scipy pandas matplotlib seaborn
```

### 2. Add Model Weights

Place your trained `.pth` model files in `static/ml_models/`:
- `crossvit_tiny.pth`
- `resnet50.pth`
- `densenet121.pth`
- `efficientnet_b0.pth`
- `vit_base.pth`
- `swin_tiny.pth`

### 3. Switch to Real ML Engine

In `detection/views.py`, change the imports:

```python
# Change FROM:
from .ml_engine_stub import model_ensemble
from .preprocessing_stub import apply_clahe
from .explainability_stub import generate_explainability_report

# TO:
from .ml_engine import model_ensemble
from .preprocessing import apply_clahe
from .explainability import generate_explainability_report
```

### 4. Verify CUDA Availability

```python
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}')"
```

## Project Structure

```
fyp-webapp/
├── config/                 # Main Django configuration
│   ├── settings.py        # Settings with ML configurations
│   └── urls.py            # Main URL routing
├── detection/             # Main application
│   ├── models.py          # Database models
│   ├── views.py           # View logic
│   ├── forms.py           # Forms
│   ├── admin.py           # Admin configuration
│   ├── ml_engine.py       # Real ML engine (needs PyTorch)
│   ├── ml_engine_stub.py  # Stub version (currently active)
│   ├── preprocessing.py   # CLAHE preprocessing (needs OpenCV)
│   ├── preprocessing_stub.py  # Stub version (currently active)
│   ├── explainability.py  # Grad-CAM (needs PyTorch)
│   ├── explainability_stub.py # Stub version (currently active)
│   ├── urls.py            # App URLs
│   └── templates/         # HTML templates
├── templates/             # Global templates
│   ├── base.html          # Bootstrap 5 base template
│   └── home.html          # Landing page
├── static/                # Static files
│   ├── ml_models/         # Model weights (.pth files)
│   ├── css/               # Custom CSS
│   └── js/                # JavaScript
├── media/                 # Uploaded files
│   ├── xrays/             # X-ray images
│   ├── heatmaps/          # Grad-CAM visualizations
│   └── attention/         # Attention maps
├── logs/                  # Application logs
└── db.sqlite3            # SQLite database
```

## User Roles

### Admin
- Access admin panel: http://localhost:8000/admin/
- Manage users, view all predictions
- System configuration

### Doctor
- Upload X-ray images
- View multi-model predictions
- Add clinical notes and validate predictions
- Access all patient results

### Patient
- View own X-ray results
- See prediction history
- Access explainability visualizations

## Key URLs

| URL | Description | Access |
|-----|-------------|--------|
| `/` | Landing page | All |
| `/admin/` | Admin panel | Admin only |
| `/register/` | User registration | All |
| `/accounts/login/` | Login | All |
| `/detection/upload/` | Upload X-ray | Doctors |
| `/detection/results/<id>/` | View results | Doctor/Patient |
| `/detection/explain/<id>/` | Explainability | Doctor/Patient |
| `/detection/doctor/dashboard/` | Doctor dashboard | Doctors |
| `/detection/patient/dashboard/` | Patient dashboard | Patients |
| `/detection/history/` | Prediction history | Doctor/Patient |

## Development

### Running Tests
```bash
python manage.py test
```

### Collecting Static Files
```bash
python manage.py collectstatic
```

### Creating Test Users

Via Django shell:
```python
python manage.py shell

from django.contrib.auth.models import User
from detection.models import UserProfile, Patient

# Create doctor
doctor = User.objects.create_user(username='doctor1', password='test123', email='doctor@test.com')
doctor.profile.role = 'doctor'
doctor.profile.save()

# Create patient
patient = User.objects.create_user(username='patient1', password='test123', email='patient@test.com')
patient.profile.role = 'patient'
patient.profile.save()
Patient.objects.create(user=patient, age=35, gender='M')
```

## Documentation References

See the `files/` directory for:
- `INDEX.md` - Complete project overview
- `SETUP_INSTRUCTIONS.md` - Detailed setup guide
- `QUICK_REFERENCE.md` - Commands and troubleshooting

## Important Notes

1. **Security:** Change `SECRET_KEY` in production
2. **Database:** SQLite is for development only. Use PostgreSQL for production.
3. **Debug Mode:** Set `DEBUG=False` in production
4. **Static Files:** Use proper web server (Nginx/Apache) in production
5. **HTTPS:** Enable SSL/TLS in production

## Memory Optimization

The ML engine is optimized for RTX 4060 8GB VRAM:
- Models loaded sequentially
- Mixed precision training
- Batch size = 1
- CUDA cache clearing after each prediction

## Next Steps for Deployment

1. Install PyTorch and ML dependencies
2. Add trained model weights
3. Switch to real ML engine (modify imports)
4. Test predictions with real X-rays
5. Configure PostgreSQL database
6. Set up Nginx/Gunicorn
7. Enable HTTPS
8. Deploy to production server

## Support

For questions or issues, refer to:
- Django documentation: https://docs.djangoproject.com/
- Project documentation in `files/` directory

## License

Academic project for TAR UMT Final Year Project

---

**Version:** 1.0.0
**Last Updated:** 2025-11-18
