---
name: Virtual Environment Management
description: Enforces the use of Python virtual environment for all package installations and Python commands. Auto-applies when running pip, python, or Django management commands.
---

Ensures all Python commands and package installations are executed within the project's virtual environment to maintain dependency isolation and prevent system-wide package conflicts.

## Core Principles

1. **Isolation**: Never install packages globally
2. **Consistency**: All team members use the same virtual environment
3. **Reproducibility**: Dependencies are tracked in requirements.txt
4. **Safety**: Protect system Python from modifications
5. **Portability**: Virtual environment can be recreated anywhere

## Virtual Environment Setup

### Location
```
fyp-webapp/
├── venv/                    # Virtual environment directory
│   ├── Scripts/            # (Windows) Executables and activation scripts
│   ├── Lib/                # Python packages
│   └── ...
├── requirements.txt        # Package dependencies
└── ...
```

### Creating Virtual Environment

**ONLY if venv doesn't exist:**
```bash
python -m venv venv
```

### Activation (Manual - for reference only)

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

## Command Usage Rules

### ✅ ALWAYS Use Virtual Environment Python

**Windows:**
```bash
# Python commands
venv/Scripts/python.exe script.py
venv/Scripts/python.exe manage.py runserver
venv/Scripts/python.exe manage.py migrate

# Pip commands
venv/Scripts/python.exe -m pip install package_name
venv/Scripts/python.exe -m pip install -r requirements.txt
venv/Scripts/python.exe -m pip freeze > requirements.txt
venv/Scripts/python.exe -m pip list
```

**Linux/Mac:**
```bash
# Python commands
venv/bin/python script.py
venv/bin/python manage.py runserver
venv/bin/python manage.py migrate

# Pip commands
venv/bin/python -m pip install package_name
venv/bin/python -m pip install -r requirements.txt
venv/bin/python -m pip freeze > requirements.txt
venv/bin/python -m pip list
```

### ❌ NEVER Use Global Python

```bash
# DON'T do this:
python manage.py runserver        # Uses system Python
pip install django                 # Installs globally
python script.py                   # Uses system Python

# ALWAYS do this instead:
venv/Scripts/python.exe manage.py runserver    # Windows
venv/bin/python manage.py runserver            # Linux/Mac
```

## Common Django Commands

### Development Server
```bash
# Windows
venv/Scripts/python.exe manage.py runserver

# Linux/Mac
venv/bin/python manage.py runserver
```

### Database Migrations
```bash
# Windows
venv/Scripts/python.exe manage.py makemigrations
venv/Scripts/python.exe manage.py migrate

# Linux/Mac
venv/bin/python manage.py makemigrations
venv/bin/python manage.py migrate
```

### Running Tests
```bash
# Windows
venv/Scripts/python.exe manage.py test
venv/Scripts/python.exe -m pytest

# Linux/Mac
venv/bin/python manage.py test
venv/bin/python -m pytest
```

### Creating Superuser
```bash
# Windows
venv/Scripts/python.exe manage.py createsuperuser

# Linux/Mac
venv/bin/python manage.py createsuperuser
```

### Collecting Static Files
```bash
# Windows
venv/Scripts/python.exe manage.py collectstatic

# Linux/Mac
venv/bin/python manage.py collectstatic
```

## Package Management

### Installing New Packages

```bash
# Windows
venv/Scripts/python.exe -m pip install package_name
venv/Scripts/python.exe -m pip freeze > requirements.txt

# Linux/Mac
venv/bin/python -m pip install package_name
venv/bin/python -m pip freeze > requirements.txt
```

### Installing from requirements.txt

```bash
# Windows
venv/Scripts/python.exe -m pip install -r requirements.txt

# Linux/Mac
venv/bin/python -m pip install -r requirements.txt
```

### Upgrading Packages

```bash
# Windows
venv/Scripts/python.exe -m pip install --upgrade package_name
venv/Scripts/python.exe -m pip install --upgrade pip

# Linux/Mac
venv/bin/python -m pip install --upgrade package_name
venv/bin/python -m pip install --upgrade pip
```

### Uninstalling Packages

```bash
# Windows
venv/Scripts/python.exe -m pip uninstall package_name

# Linux/Mac
venv/bin/python -m pip uninstall package_name
```

## Verifying Virtual Environment

### Check Python Location
```bash
# Windows
venv/Scripts/python.exe -c "import sys; print(sys.executable)"
# Should output: D:\Users\USER\Documents\GitHub\fyp-webapp\venv\Scripts\python.exe

# Linux/Mac
venv/bin/python -c "import sys; print(sys.executable)"
# Should output: /path/to/fyp-webapp/venv/bin/python
```

### Check Installed Packages
```bash
# Windows
venv/Scripts/python.exe -m pip list

# Linux/Mac
venv/bin/python -m pip list
```

### Check Package Location
```bash
# Windows
venv/Scripts/python.exe -m pip show django
# Location should be inside venv/Lib/site-packages

# Linux/Mac
venv/bin/python -m pip show django
# Location should be inside venv/lib/python*/site-packages
```

## Troubleshooting

### Virtual Environment Not Found

**Error:** `venv/Scripts/python.exe: command not found`

**Solution:**
```bash
# Create virtual environment
python -m venv venv

# Windows: Verify creation
dir venv\Scripts\python.exe

# Linux/Mac: Verify creation
ls venv/bin/python
```

### Wrong Python Version

**Check version:**
```bash
# Windows
venv/Scripts/python.exe --version

# Linux/Mac
venv/bin/python --version
```

**Expected:** Python 3.11+ (project requirement)

### Package Import Errors

**Error:** `ModuleNotFoundError: No module named 'django'`

**Solution:**
```bash
# Verify you're using venv Python
venv/Scripts/python.exe -c "import sys; print(sys.executable)"  # Windows
venv/bin/python -c "import sys; print(sys.executable)"          # Linux/Mac

# Install missing packages
venv/Scripts/python.exe -m pip install -r requirements.txt      # Windows
venv/bin/python -m pip install -r requirements.txt              # Linux/Mac
```

### Permission Errors (Linux/Mac)

**Error:** `Permission denied: 'venv/bin/python'`

**Solution:**
```bash
chmod +x venv/bin/python
chmod +x venv/bin/activate
```

## Dependencies Management

### Current Project Dependencies

**Core Django:**
- Django==4.2.7
- django-crispy-forms
- crispy-bootstrap5

**Database:**
- psycopg2-binary (optional, for PostgreSQL)

**Image Processing:**
- Pillow

**ML/AI Dependencies:**
- torch (when needed)
- torchvision
- timm
- opencv-python
- scikit-learn
- numpy
- pandas

**Analytics:**
- plotly

**Reporting:**
- weasyprint
- xhtml2pdf
- openpyxl
- qrcode

**REST API:**
- djangorestframework
- djangorestframework-simplejwt
- drf-yasg
- django-cors-headers
- django-filter

**Utilities:**
- python-dateutil
- pytz

### Updating requirements.txt

**After installing new packages:**
```bash
# Windows
venv/Scripts/python.exe -m pip freeze > requirements.txt

# Linux/Mac
venv/bin/python -m pip freeze > requirements.txt
```

**Best practice:** Commit requirements.txt with every package change

## IDE Configuration

### VS Code

**settings.json:**
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/Scripts/python.exe",
    "python.terminal.activateEnvironment": true
}
```

### PyCharm

1. File → Settings → Project → Python Interpreter
2. Click gear icon → Add
3. Select "Existing environment"
4. Choose `venv/Scripts/python.exe` (Windows) or `venv/bin/python` (Linux/Mac)

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Django CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Create virtual environment
        run: python -m venv venv

      - name: Install dependencies
        run: |
          venv/bin/python -m pip install --upgrade pip
          venv/bin/python -m pip install -r requirements.txt

      - name: Run tests
        run: venv/bin/python manage.py test
```

## Auto-Apply This Skill When:

- Running `python` commands
- Running `pip` commands
- Running Django `manage.py` commands
- Installing or upgrading packages
- Running tests
- Starting development server
- Performing database migrations
- Creating new Django apps
- Executing Python scripts
- Troubleshooting import errors

## Critical Reminders

1. **NEVER** use bare `python` or `pip` commands
2. **ALWAYS** use `venv/Scripts/python.exe` (Windows) or `venv/bin/python` (Linux/Mac)
3. **ALWAYS** update requirements.txt after package changes
4. **NEVER** commit the venv folder to git (add to .gitignore)
5. **ALWAYS** verify you're in venv before running commands

## Verification Checklist

Before executing any Python command:

- ✅ Virtual environment exists at `venv/`
- ✅ Using full path to venv Python executable
- ✅ Command uses `venv/Scripts/python.exe` (Windows) or `venv/bin/python` (Linux/Mac)
- ✅ Not using global `python` or `pip`
- ✅ requirements.txt is up to date
- ✅ venv is in .gitignore

## Quick Reference Card

**Windows:**
```bash
# Python
venv/Scripts/python.exe

# Pip
venv/Scripts/python.exe -m pip

# Django manage.py
venv/Scripts/python.exe manage.py
```

**Linux/Mac:**
```bash
# Python
venv/bin/python

# Pip
venv/bin/python -m pip

# Django manage.py
venv/bin/python manage.py
```
