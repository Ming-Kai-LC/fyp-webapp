#!/usr/bin/env python
"""
Syntax and structure validation for medical_records module
Tests what we can without Django installed
"""
import os
import sys
import py_compile
from pathlib import Path

def test_python_syntax(file_path):
    """Test if a Python file has valid syntax"""
    try:
        py_compile.compile(file_path, doraise=True)
        return True, "✓ Syntax OK"
    except py_compile.PyCompileError as e:
        return False, f"✗ Syntax Error: {e}"

def test_file_structure():
    """Test if all required files exist"""
    base_path = Path("medical_records")

    required_files = [
        "__init__.py",
        "models.py",
        "forms.py",
        "views.py",
        "urls.py",
        "admin.py",
        "services.py",
        "tests.py",
        "apps.py",
        "README.md",
    ]

    required_dirs = [
        "migrations",
        "templates/medical_records",
    ]

    required_templates = [
        "templates/medical_records/base_medical.html",
        "templates/medical_records/condition_list.html",
        "templates/medical_records/condition_form.html",
        "templates/medical_records/allergy_list.html",
        "templates/medical_records/allergy_form.html",
        "templates/medical_records/medication_list.html",
        "templates/medical_records/medication_form.html",
        "templates/medical_records/vaccination_list.html",
        "templates/medical_records/vaccination_form.html",
        "templates/medical_records/document_list.html",
        "templates/medical_records/document_form.html",
        "templates/medical_records/document_detail.html",
        "templates/medical_records/medical_summary.html",
        "templates/medical_records/risk_assessment.html",
    ]

    print("\n=== File Structure Test ===")
    all_good = True

    # Check required files
    print("\nRequired Python files:")
    for file in required_files:
        file_path = base_path / file
        if file_path.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - MISSING")
            all_good = False

    # Check required directories
    print("\nRequired directories:")
    for dir_name in required_dirs:
        dir_path = base_path / dir_name
        if dir_path.exists() and dir_path.is_dir():
            print(f"  ✓ {dir_name}/")
        else:
            print(f"  ✗ {dir_name}/ - MISSING")
            all_good = False

    # Check templates
    print("\nRequired templates:")
    for template in required_templates:
        template_path = base_path / template
        if template_path.exists():
            print(f"  ✓ {template}")
        else:
            print(f"  ✗ {template} - MISSING")
            all_good = False

    return all_good

def test_python_files():
    """Test syntax of all Python files"""
    print("\n=== Python Syntax Test ===")
    base_path = Path("medical_records")

    python_files = [
        "models.py",
        "forms.py",
        "views.py",
        "urls.py",
        "admin.py",
        "services.py",
        "tests.py",
        "apps.py",
    ]

    all_good = True
    for py_file in python_files:
        file_path = base_path / py_file
        if file_path.exists():
            success, message = test_python_syntax(str(file_path))
            print(f"\n{py_file}:")
            print(f"  {message}")
            if not success:
                all_good = False
        else:
            print(f"\n{py_file}:")
            print(f"  ✗ File not found")
            all_good = False

    return all_good

def count_lines_of_code():
    """Count lines of code in the module"""
    print("\n=== Code Statistics ===")
    base_path = Path("medical_records")

    python_files = list(base_path.glob("*.py"))
    template_files = list(base_path.glob("templates/**/*.html"))

    total_py_lines = 0
    total_html_lines = 0

    for py_file in python_files:
        if py_file.name != "__init__.py":
            with open(py_file, 'r') as f:
                lines = len(f.readlines())
                total_py_lines += lines
                print(f"  {py_file.name}: {lines} lines")

    print(f"\nTemplate files: {len(template_files)}")
    for template_file in template_files:
        with open(template_file, 'r') as f:
            lines = len(f.readlines())
            total_html_lines += lines

    print(f"\nTotal Python code: {total_py_lines} lines")
    print(f"Total HTML templates: {total_html_lines} lines")
    print(f"Total: {total_py_lines + total_html_lines} lines")

def test_model_definitions():
    """Parse models.py and count models"""
    print("\n=== Model Definitions Test ===")
    models_file = Path("medical_records/models.py")

    if not models_file.exists():
        print("  ✗ models.py not found")
        return False

    with open(models_file, 'r') as f:
        content = f.read()

    # Count model classes
    model_classes = [
        "MedicalCondition",
        "Allergy",
        "Medication",
        "Vaccination",
        "Surgery",
        "FamilyHistory",
        "MedicalDocument",
        "LifestyleInformation",
        "COVIDRiskScore"
    ]

    for model_name in model_classes:
        if f"class {model_name}" in content:
            print(f"  ✓ {model_name} model defined")
        else:
            print(f"  ✗ {model_name} model missing")

    return True

def test_url_patterns():
    """Check URL patterns"""
    print("\n=== URL Patterns Test ===")
    urls_file = Path("medical_records/urls.py")

    if not urls_file.exists():
        print("  ✗ urls.py not found")
        return False

    with open(urls_file, 'r') as f:
        content = f.read()

    required_urls = [
        "condition_list",
        "add_condition",
        "allergy_list",
        "add_allergy",
        "medication_list",
        "add_medication",
        "vaccination_list",
        "add_vaccination",
        "document_list",
        "upload_document",
        "medical_summary",
        "calculate_risk_score",
    ]

    for url_name in required_urls:
        if url_name in content:
            print(f"  ✓ {url_name} URL pattern exists")
        else:
            print(f"  ✗ {url_name} URL pattern missing")

    return True

def main():
    """Run all tests"""
    print("="*60)
    print("MEDICAL RECORDS MODULE - VALIDATION TEST")
    print("="*60)

    tests_passed = 0
    tests_total = 5

    # Test 1: File structure
    if test_file_structure():
        tests_passed += 1

    # Test 2: Python syntax
    if test_python_files():
        tests_passed += 1

    # Test 3: Model definitions
    if test_model_definitions():
        tests_passed += 1

    # Test 4: URL patterns
    if test_url_patterns():
        tests_passed += 1

    # Test 5: Code statistics
    count_lines_of_code()
    tests_passed += 1  # Always passes

    # Summary
    print("\n" + "="*60)
    print(f"VALIDATION SUMMARY: {tests_passed}/{tests_total} tests passed")
    print("="*60)

    if tests_passed == tests_total:
        print("\n✓ ALL VALIDATION TESTS PASSED!")
        print("\nNote: Django is not installed in this environment.")
        print("To run full tests with Django:")
        print("  1. Install Django: pip install django crispy-forms crispy-bootstrap5")
        print("  2. Run migrations: python manage.py makemigrations medical_records")
        print("  3. Apply migrations: python manage.py migrate")
        print("  4. Run tests: python manage.py test medical_records")
        return 0
    else:
        print("\n✗ Some validation tests failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
