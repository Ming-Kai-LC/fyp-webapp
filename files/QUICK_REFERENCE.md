# 🚀 COVID-19 Detection System - Quick Reference Guide

## **📋 File Placement Guide**

After creating your Django project, place each artifact file in the correct location:

```
covid_detection_django/
├── manage.py                              # Django management script
├── requirements.txt                       # ✅ From artifact: requirements.txt
├── SETUP_INSTRUCTIONS.md                  # ✅ From artifact: SETUP_INSTRUCTIONS.md
│
├── config/                                # Main project folder
│   ├── __init__.py
│   ├── settings.py                        # ✅ From artifact: settings_config.py
│   ├── urls.py                            # ✅ From artifact: urls_config.py (main section)
│   └── wsgi.py
│
├── accounts/                              # User authentication app
│   ├── __init__.py
│   ├── models.py                          # (use default)
│   ├── views.py                           # (register view in detection_views.py)
│   ├── urls.py                            # (basic auth URLs)
│   └── templates/accounts/
│       ├── login.html                     # (create from Bootstrap template)
│       └── register.html                  # (create from Bootstrap template)
│
├── detection/                             # 🔥 MAIN APP - Your ML code
│   ├── __init__.py
│   ├── models.py                          # ✅ From artifact: detection_models.py
│   ├── views.py                           # ✅ From artifact: detection_views.py
│   ├── forms.py                           # ✅ From artifact: detection_forms.py
│   ├── admin.py                           # ✅ From artifact: detection_admin.py
│   ├── urls.py                            # ✅ From artifact: urls_config.py (detection section)
│   ├── ml_engine.py                       # ✅ From artifact: ml_engine.py
│   ├── preprocessing.py                   # ✅ From artifact: preprocessing.py
│   ├── explainability.py                  # ✅ From artifact: explainability.py
│   └── templates/detection/
│       ├── upload.html                    # (create HTML templates)
│       ├── results.html                   # (create HTML templates)
│       ├── explain.html                   # (create HTML templates)
│       └── history.html                   # (create HTML templates)
│
├── dashboards/                            # Dashboard app
│   ├── __init__.py
│   ├── views.py                           # (dashboard views in detection_views.py)
│   └── templates/dashboards/
│       ├── doctor_dashboard.html          # (create HTML templates)
│       └── patient_dashboard.html         # (create HTML templates)
│
├── templates/                             # Global templates
│   ├── base.html                          # (create Bootstrap base template)
│   └── home.html                          # (create landing page)
│
├── static/                                # Static files
│   ├── css/
│   │   └── custom.css                     # (your custom styles)
│   ├── js/
│   │   └── app.js                         # (JavaScript for charts)
│   └── ml_models/                         # 🔥 YOUR MODEL WEIGHTS HERE
│       ├── crossvit_tiny.pth
│       ├── resnet50.pth
│       ├── densenet121.pth
│       ├── efficientnet_b0.pth
│       ├── vit_base.pth
│       └── swin_tiny.pth
│
└── media/                                 # Uploaded files (auto-created)
    ├── xrays/
    ├── heatmaps/
    └── attention/
```

---

## **⚡ Quick Start Commands**

### **Initial Setup:**
```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create Django project
django-admin startproject config .
python manage.py startapp accounts
python manage.py startapp detection
python manage.py startapp dashboards

# 4. Copy all artifact files to correct locations (see above)

# 5. Copy model weights
cp /path/to/weights/*.pth static/ml_models/

# 6. Database setup
python manage.py makemigrations
python manage.py migrate

# 7. Create superuser (admin account)
python manage.py createsuperuser

# 8. Collect static files
python manage.py collectstatic --noinput

# 9. Run server
python manage.py runserver
```

### **Daily Development:**
```bash
# Activate virtual environment
source venv/bin/activate

# Run development server
python manage.py runserver

# Access:
# Main site: http://localhost:8000/
# Admin: http://localhost:8000/admin/
```

### **Database Commands:**
```bash
# Make migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (DANGER!)
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### **Testing:**
```bash
# Test if CUDA works
python -c "import torch; print(torch.cuda.is_available())"

# Test model loading
python manage.py shell
>>> from detection.ml_engine import model_ensemble
>>> print(model_ensemble.device)
>>> model_ensemble.get_all_models_info()

# Test image preprocessing
>>> from detection.preprocessing import apply_clahe
>>> apply_clahe('path/to/test/image.jpg')
```

---

## **🎯 Key URLs for Your Application**

| URL | Purpose | Access |
|-----|---------|--------|
| `/` | Landing page | Everyone |
| `/admin/` | 🌟 Admin panel | Admin only |
| `/accounts/login/` | Login | Everyone |
| `/register/` | Registration | Everyone |
| `/detection/doctor/dashboard/` | Doctor dashboard | Doctors |
| `/detection/patient/dashboard/` | Patient dashboard | Patients |
| `/detection/upload/` | 🌟 Upload & Predict (Spotlight 1) | Doctors |
| `/detection/results/<id>/` | View prediction results | Doctor/Patient |
| `/detection/explain/<id>/` | 🌟 Explainability (Spotlight 2) | Doctor/Patient |
| `/detection/history/` | Prediction history | Doctor/Patient |

---

## **🔐 Default Users for Testing**

After creating superuser, you can create test users via admin panel or shell:

```python
python manage.py shell

# Create test doctor
from django.contrib.auth.models import User
from detection.models import UserProfile

doctor = User.objects.create_user(
    username='doctor1',
    password='testpass123',
    first_name='Dr. John',
    last_name='Smith',
    email='doctor@test.com'
)
doctor.profile.role = 'doctor'
doctor.profile.save()

# Create test patient
patient = User.objects.create_user(
    username='patient1',
    password='testpass123',
    first_name='Jane',
    last_name='Doe',
    email='patient@test.com'
)
from detection.models import Patient
Patient.objects.create(
    user=patient,
    age=35,
    gender='F'
)
```

---

## **🔥 Your 2 Spotlight Features**

### **Spotlight 1: Multi-Model Comparison**
- **Location**: `detection/upload/` → `detection/results/<id>/`
- **What it does**: Runs all 6 models simultaneously and compares results
- **How to demo**:
  1. Login as doctor
  2. Upload X-ray at `/detection/upload/`
  3. View results showing all 6 predictions
  4. Highlight: "My CrossViT achieved 95% while ResNet only got 88%"

### **Spotlight 2: Explainable AI**
- **Location**: `detection/explain/<id>/`
- **What it does**: Shows Grad-CAM heatmaps + dual-branch visualization
- **How to demo**:
  1. From results page, click "View Explanation"
  2. Show Grad-CAM highlighting COVID-affected regions
  3. Show dual-branch visualization (unique to CrossViT!)
  4. Highlight: "Doctors can trust AI when they see WHY it made the decision"

---

## **📊 Admin Panel Power Features**

Access: `http://localhost:8000/admin/`

**What you get for FREE:**
- ✅ User management (add/edit/delete users)
- ✅ View all predictions in beautiful table
- ✅ Filter by diagnosis, date, model
- ✅ Search patients by name
- ✅ See all 6 model results (collapsible sections)
- ✅ View X-ray images directly
- ✅ Mark predictions as validated
- ✅ Add doctor notes
- ✅ Export data

**No coding required for admin panel!**

---

## **🐛 Common Issues & Solutions**

### Issue 1: CUDA not available
```bash
# Solution: Reinstall PyTorch with correct CUDA
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Issue 2: Model weights not found
```bash
# Check if weights exist
ls static/ml_models/

# Verify path in settings
python manage.py shell
>>> from django.conf import settings
>>> print(settings.MODEL_WEIGHTS_DIR)
```

### Issue 3: Image upload fails
```bash
# Check media directory permissions
ls -la media/
chmod -R 755 media/

# Check settings.py
>>> from django.conf import settings
>>> print(settings.MEDIA_ROOT)
```

### Issue 4: Admin panel not showing images
```bash
# Make sure MEDIA_URL is configured in urls.py
# And DEBUG=True for development
```

### Issue 5: Out of VRAM (RTX 4060 8GB)
```python
# Edit ml_engine.py:
# Ensure models are loaded ONE AT A TIME
# Ensure torch.cuda.empty_cache() after each model
# Use mixed precision: torch.cuda.amp
```

---

## **📝 FYP Documentation Tips**

### For Chapter 4 (Research Design):
- Screenshot the admin panel (shows professional system)
- Screenshot multi-model comparison results
- Screenshot explainability visualizations
- Include database schema (from models.py)

### For Chapter 5 (Results):
- Use the admin panel to export prediction data
- Generate comparison tables (CSV export from admin)
- Take screenshots of Grad-CAM heatmaps
- Show model agreement statistics

### For Presentation:
- Demo flow: Register → Login → Upload → View Results → Explainability
- Highlight admin panel (show it's production-ready)
- Compare 6 models side-by-side
- Show explainability (your unique feature!)

---

## **🎓 For Your Thesis**

**When writing about the system:**
- "The system was implemented using Django framework with PostgreSQL database"
- "A role-based access control system was developed with three user types: administrator, doctor, and patient"
- "The web interface provides real-time multi-model comparison, allowing clinicians to view predictions from six different architectures simultaneously"
- "Explainability features were integrated using Gradient-weighted Class Activation Mapping (Grad-CAM) to visualize attention regions"
- "The admin panel provides comprehensive system management capabilities including user administration, prediction review, and statistical analysis"

---

## **🚀 Deployment (Optional - for production)**

### Simple deployment with Gunicorn:
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### With Nginx (production):
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location /static/ {
        alias /path/to/staticfiles/;
    }
    
    location /media/ {
        alias /path/to/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## **📞 Support & Help**

If you encounter issues:
1. Check Django logs: `logs/django.log`
2. Check console output when running `python manage.py runserver`
3. Use Django shell for debugging: `python manage.py shell`
4. Check admin panel for data integrity
5. Verify CUDA availability: `python -c "import torch; print(torch.cuda.is_available())"`

---

## **✅ Final Checklist Before Submission**

- [ ] All 6 model weights in `static/ml_models/`
- [ ] Database migrated and working
- [ ] Superuser created
- [ ] Test upload works
- [ ] All 6 models predict successfully
- [ ] Explainability generates correctly
- [ ] Admin panel accessible
- [ ] Screenshots taken for documentation
- [ ] Code well-commented
- [ ] Requirements.txt up to date
- [ ] Git repository committed
- [ ] Turnitin check <20%

---

## **🎉 You're Ready to Build!**

Follow the setup instructions, copy all files to correct locations, and start your development server. The system is designed to be:
- ✅ Easy to set up (no Docker complexity)
- ✅ Easy to understand (well-documented code)
- ✅ Easy to demo (beautiful UI)
- ✅ Easy to maintain (Django admin magic!)

**Good luck with your FYP! You've got this! 🎓🚀**
