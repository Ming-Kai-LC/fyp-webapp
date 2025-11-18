# COVID-19 Detection System - Deployment Guide

This guide provides step-by-step instructions for deploying the COVID-19 Detection System.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Database Setup](#database-setup)
4. [Create Admin User](#create-admin-user)
5. [Load Initial Data](#load-initial-data)
6. [Run Development Server](#run-development-server)
7. [Production Deployment](#production-deployment)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- Python 3.9 or higher
- pip (Python package manager)
- Git
- 4GB RAM minimum
- 10GB disk space

### Optional (for production)
- PostgreSQL 12+
- Nginx/Apache web server
- SSL certificate
- Twilio account (for SMS)
- SMTP server (for email)

---

## Initial Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Ming-Kai-LC/fyp-webapp.git
cd fyp-webapp
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Database Setup

### 1. Run Migrations
```bash
# Create all database tables
python manage.py migrate
```

Expected output:
```
Operations to perform:
  Apply all migrations: admin, appointments, audit, auth, contenttypes, dashboards, detection, medical_records, notifications, reporting, sessions, token_blacklist
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
  ✅ All migrations applied successfully
```

### 2. Verify Database
```bash
# Check migration status
python manage.py showmigrations
```

All migrations should show `[X]` indicating they've been applied.

---

## Create Admin User

### 1. Create Superuser
```bash
python manage.py createsuperuser
```

Follow the prompts:
```
Username: admin
Email address: admin@example.com
Password: ********
Password (again): ********
Superuser created successfully.
```

### 2. Set Admin Profile
Start Django shell and configure:
```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User

# Get admin user
admin = User.objects.get(username='admin')

# Set profile as admin
admin.profile.role = 'admin'
admin.profile.phone = '+60123456789'
admin.profile.save()

exit()
```

---

## Load Initial Data

### 1. Create Notification Templates
```bash
python manage.py shell
```

```python
from notifications.models import NotificationTemplate

# Create templates
templates = [
    {
        'template_type': 'prediction_ready',
        'channel': 'in_app',
        'subject': 'Your COVID-19 Test Results are Ready',
        'body_template': 'Dear {patient_name}, your test results are now available. Please log in to view them.',
        'is_active': True,
        'is_critical': False
    },
    {
        'template_type': 'critical_result',
        'channel': 'in_app',
        'subject': 'URGENT: COVID-19 Positive Result',
        'body_template': 'Dear {patient_name}, your test result is COVID-19 POSITIVE. Please contact your doctor immediately.',
        'is_active': True,
        'is_critical': True
    },
    {
        'template_type': 'appointment_reminder',
        'channel': 'in_app',
        'subject': 'Appointment Reminder',
        'body_template': 'You have an appointment on {date} at {time} with Dr. {doctor_name}.',
        'is_active': True,
        'is_critical': False
    },
]

for t in templates:
    NotificationTemplate.objects.get_or_create(
        template_type=t['template_type'],
        channel=t['channel'],
        defaults=t
    )

print("✅ Notification templates created")
exit()
```

### 2. Create Report Templates
```bash
python manage.py shell
```

```python
from reporting.models import ReportTemplate

# Create default report template
ReportTemplate.objects.get_or_create(
    name='Standard COVID-19 Detection Report',
    defaults={
        'description': 'Standard report format for COVID-19 detection results',
        'is_default': True,
        'is_active': True
    }
)

print("✅ Report template created")
exit()
```

---

## Run Development Server

### 1. Collect Static Files (optional)
```bash
python manage.py collectstatic --noinput
```

### 2. Start Development Server
```bash
python manage.py runserver
```

The application will be available at: `http://127.0.0.1:8000/`

### 3. Access the Application

**Admin Panel:** `http://127.0.0.1:8000/admin/`
- Username: admin
- Password: (your superuser password)

**Main Site:** `http://127.0.0.1:8000/`

---

## Production Deployment

### 1. Environment Configuration

Create `.env` file:
```bash
cp .env.example .env
```

Edit `.env`:
```
DEBUG=False
SECRET_KEY=your-very-secret-key-here-change-this
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@localhost/covid_detection

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Twilio (optional)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

### 2. Update settings.py

Modify `config/settings.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv('DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL')
    )
}

# Email
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND')
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
```

### 3. PostgreSQL Setup

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE DATABASE covid_detection;
CREATE USER covid_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE covid_detection TO covid_user;
\q
```

Update DATABASE_URL in `.env`:
```
DATABASE_URL=postgresql://covid_user:your_password@localhost/covid_detection
```

Run migrations:
```bash
python manage.py migrate
```

### 4. Gunicorn Setup

Install Gunicorn:
```bash
pip install gunicorn
```

Test Gunicorn:
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### 5. Nginx Configuration

Create `/etc/nginx/sites-available/covid_detection`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /path/to/fyp-webapp/staticfiles/;
    }

    location /media/ {
        alias /path/to/fyp-webapp/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/covid_detection /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. Systemd Service

Create `/etc/systemd/system/covid_detection.service`:

```ini
[Unit]
Description=COVID-19 Detection System
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/fyp-webapp
Environment="PATH=/path/to/fyp-webapp/venv/bin"
ExecStart=/path/to/fyp-webapp/venv/bin/gunicorn \
          --workers 3 \
          --bind 127.0.0.1:8000 \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable covid_detection
sudo systemctl start covid_detection
sudo systemctl status covid_detection
```

### 7. SSL Certificate (Let's Encrypt)

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## Troubleshooting

### Issue: Migration Errors

**Solution:**
```bash
# Reset migrations (⚠️ WARNING: This will delete all data!)
python manage.py migrate --run-syncdb

# Or manually fix:
python manage.py showmigrations
python manage.py migrate [app_name] [migration_name]
```

### Issue: Static Files Not Loading

**Solution:**
```bash
# Collect static files again
python manage.py collectstatic --clear --noinput

# Check STATIC_ROOT and STATIC_URL in settings.py
```

### Issue: Database Connection Error

**Solution:**
```bash
# Check database credentials
# Verify PostgreSQL is running:
sudo systemctl status postgresql

# Test connection:
psql -U covid_user -d covid_detection -h localhost
```

### Issue: Permission Denied on Media Files

**Solution:**
```bash
# Fix media directory permissions
sudo chown -R www-data:www-data /path/to/fyp-webapp/media
sudo chmod -R 755 /path/to/fyp-webapp/media
```

### Issue: Import Error for Dependencies

**Solution:**
```bash
# Reinstall all dependencies
pip install --upgrade -r requirements.txt

# Or install specific package:
pip install --upgrade [package_name]
```

---

## Post-Deployment Checklist

- [ ] All migrations applied
- [ ] Superuser created
- [ ] Initial data loaded (notification templates, report templates)
- [ ] Static files collected
- [ ] Media directories have proper permissions
- [ ] Debug mode disabled in production
- [ ] Secret key changed from default
- [ ] Database backups configured
- [ ] SSL certificate installed
- [ ] ALLOWED_HOSTS configured
- [ ] Email backend configured
- [ ] Error logging set up
- [ ] Performance monitoring enabled

---

## Maintenance

### Regular Tasks

**Daily:**
- Monitor error logs: `tail -f /path/to/logs/django.log`
- Check disk space: `df -h`

**Weekly:**
- Database backup: `pg_dump covid_detection > backup_$(date +%Y%m%d).sql`
- Review audit logs
- Check security alerts

**Monthly:**
- Update dependencies: `pip install --upgrade -r requirements.txt`
- Review analytics data
- Generate compliance reports

---

## Support

For issues or questions:
- Check documentation in `docs/` directory
- Review `INTEGRATION_STATUS.md` for module details
- Contact: Tan Ming Kai (24PMR12003)

---

**Last Updated:** November 18, 2025
**Version:** 1.0.0
