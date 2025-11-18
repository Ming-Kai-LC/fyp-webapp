# COVID-19 Detection System - Project Structure

**Last Updated:** 2025-11-18
**Purpose:** Complete project structure documentation for cross-session reference

---

## 📁 Directory Structure

```
fyp-webapp/
├── .claude/                          # Claude Code configuration
│   └── skills/                       # Development skills (auto-apply)
│       ├── README.md
│       ├── mobile-responsive.md
│       ├── ui-ux-consistency.md
│       ├── django-module-creation.md
│       ├── security-best-practices.md
│       ├── performance-optimization.md
│       ├── code-quality-standards.md
│       └── component-reusability.md
│
├── config/                           # Main Django project
│   ├── __init__.py
│   ├── settings.py                   # ⭐ Main settings
│   ├── urls.py                       # ⭐ Main URL routing
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/                         # ✅ User authentication module
│   ├── models.py                     # Extended User with profile
│   ├── views.py                      # Auth views (stub)
│   ├── forms.py                      # Auth forms (stub)
│   ├── admin.py
│   └── migrations/
│
├── detection/                        # ✅ Main COVID-19 detection module
│   ├── models.py                     # ⭐ UserProfile, Patient, XRayImage, Prediction
│   ├── views.py                      # ⭐ All detection views
│   ├── forms.py                      # ⭐ XRay upload, user registration
│   ├── admin.py                      # ⭐ Beautiful admin panel
│   ├── urls.py                       # Detection URL routing
│   ├── ml_engine.py                  # 🔥 Real ML engine (needs PyTorch)
│   ├── ml_engine_stub.py            # ✅ Mock ML (currently active)
│   ├── preprocessing.py              # 🔥 CLAHE preprocessing
│   ├── preprocessing_stub.py         # ✅ Mock preprocessing
│   ├── explainability.py             # 🔥 Grad-CAM
│   ├── explainability_stub.py        # ✅ Mock explainability
│   ├── services.py                   # (To be created) Business logic
│   ├── mixins.py                     # (To be created) Reusable mixins
│   ├── managers.py                   # (To be created) Custom managers
│   ├── templates/detection/
│   │   ├── components/               # (To be created)
│   │   └── pages/
│   │       ├── upload.html           # ✅ X-ray upload
│   │       ├── results.html          # ✅ Multi-model results
│   │       ├── explain.html          # ✅ Explainability
│   │       ├── doctor_dashboard.html # ✅ Doctor dashboard
│   │       ├── patient_dashboard.html# ✅ Patient dashboard
│   │       ├── history.html          # ✅ Prediction history
│   │       └── patient_profile.html  # ✅ Patient profile
│   └── tests/                        # (To be created) Test suite
│
├── dashboards/                       # 🚧 Role-based dashboards (stub)
│   ├── models.py                     # Empty (uses other models)
│   ├── views.py                      # Dashboard views (to implement)
│   ├── admin.py
│   └── migrations/
│
├── templates/                        # Global templates
│   ├── base.html                     # ✅ Bootstrap 5 base layout
│   ├── home.html                     # ✅ Landing page
│   ├── components/                   # ✅ Reusable components
│   │   ├── navbar.html               # (In base.html)
│   │   ├── footer.html               # (In base.html)
│   │   ├── messages.html             # (In base.html)
│   │   ├── pagination.html           # (To be extracted)
│   │   ├── card.html                 # (To be created)
│   │   ├── stats_card.html           # (To be created)
│   │   ├── empty_state.html          # (To be created)
│   │   └── loading.html              # (To be created)
│   └── accounts/
│       ├── login.html                # ✅ Login page
│       └── register.html             # ✅ Registration page
│
├── static/                           # Static files
│   ├── css/
│   │   └── custom.css                # (To be created) Custom styles
│   ├── js/
│   │   └── app.js                    # (To be created) Custom JS
│   └── ml_models/                    # 🔥 Model weights (.pth files)
│       ├── crossvit_tiny.pth         # (Add when ready)
│       ├── resnet50.pth              # (Add when ready)
│       ├── densenet121.pth           # (Add when ready)
│       ├── efficientnet_b0.pth       # (Add when ready)
│       ├── vit_base.pth              # (Add when ready)
│       └── swin_tiny.pth             # (Add when ready)
│
├── media/                            # Uploaded files
│   ├── xrays/
│   │   ├── original/                 # Original X-ray uploads
│   │   └── processed/                # CLAHE processed images
│   ├── heatmaps/                     # Grad-CAM heatmaps
│   └── attention/                    # Attention maps
│       ├── large/                    # Large branch attention
│       └── small/                    # Small branch attention
│
├── logs/                             # Application logs
│   └── django.log                    # Main log file
│
├── docs/                             # Documentation
│   └── sessions/                     # Session notes (to be created)
│       └── session_YYYYMMDD.md
│
├── files/                            # Original requirement files
│   ├── INDEX.md
│   ├── SETUP_INSTRUCTIONS.md
│   ├── QUICK_REFERENCE.md
│   └── [other original files]
│
├── sample_data/                      # Test data
│   └── test_xray.jpg                 # ✅ Sample X-ray
│
├── venv/                             # Virtual environment (gitignored)
│
├── manage.py                         # ✅ Django management script
├── db.sqlite3                        # ✅ SQLite database
├── requirements.txt                  # (To be created) Dependencies
├── .gitignore                        # ✅ Git ignore rules
├── README.md                         # ✅ Project overview
├── TESTING_GUIDE.md                  # ✅ Testing instructions
├── MODULE_DEVELOPMENT_GUIDE.md       # ✅ Module development guide
└── PROJECT_STRUCTURE.md              # ✅ This file
```

---

## 📊 Module Status

### ✅ Complete Modules

#### config (Main Project)
- **Status:** Complete
- **Purpose:** Django project settings and configuration
- **Key Files:** settings.py, urls.py
- **Dependencies:** None

#### accounts (Authentication)
- **Status:** Basic structure complete
- **Purpose:** User authentication and management
- **Key Files:** models.py (stub)
- **Dependencies:** Django auth
- **Notes:** Using Django's built-in auth + UserProfile from detection

#### detection (COVID-19 Detection Core)
- **Status:** Framework complete (stub mode)
- **Purpose:** Main COVID-19 detection functionality
- **Key Features:**
  - ✅ Database models (UserProfile, Patient, XRayImage, Prediction)
  - ✅ Views (upload, results, explain, dashboards)
  - ✅ Forms (upload, registration)
  - ✅ Admin panel (comprehensive)
  - ✅ ML engine (stub - needs PyTorch)
  - ✅ Templates (all main pages)
- **Dependencies:** accounts
- **Integration:** All other modules depend on this

### 🚧 Stub Modules

#### dashboards (Role-Based Dashboards)
- **Status:** Empty stub
- **Purpose:** Consolidated dashboards for different user roles
- **Planned Features:**
  - Doctor analytics dashboard
  - Patient health summary
  - Admin system overview
- **Dependencies:** detection, accounts
- **Priority:** Medium (functionality in detection for now)

---

## 🗂️ Database Schema

### Current Models

```sql
-- User Management
User (Django built-in)
    - id, username, email, password, first_name, last_name

UserProfile (detection.models)
    - id, user_id (FK), role, phone, created_at, updated_at
    - Roles: admin, doctor, patient

Patient (detection.models)
    - id, user_id (FK), age, gender, date_of_birth
    - medical_history, current_medications
    - emergency_contact, address
    - created_at, updated_at

-- COVID-19 Detection
XRayImage (detection.models)
    - id, patient_id (FK), uploaded_by_id (FK)
    - original_image, processed_image
    - upload_date, notes
    - image_width, image_height, file_size

Prediction (detection.models)
    - id, xray_id (FK)
    - crossvit_prediction, crossvit_confidence
    - resnet50_prediction, resnet50_confidence
    - densenet121_prediction, densenet121_confidence
    - efficientnet_prediction, efficientnet_confidence
    - vit_prediction, vit_confidence
    - swin_prediction, swin_confidence
    - final_diagnosis, consensus_confidence
    - gradcam_heatmap, large_branch_attention, small_branch_attention
    - inference_time
    - reviewed_by_id (FK), doctor_notes
    - is_validated, validated_at
    - created_at
```

### Relationships

```
User 1:1 UserProfile
User 1:1 Patient (if role=patient)
User 1:N XRayImage (as uploader)
Patient 1:N XRayImage
XRayImage 1:N Prediction
User 1:N Prediction (as reviewer)
```

---

## 🔗 URL Routing Structure

```
/                                   # Home page
/admin/                            # Django admin panel
/accounts/login/                   # Login
/accounts/logout/                  # Logout
/register/                         # User registration

/detection/
    ├── doctor/dashboard/          # Doctor dashboard
    ├── patient/dashboard/         # Patient dashboard
    ├── upload/                    # Upload X-ray
    ├── results/<id>/              # View prediction results
    ├── explain/<id>/              # Explainability visualization
    ├── history/                   # Prediction history
    ├── add-notes/<id>/            # Add doctor notes
    ├── patient/profile/           # Patient profile
    └── api/models/                # Model info API
```

---

## 🎨 Template Hierarchy

```
base.html (Bootstrap 5 layout)
    ├── home.html (Landing page)
    │
    ├── accounts/
    │   ├── login.html
    │   └── register.html
    │
    └── detection/
        ├── upload.html
        ├── results.html
        ├── explain.html
        ├── doctor_dashboard.html
        ├── patient_dashboard.html
        ├── history.html
        └── patient_profile.html
```

---

## 🔧 Configuration Files

### settings.py Key Sections

```python
# Apps
INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    # ...
    # Third-party
    'crispy_forms',
    'crispy_bootstrap5',
    # Our apps
    'accounts',
    'detection',
    'dashboards',
]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ML Settings
MODEL_WEIGHTS_DIR = BASE_DIR / 'static' / 'ml_models'
INFERENCE_BATCH_SIZE = 1  # For RTX 4060 8GB
USE_MIXED_PRECISION = True

# Project Metadata
PROJECT_NAME = "COVID-19 Detection using CrossViT"
STUDENT_NAME = "Tan Ming Kai"
STUDENT_ID = "24PMR12003"
UNIVERSITY = "TAR UMT"
```

---

## 📦 Dependencies

### Currently Installed

```
Django==4.2.7
django-crispy-forms==2.1
crispy-bootstrap5==0.7
Pillow==12.0.0
python-decouple==3.8
```

### To Install (When Models Ready)

```
torch==2.1.0
torchvision==0.16.0
timm==0.9.12
pytorch-grad-cam==1.4.8
opencv-python==4.8.1.78
albumentations==1.3.1
scikit-image==0.22.0
numpy==1.24.3
scipy==1.11.4
pandas==2.1.3
matplotlib==3.8.2
seaborn==0.13.0
```

---

## 🎯 Feature Mapping

### Spotlight Feature #1: Multi-Model Comparison

**Location:**
- Backend: `detection/ml_engine.py` (method: `predict_all_models`)
- Frontend: `detection/templates/detection/results.html`
- View: `detection/views.py` (function: `view_results`)

**Status:** ✅ Framework complete (stub mode)

### Spotlight Feature #2: Explainable AI

**Location:**
- Backend: `detection/explainability.py` (function: `generate_explainability_report`)
- Frontend: `detection/templates/detection/explain.html`
- View: `detection/views.py` (function: `explain_prediction`)

**Status:** ✅ Framework complete (stub mode)

---

## 🚀 Planned Modules

### Priority 1: Essential

1. **Reporting Module**
   - Purpose: Generate PDF reports of predictions
   - Status: Not started
   - Dependencies: detection
   - Estimated: 2-3 sessions

2. **Notification System**
   - Purpose: Email/SMS notifications for results
   - Status: Not started
   - Dependencies: detection, accounts
   - Estimated: 2 sessions

### Priority 2: Enhancement

3. **Analytics Module**
   - Purpose: Advanced statistics and insights
   - Status: Not started
   - Dependencies: detection
   - Estimated: 3-4 sessions

4. **Appointment System**
   - Purpose: Manage patient appointments
   - Status: Not started
   - Dependencies: accounts, detection
   - Estimated: 4-5 sessions

### Priority 3: Advanced

5. **API Module (REST)**
   - Purpose: RESTful API for mobile apps
   - Status: Not started
   - Dependencies: All modules
   - Estimated: 3-4 sessions

6. **Real-time Collaboration**
   - Purpose: Doctor consultation chat
   - Status: Not started
   - Dependencies: accounts, detection
   - Estimated: 5-6 sessions

---

## 📝 Development Notes

### Test Accounts Created

```
Admin:
  Username: admin
  Password: admin123
  Role: Administrator

Doctor:
  Username: doctor1
  Password: test123
  Role: Doctor

Patient:
  Username: patient1
  Password: test123
  Role: Patient
```

### Git Branch

```
Current Branch: claude/file-reading-help-01MBgRqJ1Ty9jYGANB79gCEV
Main Branch: (to be determined)
```

### Database State

```
Migrations Applied: ✅ Yes
Superuser Created: ✅ Yes
Test Data: ✅ Yes (3 users, 1 patient)
```

---

## 🔄 Version History

- **v1.0** (2025-11-18): Initial project setup
  - Django structure created
  - Detection module framework complete
  - Stub ML engine for testing
  - All templates created
  - Test accounts set up

---

## 📚 Quick Navigation

- **Start Development:** Read `README.md`
- **Create Module:** Read `MODULE_DEVELOPMENT_GUIDE.md`
- **Test Application:** Read `TESTING_GUIDE.md`
- **Apply Skills:** Check `.claude/skills/`
- **Original Specs:** Check `files/INDEX.md`

---

**This document should be updated whenever the project structure changes!**
