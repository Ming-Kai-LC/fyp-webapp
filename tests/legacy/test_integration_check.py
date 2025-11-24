#!/usr/bin/env python
"""
Integration check for medical_records module
Verifies configuration, imports, and integration points
"""
import re
from pathlib import Path

def test_settings_integration():
    """Check if medical_records is properly added to settings.py"""
    print("\n=== Testing Settings Integration ===")
    settings_file = Path("config/settings.py")

    with open(settings_file, 'r') as f:
        content = f.read()

    checks = [
        ("medical_records in INSTALLED_APPS", '"medical_records"' in content or "'medical_records'" in content),
        ("Media directories created", '"medical_records"' in content and '"documents"' in content),
        ("Vaccination cert directory", "vaccination_certificates" in content),
    ]

    all_passed = True
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"  {status} {check_name}")
        if not result:
            all_passed = False

    return all_passed

def test_urls_integration():
    """Check if medical_records URLs are included in main urls.py"""
    print("\n=== Testing URL Integration ===")
    urls_file = Path("config/urls.py")

    with open(urls_file, 'r') as f:
        content = f.read()

    checks = [
        ("medical_records URLs included", "medical_records.urls" in content),
        ("URL path configured", "medical-records" in content),
    ]

    all_passed = True
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"  {status} {check_name}")
        if not result:
            all_passed = False

    return all_passed

def test_model_relationships():
    """Check model relationships and imports"""
    print("\n=== Testing Model Relationships ===")
    models_file = Path("medical_records/models.py")

    with open(models_file, 'r') as f:
        content = f.read()

    checks = [
        ("Patient model imported", "from detection.models import Patient" in content),
        ("User model referenced", "settings.AUTH_USER_MODEL" in content),
        ("UUID import for documents", "import uuid" in content),
        ("FileExtensionValidator", "FileExtensionValidator" in content),
        ("All 9 models defined", len(re.findall(r'class \w+\(models\.Model\):', content)) == 9),
    ]

    all_passed = True
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"  {status} {check_name}")
        if not result:
            all_passed = False

    return all_passed

def test_view_security():
    """Check security decorators and permissions"""
    print("\n=== Testing View Security ===")
    views_file = Path("medical_records/views.py")

    with open(views_file, 'r') as f:
        content = f.read()

    # Count view functions
    view_functions = re.findall(r'^def (\w+)\(request', content, re.MULTILINE)

    # Check decorators
    login_required_count = content.count('@login_required')

    checks = [
        ("login_required imported", "from django.contrib.auth.decorators import login_required" in content),
        (f"All {len(view_functions)} views require login", login_required_count >= len(view_functions)),
        ("Patient permission checks", "patient_info" in content),
        ("Messages framework used", "from django.contrib import messages" in content),
        ("FileResponse for downloads", "FileResponse" in content),
    ]

    all_passed = True
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"  {status} {check_name}")
        if not result:
            all_passed = False

    print(f"\n  Found {len(view_functions)} view functions")
    print(f"  {login_required_count} @login_required decorators")

    return all_passed

def test_form_styling():
    """Check Bootstrap form styling"""
    print("\n=== Testing Form Styling ===")
    forms_file = Path("medical_records/forms.py")

    with open(forms_file, 'r') as f:
        content = f.read()

    # Count forms
    form_classes = re.findall(r'class (\w+Form)\(', content)

    checks = [
        (f"{len(form_classes)} ModelForms created", len(form_classes) >= 8),
        ("Bootstrap classes applied", "form-control" in content),
        ("Date input widgets", "type': 'date'" in content),
        ("Textarea widgets", "Textarea" in content),
        ("Checkbox inputs", "CheckboxInput" in content),
    ]

    all_passed = True
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"  {status} {check_name}")
        if not result:
            all_passed = False

    print(f"\n  Form classes: {', '.join(form_classes)}")

    return all_passed

def test_admin_configuration():
    """Check Django admin configuration"""
    print("\n=== Testing Admin Configuration ===")
    admin_file = Path("medical_records/admin.py")

    with open(admin_file, 'r') as f:
        content = f.read()

    registered_models = re.findall(r'@admin\.register\((\w+)\)', content)

    checks = [
        ("Admin models registered", len(registered_models) == 9),
        ("ModelAdmin classes", "ModelAdmin" in content),
        ("list_display configured", "list_display" in content),
        ("list_filter configured", "list_filter" in content),
        ("search_fields configured", "search_fields" in content),
        ("fieldsets defined", "fieldsets" in content),
    ]

    all_passed = True
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"  {status} {check_name}")
        if not result:
            all_passed = False

    print(f"\n  Registered models: {', '.join(registered_models)}")

    return all_passed

def test_service_layer():
    """Check service layer implementation"""
    print("\n=== Testing Service Layer ===")
    services_file = Path("medical_records/services.py")

    with open(services_file, 'r') as f:
        content = f.read()

    methods = re.findall(r'def (\w+)\(', content)

    checks = [
        ("RiskAssessmentService class", "class RiskAssessmentService" in content),
        ("calculate_age_score method", "calculate_age_score" in content),
        ("calculate_comorbidity_score", "calculate_comorbidity_score" in content),
        ("calculate_lifestyle_score", "calculate_lifestyle_score" in content),
        ("calculate_vaccination_score", "calculate_vaccination_score" in content),
        ("determine_risk_level method", "determine_risk_level" in content),
        ("generate_recommendations", "generate_recommendations" in content),
        ("Main calculate_risk_score", "calculate_risk_score" in content and "classmethod" in content),
        ("High-risk conditions list", "HIGH_RISK_CONDITIONS" in content),
        ("Type hints used", "-> Tuple" in content or "-> Dict" in content),
    ]

    all_passed = True
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"  {status} {check_name}")
        if not result:
            all_passed = False

    return all_passed

def test_template_completeness():
    """Check template completeness and structure"""
    print("\n=== Testing Template Completeness ===")
    template_dir = Path("medical_records/templates/medical_records")

    required_templates = {
        "base_medical.html": ["medical-sidebar", "nav-link", "medical_content"],
        "condition_list.html": ["condition", "add_condition"],
        "allergy_list.html": ["allergy", "severity"],
        "medication_list.html": ["medication", "current_medications"],
        "vaccination_list.html": ["vaccination", "covid"],
        "document_list.html": ["document", "upload"],
        "medical_summary.html": ["risk_score", "conditions", "allergies"],
        "risk_assessment.html": ["risk_level", "recommendations"],
    }

    all_passed = True
    for template_name, required_elements in required_templates.items():
        template_path = template_dir / template_name
        if not template_path.exists():
            print(f"  ✗ {template_name} - NOT FOUND")
            all_passed = False
            continue

        with open(template_path, 'r') as f:
            content = f.read().lower()

        missing = [elem for elem in required_elements if elem.lower() not in content]

        if missing:
            print(f"  ✗ {template_name} - Missing: {', '.join(missing)}")
            all_passed = False
        else:
            print(f"  ✓ {template_name}")

    return all_passed

def test_documentation():
    """Check documentation completeness"""
    print("\n=== Testing Documentation ===")
    readme_file = Path("medical_records/README.md")

    if not readme_file.exists():
        print("  ✗ README.md not found")
        return False

    with open(readme_file, 'r') as f:
        content = f.read()

    checks = [
        ("Title present", "# Enhanced Patient Records Module" in content),
        ("Features documented", "## Features Implemented" in content),
        ("Models documented", "## Database Models" in content),
        ("URL routes documented", "## URL Routes" in content),
        ("Risk algorithm explained", "## Risk Assessment Algorithm" in content),
        ("Installation instructions", "## Installation & Setup" in content),
        ("Testing instructions", "## Testing" in content),
        ("File structure documented", "## File Structure" in content),
    ]

    all_passed = True
    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"  {status} {check_name}")
        if not result:
            all_passed = False

    # Count words
    word_count = len(content.split())
    print(f"\n  Documentation: {word_count} words")

    return all_passed

def main():
    """Run all integration tests"""
    print("="*60)
    print("MEDICAL RECORDS MODULE - INTEGRATION TEST")
    print("="*60)

    tests = [
        ("Settings Integration", test_settings_integration),
        ("URL Integration", test_urls_integration),
        ("Model Relationships", test_model_relationships),
        ("View Security", test_view_security),
        ("Form Styling", test_form_styling),
        ("Admin Configuration", test_admin_configuration),
        ("Service Layer", test_service_layer),
        ("Template Completeness", test_template_completeness),
        ("Documentation", test_documentation),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        if test_func():
            print(f"\n✓ {test_name}: PASSED")
            passed += 1
        else:
            print(f"\n✗ {test_name}: FAILED")

    print("\n" + "="*60)
    print(f"INTEGRATION TEST SUMMARY: {passed}/{total} tests passed")
    print("="*60)

    if passed == total:
        print("\n✓ ALL INTEGRATION TESTS PASSED!")
        print("\nThe medical records module is properly integrated.")
        return 0
    else:
        print("\n✗ Some integration tests failed.")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
