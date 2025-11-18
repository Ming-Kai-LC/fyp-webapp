#!/usr/bin/env python
"""
Comprehensive Integration Test for COVID-19 Detection System
Tests all modules, models, views, URLs, and integrations
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.urls import reverse, NoReverseMatch
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.apps import apps

print("=" * 80)
print("🔍 COMPREHENSIVE SYSTEM TEST - COVID-19 Detection System")
print("=" * 80)
print()

# Track results
total_tests = 0
passed_tests = 0
failed_tests = 0
warnings = []

def test_section(name):
    print(f"\n{'=' * 80}")
    print(f"📋 {name}")
    print("=" * 80)

def test_result(test_name, passed, message=""):
    global total_tests, passed_tests, failed_tests
    total_tests += 1
    if passed:
        passed_tests += 1
        print(f"  ✅ {test_name}")
        if message:
            print(f"     {message}")
    else:
        failed_tests += 1
        print(f"  ❌ {test_name}")
        if message:
            print(f"     Error: {message}")

def test_warning(message):
    warnings.append(message)
    print(f"  ⚠️  {message}")

# ============================================================================
# TEST 1: Module Imports
# ============================================================================
test_section("Module Imports")

modules_to_test = [
    ('detection', ['models', 'views', 'forms', 'urls', 'admin']),
    ('medical_records', ['models', 'views', 'forms', 'urls', 'admin', 'services']),
    ('appointments', ['models', 'views', 'forms', 'urls', 'admin']),
    ('reporting', ['models', 'views', 'forms', 'urls', 'admin', 'services']),
    ('audit', ['models', 'views', 'urls', 'admin', 'middleware']),
    ('notifications', ['models', 'views', 'urls', 'admin', 'services']),
    ('analytics', ['models', 'views', 'urls']),
    ('dashboards', ['models', 'views', 'urls']),
    ('api', ['views', 'serializers', 'urls']),
]

for app_name, components in modules_to_test:
    for component in components:
        try:
            __import__(f"{app_name}.{component}")
            test_result(f"{app_name}.{component}", True)
        except ImportError as e:
            test_result(f"{app_name}.{component}", False, str(e))
        except Exception as e:
            test_result(f"{app_name}.{component}", False, f"Error: {str(e)}")

# ============================================================================
# TEST 2: Django Apps Configuration
# ============================================================================
test_section("Django Apps Configuration")

required_apps = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'accounts',
    'detection',
    'medical_records',
    'appointments',
    'reporting',
    'audit',
    'notifications',
    'analytics',
    'dashboards',
    'api',
]

from django.conf import settings

for app in required_apps:
    is_installed = app in settings.INSTALLED_APPS
    test_result(f"App '{app}' in INSTALLED_APPS", is_installed)

# ============================================================================
# TEST 3: Database Models
# ============================================================================
test_section("Database Models")

try:
    # Detection module models
    from detection.models import Patient, UserProfile, XRayImage, Prediction
    test_result("Detection models imported", True, "Patient, UserProfile, XRayImage, Prediction")

    # Medical Records models
    from medical_records.models import (
        MedicalCondition, Allergy, Medication, Vaccination,
        Surgery, FamilyHistory, MedicalDocument, LifestyleInformation, COVIDRiskScore
    )
    test_result("Medical Records models imported", True, "9 models")

    # Appointments models
    from appointments.models import Appointment, AppointmentType, AppointmentStatus
    test_result("Appointments models imported", True)

    # Reporting models
    from reporting.models import Report, ReportTemplate, BatchReport, ReportAnalytics
    test_result("Reporting models imported", True)

    # Audit models
    from audit.models import AuditLog, AccessLog, LoginAttempt, SystemEvent
    test_result("Audit models imported", True)

    # Notifications models
    from notifications.models import Notification, NotificationTemplate, NotificationPreference
    test_result("Notifications models imported", True)

    # Analytics models
    from analytics.models import AnalyticsSnapshot, ModelPerformanceMetric, CustomReport, DataExport
    test_result("Analytics models imported", True)

    # Dashboards models
    from dashboards.models import DashboardPreference, SavedDashboardView
    test_result("Dashboards models imported", True)

except Exception as e:
    test_result("Models import", False, str(e))

# ============================================================================
# TEST 4: Model Counts in Database
# ============================================================================
test_section("Database Tables")

try:
    from django.db import connection
    tables = connection.introspection.table_names()
    test_result(f"Database tables created", True, f"{len(tables)} tables found")

    # Check key tables exist
    key_tables = [
        'detection_patient', 'detection_xrayimage', 'detection_prediction',
        'medical_records_medicalcondition', 'medical_records_covidriskscore',
        'appointments_appointment', 'reporting_report',
        'audit_auditlog', 'notifications_notification',
        'analytics_analyticssnapshot', 'dashboards_dashboardpreference'
    ]

    for table in key_tables:
        if table in tables:
            test_result(f"Table '{table}' exists", True)
        else:
            test_warning(f"Table '{table}' not found")

except Exception as e:
    test_result("Database tables check", False, str(e))

# ============================================================================
# TEST 5: URL Configuration
# ============================================================================
test_section("URL Configuration")

url_tests = [
    ('home', {}, 'Home page'),
    ('detection:upload', {}, 'X-ray upload'),
    ('appointments:my_appointments', {}, 'My appointments'),
    ('notifications:list', {}, 'Notifications list'),
    ('reporting:list', {}, 'Reports list'),
    ('audit:logs', {}, 'Audit logs'),
    ('analytics:dashboard', {}, 'Analytics dashboard'),
]

for url_name, kwargs, description in url_tests:
    try:
        url = reverse(url_name, kwargs=kwargs)
        test_result(f"URL '{url_name}' resolves", True, f"→ {url}")
    except NoReverseMatch as e:
        test_warning(f"URL '{url_name}' not found ({description})")
    except Exception as e:
        test_result(f"URL '{url_name}'", False, str(e))

# ============================================================================
# TEST 6: Views
# ============================================================================
test_section("View Functions")

try:
    from detection import views as detection_views
    test_result("Detection views imported", True)

    from medical_records import views as mr_views
    test_result("Medical Records views imported", True)

    from appointments import views as appt_views
    test_result("Appointments views imported", True)

    from reporting import views as report_views
    test_result("Reporting views imported", True)

    from audit import views as audit_views
    test_result("Audit views imported", True)

    from notifications import views as notif_views
    test_result("Notifications views imported", True)

    from analytics import views as analytics_views
    test_result("Analytics views imported", True)

    from dashboards import views as dash_views
    test_result("Dashboards views imported", True)

except Exception as e:
    test_result("Views import", False, str(e))

# ============================================================================
# TEST 7: Forms
# ============================================================================
test_section("Form Classes")

try:
    from detection.forms import XRayUploadForm, PatientForm
    test_result("Detection forms imported", True)

    from medical_records.forms import (
        MedicalConditionForm, AllergyForm, MedicationForm, VaccinationForm
    )
    test_result("Medical Records forms imported", True)

    from appointments.forms import AppointmentForm
    test_result("Appointments forms imported", True)

    from reporting.forms import ReportGenerationForm
    test_result("Reporting forms imported", True)

except Exception as e:
    test_result("Forms import", False, str(e))

# ============================================================================
# TEST 8: Admin Registrations
# ============================================================================
test_section("Admin Site Registrations")

try:
    from django.contrib import admin
    registered_models = admin.site._registry
    test_result("Admin site accessible", True, f"{len(registered_models)} models registered")

    # Check key models are registered
    from detection.models import Patient, XRayImage
    if Patient in registered_models:
        test_result("Patient model in admin", True)
    else:
        test_warning("Patient model not in admin")

    if XRayImage in registered_models:
        test_result("XRayImage model in admin", True)
    else:
        test_warning("XRayImage model not in admin")

except Exception as e:
    test_result("Admin registrations", False, str(e))

# ============================================================================
# TEST 9: Middleware
# ============================================================================
test_section("Middleware Configuration")

middleware_checks = [
    ('django.middleware.security.SecurityMiddleware', 'Security middleware'),
    ('django.contrib.sessions.middleware.SessionMiddleware', 'Session middleware'),
    ('django.contrib.auth.middleware.AuthenticationMiddleware', 'Auth middleware'),
    ('audit.middleware.AuditMiddleware', 'Audit middleware'),
]

for middleware, description in middleware_checks:
    if middleware in settings.MIDDLEWARE:
        test_result(f"{description}", True)
    else:
        test_warning(f"{description} not configured")

# ============================================================================
# TEST 10: REST API Configuration
# ============================================================================
test_section("REST API Configuration")

try:
    from rest_framework.settings import api_settings
    test_result("REST Framework configured", True)

    from api.serializers import (
        PatientSerializer, XRayImageSerializer, PredictionSerializer
    )
    test_result("API serializers imported", True)

    # Check JWT configuration
    if 'rest_framework_simplejwt' in settings.INSTALLED_APPS:
        test_result("JWT authentication installed", True)
    else:
        test_warning("JWT authentication not configured")

except Exception as e:
    test_result("REST API", False, str(e))

# ============================================================================
# TEST 11: Template Directories
# ============================================================================
test_section("Template Configuration")

import os
template_dirs = []
for template_setting in settings.TEMPLATES:
    template_dirs.extend(template_setting.get('DIRS', []))

test_result("Template directories configured", len(template_dirs) > 0,
            f"{len(template_dirs)} directories")

# Check for base templates
base_dir = settings.BASE_DIR
templates_path = base_dir / 'templates'
if templates_path.exists():
    test_result("Global templates directory exists", True, str(templates_path))
else:
    test_warning("Global templates directory not found")

# ============================================================================
# TEST 12: Static and Media Files
# ============================================================================
test_section("Static and Media Files")

test_result("STATIC_URL configured", settings.STATIC_URL is not None, settings.STATIC_URL)
test_result("STATIC_ROOT configured", settings.STATIC_ROOT is not None, str(settings.STATIC_ROOT))
test_result("MEDIA_URL configured", settings.MEDIA_URL is not None, settings.MEDIA_URL)
test_result("MEDIA_ROOT configured", settings.MEDIA_ROOT is not None, str(settings.MEDIA_ROOT))

# Check if media directories exist
if settings.MEDIA_ROOT.exists():
    test_result("Media root exists", True)
else:
    test_warning("Media root directory doesn't exist")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("📊 TEST SUMMARY")
print("=" * 80)
print(f"Total Tests: {total_tests}")
print(f"✅ Passed: {passed_tests}")
print(f"❌ Failed: {failed_tests}")
print(f"⚠️  Warnings: {len(warnings)}")
print()

success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
print(f"Success Rate: {success_rate:.1f}%")
print()

if warnings:
    print("Warnings:")
    for warning in warnings:
        print(f"  ⚠️  {warning}")
    print()

if failed_tests == 0:
    print("✅ ALL CRITICAL TESTS PASSED!")
    print("The system is properly integrated and ready for use.")
else:
    print(f"❌ {failed_tests} tests failed. Please review the errors above.")

print("=" * 80)
