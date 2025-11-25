#!/usr/bin/env python
"""
Automated Model Refactoring Script
Refactors Django models to use abstract base models from common/models.py
"""

import re
import shutil
from pathlib import Path
from datetime import datetime

# Mapping of model names to their appropriate abstract base class
MODEL_BASE_CLASS_MAP = {
    # reporting/models.py
    'ReportTemplate': 'TimeStampedModel',
    'Report': 'TimeStampedAuditableModel',
    'BatchReportJob': 'TimeStampedAuditableModel',

    # medical_records/models.py
    'MedicalCondition': 'TimeStampedAuditableModel',
    'Allergy': 'TimeStampedAuditableModel',
    'Medication': 'TimeStampedAuditableModel',
    'Vaccination': 'TimeStampedAuditableModel',
    'Surgery': 'TimeStampedAuditableModel',
    'FamilyHistory': 'TimeStampedAuditableModel',
    'MedicalDocument': 'TimeStampedAuditableModel',
    'LifestyleInformation': 'TimeStampedModel',
    'COVIDRiskScore': 'TimeStampedModel',

    # audit/models.py
    'AuditLog': 'TimeStampedModel',
    'DataAccessLog': 'TimeStampedModel',
    'LoginAttempt': 'TimeStampedModel',
    'DataChange': 'TimeStampedModel',
    'ComplianceReport': 'TimeStampedAuditableModel',
    'DataRetentionPolicy': 'TimeStampedModel',
    'SecurityAlert': 'TimeStampedModel',

    # notifications/models.py
    'NotificationTemplate': 'TimeStampedModel',
    'Notification': 'TimeStampedModel',
    'NotificationPreference': 'TimeStampedModel',
    'NotificationLog': 'TimeStampedModel',

    # dashboards/models.py
    'DashboardPreference': 'TimeStampedModel',
    'DashboardWidget': 'TimeStampedModel',
}

# Timestamp field patterns to remove or comment
TIMESTAMP_PATTERNS = [
    r'created_at\s*=\s*models\.DateTimeField\(auto_now_add=True[^\)]*\)',
    r'updated_at\s*=\s*models\.DateTimeField\(auto_now=True[^\)]*\)',
    r'generated_at\s*=\s*models\.DateTimeField\(auto_now_add=True[^\)]*\)',
    r'uploaded_at\s*=\s*models\.DateTimeField\(auto_now_add=True[^\)]*\)',
    r'accessed_at\s*=\s*models\.DateTimeField\(auto_now_add=True[^\)]*\)',
    r'timestamp\s*=\s*models\.DateTimeField\(auto_now_add=True[^\)]*\)',
    r'changed_at\s*=\s*models\.DateTimeField\(auto_now_add=True[^\)]*\)',
    r'calculated_at\s*=\s*models\.DateTimeField\(auto_now_add=True[^\)]*\)',
    r'triggered_at\s*=\s*models\.DateTimeField\(auto_now_add=True[^\)]*\)',
    r'attempted_at\s*=\s*models\.DateTimeField\(auto_now_add=True[^\)]*\)',
]

# User tracking field patterns
USER_TRACKING_PATTERNS = [
    r'created_by\s*=\s*models\.ForeignKey\([^)]+related_name=[^)]+\)',
    r'generated_by\s*=\s*models\.ForeignKey\([^)]+related_name=[^)]+\)',
    r'uploaded_by\s*=\s*models\.ForeignKey\([^)]+related_name=[^)]+\)',
    r'recorded_by\s*=\s*models\.ForeignKey\([^)]+related_name=[^)]+\)',
    r'changed_by\s*=\s*models\.ForeignKey\([^)]+related_name=[^)]+\)',
    r'calculated_by\s*=\s*models\.ForeignKey\([^)]+related_name=[^)]+\)',
]

FILES_TO_REFACTOR = [
    'reporting/models.py',
    'medical_records/models.py',
    'audit/models.py',
    'notifications/models.py',
    'dashboards/models.py',
]


def backup_file(file_path):
    """Create a backup of the original file"""
    backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    print(f"[OK] Backed up: {file_path} -> {backup_path}")
    return backup_path


def update_imports(content):
    """Add common.models imports if not present"""
    if 'from common.models import' in content:
        return content

    # Find the last import statement
    import_pattern = r'(from [^\n]+ import [^\n]+\n)'
    imports = list(re.finditer(import_pattern, content))

    if imports:
        last_import = imports[-1]
        insert_pos = last_import.end()

        new_import = "from common.models import TimeStampedModel, TimeStampedAuditableModel, TimeStampedSoftDeleteModel, FullAuditModel, ActiveManager\n"
        content = content[:insert_pos] + new_import + content[insert_pos:]
        print("  [OK] Added common.models imports")

    return content


def refactor_model_class(content, model_name, base_class):
    """Replace models.Model with appropriate abstract base class"""
    # Pattern: class ModelName(models.Model):
    pattern = rf'class {model_name}\(models\.Model\):'
    replacement = f'class {model_name}({base_class}):'

    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)
        print(f"  [OK] {model_name}: models.Model -> {base_class}")

    return content


def remove_timestamp_fields(content, model_name):
    """Remove or comment out manual timestamp fields"""
    for pattern in TIMESTAMP_PATTERNS:
        matches = list(re.finditer(pattern, content, re.MULTILINE))
        if matches:
            for match in matches:
                field_def = match.group(0)
                comment = f"    # Inherited from abstract base: {field_def.strip()}"
                content = content.replace(field_def, comment)
                print(f"  [OK] Commented out manual timestamp field")

    return content


def add_docstring_note(content, model_name, base_class):
    """Add inheritance note to model docstring"""
    # Find the model's docstring
    pattern = rf'class {model_name}\({base_class}\):\s+"""([^"]+)"""'
    match = re.search(pattern, content, re.DOTALL)

    if match:
        docstring = match.group(1)

        # Determine what fields are inherited
        inherited_fields = []
        if 'TimeStamped' in base_class:
            inherited_fields.append("Timestamps: created_at, updated_at")
        if 'Auditable' in base_class or 'FullAudit' in base_class:
            inherited_fields.append("Audit: created_by, updated_by")
        if 'SoftDelete' in base_class or 'FullAudit' in base_class:
            inherited_fields.append("Soft delete: is_deleted, deleted_at, deleted_by")

        if inherited_fields:
            inheritance_note = f"\n\n    Inherits from {base_class}:\n    - " + "\n    - ".join(inherited_fields)

            new_docstring = f'class {model_name}({base_class}):\n    """{docstring.strip()}{inheritance_note}\n    """'
            old_docstring = match.group(0)
            content = content.replace(old_docstring, new_docstring)
            print(f"  [OK] Updated docstring with inheritance info")

    return content


def refactor_file(file_path):
    """Refactor a single models.py file"""
    print(f"\n{'='*60}")
    print(f"Refactoring: {file_path}")
    print(f"{'='*60}")

    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Backup original
    backup_file(file_path)

    # Update imports
    content = update_imports(content)

    # Refactor each model
    for model_name, base_class in MODEL_BASE_CLASS_MAP.items():
        # Check if this model exists in the file
        if f'class {model_name}(' in content:
            print(f"\n  Refactoring {model_name}...")
            content = refactor_model_class(content, model_name, base_class)
            content = add_docstring_note(content, model_name, base_class)
            content = remove_timestamp_fields(content, model_name)

    # Write the refactored content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n[OK] Successfully refactored: {file_path}")


def main():
    """Main refactoring function"""
    print("""
============================================================
   Automated Model Refactoring Script
   Refactoring 25 models across 5 modules
============================================================
    """)

    base_dir = Path(__file__).parent
    refactored_count = 0
    failed_files = []

    for file_path in FILES_TO_REFACTOR:
        full_path = base_dir / file_path

        if not full_path.exists():
            print(f"[WARN] Warning: {file_path} not found, skipping...")
            failed_files.append(file_path)
            continue

        try:
            refactor_file(str(full_path))
            refactored_count += 1
        except Exception as e:
            print(f"[FAIL] Error refactoring {file_path}: {e}")
            failed_files.append(file_path)

    # Summary
    print(f"\n{'='*60}")
    print("REFACTORING SUMMARY")
    print(f"{'='*60}")
    print(f"[OK] Successfully refactored: {refactored_count}/{len(FILES_TO_REFACTOR)} files")

    if failed_files:
        print(f"[FAIL] Failed files: {', '.join(failed_files)}")
    else:
        print("[OK] All files refactored successfully!")

    print("\n[OK] Backups created with timestamp in filename")
    print("[OK] Next steps:")
    print("  1. Review the changes: git diff")
    print("  2. Create migrations: python manage.py makemigrations")
    print("  3. Run migrations: python manage.py migrate")
    print("  4. Test the application")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
