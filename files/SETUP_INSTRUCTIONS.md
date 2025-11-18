# 🚀 COVID-19 Detection System - Django Setup Guide

## **STEP 1: Create Virtual Environment**

```bash
# Navigate to your project folder
cd ~/your-fyp-folder

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Verify activation (should show venv in prompt)
which python  # Should point to venv/bin/python
```

---

## **STEP 2: Install Dependencies**

```bash
# Upgrade pip first
pip install --upgrade pip

# Install PyTorch (CUDA 11.8 for RTX 4060)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install all other dependencies
pip install -r requirements.txt

# Verify PyTorch CUDA
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'CUDA Version: {torch.version.cuda}')"
```

---

## **STEP 3: Create Django Project**

```bash
# Create main project
django-admin startproject config .

# Create apps
python manage.py startapp accounts
python manage.py startapp detection
python manage.py startapp dashboards

# Project structure should look like:
# covid_detection_django/
# ├── manage.py
# ├── config/
# ├── accounts/
# ├── detection/
# └── dashboards/
```

---

## **STEP 4: Create Required Directories**

```bash
# Create directory structure
mkdir -p static/ml_models
mkdir -p static/css
mkdir -p static/js
mkdir -p media/xrays/original
mkdir -p media/xrays/processed
mkdir -p media/heatmaps
mkdir -p media/attention/large
mkdir -p media/attention/small
mkdir -p templates
```

---

## **STEP 5: Copy Model Weights**

```bash
# Copy your trained model weights to static/ml_models/
# You should have these files:
# - crossvit_tiny.pth
# - resnet50.pth
# - densenet121.pth
# - efficientnet_b0.pth
# - vit_base.pth
# - swin_tiny.pth

cp /path/to/your/weights/*.pth static/ml_models/
```

---

## **STEP 6: Initial Django Setup**

```bash
# Apply migrations (after adding models)
python manage.py makemigrations
python manage.py migrate

# Create superuser for admin panel
python manage.py createsuperuser
# Username: admin
# Email: your@email.com
# Password: (choose a strong password)

# Collect static files
python manage.py collectstatic --noinput
```

---

## **STEP 7: Run Development Server**

```bash
# Start server
python manage.py runserver

# Access application:
# Main site: http://localhost:8000/
# Admin panel: http://localhost:8000/admin/
```

---

## **STEP 8: Testing ML Models**

```bash
# Test if models load correctly
python manage.py shell

>>> from detection.ml_engine import model_ensemble
>>> print(model_ensemble.device)  # Should show 'cuda' if RTX 4060 is working
>>> # Test single prediction
>>> result = model_ensemble.predict_single_model('crossvit', 'path/to/test/xray.jpg')
>>> print(result)
```

---

## **📁 Final Project Structure**

```
covid_detection_django/
├── manage.py
├── requirements.txt
├── config/
│   ├── __init__.py
│   ├── settings.py          # ⭐ Configure this
│   ├── urls.py               # ⭐ Configure this
│   └── wsgi.py
├── accounts/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── templates/
├── detection/
│   ├── models.py             # ⭐ Database schema
│   ├── views.py              # ⭐ Main logic
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py              # ⭐ Admin panel
│   ├── ml_engine.py          # ⭐ AI models
│   ├── preprocessing.py      # ⭐ CLAHE
│   ├── explainability.py     # ⭐ Grad-CAM
│   └── templates/
├── dashboards/
│   ├── views.py
│   ├── urls.py
│   └── templates/
├── templates/
│   ├── base.html
│   └── home.html
├── static/
│   ├── css/
│   ├── js/
│   └── ml_models/            # ⭐ Your .pth files here
│       ├── crossvit_tiny.pth
│       ├── resnet50.pth
│       └── ...
└── media/
    ├── xrays/
    ├── heatmaps/
    └── attention/
```

---

## **🎯 Next Steps After Setup**

1. **Configure settings.py** (see settings_config.py artifact)
2. **Copy models.py** (see detection_models.py artifact)
3. **Copy ml_engine.py** (see ml_engine.py artifact)
4. **Copy views.py** (see detection_views.py artifact)
5. **Copy admin.py** (see detection_admin.py artifact)
6. **Copy forms.py** (see detection_forms.py artifact)
7. **Configure URLs** (see urls_config.py artifact)

---

## **⚠️ Common Issues & Solutions**

### Issue: CUDA not available
```bash
# Solution: Reinstall PyTorch with correct CUDA version
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Issue: Model weights not found
```bash
# Solution: Check path in settings.py
python manage.py shell
>>> from django.conf import settings
>>> import os
>>> print(os.path.join(settings.STATICFILES_DIRS[0], 'ml_models'))
```

### Issue: Image upload fails
```bash
# Solution: Check media directory permissions
chmod -R 755 media/
```

---

## **🔥 Ready to Code!**

Once setup is complete, you can start the development server and access:
- **Admin Panel**: http://localhost:8000/admin/
- **Upload X-ray**: http://localhost:8000/detection/upload/
- **View Results**: http://localhost:8000/detection/results/<id>/

**Good luck with your FYP! 🎓**
