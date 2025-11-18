#!/usr/bin/env python
"""
Test script for Audit & Compliance Module
Verifies module structure, imports, and configuration
"""

import os
import sys
from pathlib import Path

# Add project directory to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Test results
tests_passed = 0
tests_failed = 0
errors = []

def test_module_structure():
    """Test that all required files exist"""
    print("\n=== Testing Module Structure ===")
    global tests_passed, tests_failed

    required_files = [
        'audit/__init__.py',
        'audit/models.py',
        'audit/views.py',
        'audit/urls.py',
        'audit/forms.py',
        'audit/admin.py',
        'audit/apps.py',
        'audit/services.py',
        'audit/signals.py',
        'audit/middleware.py',
        'audit/decorators.py',
        'audit/migrations/__init__.py',
    ]

    for file_path in required_files:
        full_path = BASE_DIR / file_path
        if full_path.exists():
            print(f"✓ {file_path}")
            tests_passed += 1
        else:
            print(f"✗ {file_path} - MISSING")
            errors.append(f"Missing file: {file_path}")
            tests_failed += 1

def test_templates():
    """Test that all required templates exist"""
    print("\n=== Testing Templates ===")
    global tests_passed, tests_failed

    required_templates = [
        'audit/templates/audit/audit_log_list.html',
        'audit/templates/audit/data_access_log_list.html',
        'audit/templates/audit/login_attempts_list.html',
        'audit/templates/audit/security_alerts_dashboard.html',
        'audit/templates/audit/acknowledge_alert.html',
        'audit/templates/audit/generate_compliance_report.html',
        'audit/templates/audit/view_compliance_report.html',
        'audit/templates/audit/my_access_history.html',
        'audit/templates/audit/data_change_history.html',
    ]

    for template_path in required_templates:
        full_path = BASE_DIR / template_path
        if full_path.exists():
            print(f"✓ {template_path}")
            tests_passed += 1
        else:
            print(f"✗ {template_path} - MISSING")
            errors.append(f"Missing template: {template_path}")
            tests_failed += 1

def test_models():
    """Test that all models are properly defined"""
    print("\n=== Testing Models ===")
    global tests_passed, tests_failed

    try:
        # Read models file
        models_file = BASE_DIR / 'audit' / 'models.py'
        with open(models_file, 'r') as f:
            content = f.read()

        required_models = [
            'AuditLog',
            'DataAccessLog',
            'LoginAttempt',
            'DataChange',
            'ComplianceReport',
            'DataRetentionPolicy',
            'SecurityAlert',
        ]

        for model in required_models:
            if f'class {model}' in content:
                print(f"✓ Model {model} defined")
                tests_passed += 1
            else:
                print(f"✗ Model {model} - NOT FOUND")
                errors.append(f"Model not defined: {model}")
                tests_failed += 1

    except Exception as e:
        print(f"✗ Error reading models file: {e}")
        errors.append(f"Models test error: {e}")
        tests_failed += 1

def test_views():
    """Test that all required views are defined"""
    print("\n=== Testing Views ===")
    global tests_passed, tests_failed

    try:
        views_file = BASE_DIR / 'audit' / 'views.py'
        with open(views_file, 'r') as f:
            content = f.read()

        required_views = [
            'audit_log_list',
            'data_access_log_list',
            'login_attempts_list',
            'security_alerts_dashboard',
            'acknowledge_alert',
            'generate_compliance_report',
            'view_compliance_report',
            'export_audit_logs',
            'my_access_history',
            'data_change_history',
        ]

        for view in required_views:
            if f'def {view}' in content:
                print(f"✓ View {view} defined")
                tests_passed += 1
            else:
                print(f"✗ View {view} - NOT FOUND")
                errors.append(f"View not defined: {view}")
                tests_failed += 1

    except Exception as e:
        print(f"✗ Error reading views file: {e}")
        errors.append(f"Views test error: {e}")
        tests_failed += 1

def test_services():
    """Test that all service classes are defined"""
    print("\n=== Testing Services ===")
    global tests_passed, tests_failed

    try:
        services_file = BASE_DIR / 'audit' / 'services.py'
        with open(services_file, 'r') as f:
            content = f.read()

        required_services = [
            'ComplianceReportGenerator',
            'AuditExporter',
            'SecurityMonitor',
        ]

        for service in required_services:
            if f'class {service}' in content:
                print(f"✓ Service {service} defined")
                tests_passed += 1
            else:
                print(f"✗ Service {service} - NOT FOUND")
                errors.append(f"Service not defined: {service}")
                tests_failed += 1

    except Exception as e:
        print(f"✗ Error reading services file: {e}")
        errors.append(f"Services test error: {e}")
        tests_failed += 1

def test_configuration():
    """Test that configuration is properly set up"""
    print("\n=== Testing Configuration ===")
    global tests_passed, tests_failed

    try:
        # Check settings.py
        settings_file = BASE_DIR / 'config' / 'settings.py'
        with open(settings_file, 'r') as f:
            settings_content = f.read()

        if '"audit"' in settings_content or "'audit'" in settings_content:
            print("✓ 'audit' app in INSTALLED_APPS")
            tests_passed += 1
        else:
            print("✗ 'audit' app NOT in INSTALLED_APPS")
            errors.append("'audit' not in INSTALLED_APPS")
            tests_failed += 1

        if 'audit.middleware.AuditMiddleware' in settings_content:
            print("✓ AuditMiddleware in MIDDLEWARE")
            tests_passed += 1
        else:
            print("✗ AuditMiddleware NOT in MIDDLEWARE")
            errors.append("AuditMiddleware not in MIDDLEWARE")
            tests_failed += 1

        # Check urls.py
        urls_file = BASE_DIR / 'config' / 'urls.py'
        with open(urls_file, 'r') as f:
            urls_content = f.read()

        if 'audit.urls' in urls_content:
            print("✓ Audit URLs included in main urls.py")
            tests_passed += 1
        else:
            print("✗ Audit URLs NOT included in main urls.py")
            errors.append("Audit URLs not included")
            tests_failed += 1

    except Exception as e:
        print(f"✗ Error checking configuration: {e}")
        errors.append(f"Configuration test error: {e}")
        tests_failed += 1

def test_urls():
    """Test that URL patterns are properly defined"""
    print("\n=== Testing URL Patterns ===")
    global tests_passed, tests_failed

    try:
        urls_file = BASE_DIR / 'audit' / 'urls.py'
        with open(urls_file, 'r') as f:
            content = f.read()

        required_urls = [
            'audit_log_list',
            'data_access_log_list',
            'login_attempts_list',
            'security_alerts_dashboard',
            'acknowledge_alert',
            'generate_compliance_report',
            'view_compliance_report',
            'export_audit_logs',
            'my_access_history',
            'data_change_history',
        ]

        for url_name in required_urls:
            if f"name='{url_name}'" in content or f'name="{url_name}"' in content:
                print(f"✓ URL pattern {url_name} defined")
                tests_passed += 1
            else:
                print(f"✗ URL pattern {url_name} - NOT FOUND")
                errors.append(f"URL pattern not defined: {url_name}")
                tests_failed += 1

    except Exception as e:
        print(f"✗ Error reading URLs file: {e}")
        errors.append(f"URLs test error: {e}")
        tests_failed += 1

def test_admin():
    """Test that admin classes are properly registered"""
    print("\n=== Testing Admin Configuration ===")
    global tests_passed, tests_failed

    try:
        admin_file = BASE_DIR / 'audit' / 'admin.py'
        with open(admin_file, 'r') as f:
            content = f.read()

        required_admin_classes = [
            'AuditLogAdmin',
            'DataAccessLogAdmin',
            'LoginAttemptAdmin',
            'SecurityAlertAdmin',
            'ComplianceReportAdmin',
            'DataRetentionPolicyAdmin',
            'DataChangeAdmin',
        ]

        for admin_class in required_admin_classes:
            if f'class {admin_class}' in content:
                print(f"✓ Admin class {admin_class} defined")
                tests_passed += 1
            else:
                print(f"✗ Admin class {admin_class} - NOT FOUND")
                errors.append(f"Admin class not defined: {admin_class}")
                tests_failed += 1

    except Exception as e:
        print(f"✗ Error reading admin file: {e}")
        errors.append(f"Admin test error: {e}")
        tests_failed += 1

def print_summary():
    """Print test summary"""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests Passed: {tests_passed}")
    print(f"Tests Failed: {tests_failed}")
    print(f"Total Tests:  {tests_passed + tests_failed}")
    print(f"Success Rate: {(tests_passed/(tests_passed + tests_failed)*100):.1f}%")

    if errors:
        print("\n" + "="*60)
        print("ERRORS FOUND:")
        print("="*60)
        for i, error in enumerate(errors, 1):
            print(f"{i}. {error}")

    print("\n" + "="*60)
    if tests_failed == 0:
        print("✓ ALL TESTS PASSED!")
        print("The Audit & Compliance Module is properly implemented.")
    else:
        print("✗ SOME TESTS FAILED")
        print("Please review the errors above.")
    print("="*60)

if __name__ == '__main__':
    print("="*60)
    print("AUDIT & COMPLIANCE MODULE TEST SUITE")
    print("="*60)

    test_module_structure()
    test_templates()
    test_models()
    test_views()
    test_services()
    test_configuration()
    test_urls()
    test_admin()
    print_summary()

    # Exit with appropriate code
    sys.exit(0 if tests_failed == 0 else 1)
