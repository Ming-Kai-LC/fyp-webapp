# Audit & Compliance Module

## Overview

The Audit & Compliance Module provides comprehensive tracking and logging of all system activities for medical compliance (HIPAA/GDPR) and security monitoring.

## Features

### Core Features
- Comprehensive audit trail for all user actions
- Patient data access logging (HIPAA compliance)
- Login/logout tracking with IP addresses
- Failed login attempt monitoring
- Data export and report generation logs
- Admin action tracking

### Advanced Features
- Compliance report generation (HIPAA, GDPR, Security, Access Review)
- Data retention policy enforcement
- Automated compliance alerts
- Real-time security alerts
- Suspicious activity detection
- Change tracking for medical records
- User access history (transparency)

## Installation & Setup

### 1. Database Migration

Run the following commands to create the database tables:

```bash
python manage.py makemigrations audit
python manage.py migrate audit
```

### 2. Verify Installation

The module is already configured in:
- `config/settings.py` - Added to INSTALLED_APPS and MIDDLEWARE
- `config/urls.py` - URL patterns included

### 3. Create Initial Data (Optional)

You can create default data retention policies via the Django admin panel:

```python
from audit.models import DataRetentionPolicy

# Create default retention policies
DataRetentionPolicy.objects.create(
    data_type='audit_logs',
    retention_days=365,
    description='Retain audit logs for 1 year',
    is_active=True,
    auto_delete=False
)

DataRetentionPolicy.objects.create(
    data_type='login_attempts',
    retention_days=90,
    description='Retain login attempts for 90 days',
    is_active=True,
    auto_delete=True,
    notify_before_days=7
)
```

## Usage

### Accessing Audit Features

#### Admin Users
- **Audit Logs**: `/audit/logs/`
- **Data Access Logs**: `/audit/data-access/`
- **Login Attempts**: `/audit/login-attempts/`
- **Security Alerts**: `/audit/security/alerts/`
- **Generate Compliance Report**: `/audit/compliance/generate/`

#### All Users
- **My Access History**: `/audit/my-history/`

### Programmatic Usage

#### Creating Audit Logs

```python
from audit.models import AuditLog

# Simple logging
AuditLog.log(
    user=request.user,
    action_type='read',
    description='Viewed patient record',
    severity='info',
    ip_address=request.META.get('REMOTE_ADDR')
)

# Detailed logging with context
from django.contrib.contenttypes.models import ContentType

AuditLog.objects.create(
    user=request.user,
    username=request.user.username,
    action_type='update',
    action_description='Updated patient medical history',
    severity='info',
    ip_address=request.META.get('REMOTE_ADDR'),
    content_type=ContentType.objects.get_for_model(Patient),
    object_id=patient.id,
    old_value={'field': 'old_value'},
    new_value={'field': 'new_value'}
)
```

#### Logging Data Access (HIPAA)

```python
from audit.models import DataAccessLog

DataAccessLog.objects.create(
    accessor=request.user,
    accessor_role=request.user.profile.role,
    patient=patient,
    data_type='xray',
    data_id=xray.id,
    access_type='view',
    access_reason='Clinical review',
    ip_address=request.META.get('REMOTE_ADDR')
)
```

#### Using the Decorator

```python
from audit.decorators import log_data_access

@login_required
@log_data_access('patient_record')
def view_patient_record(request, patient_id):
    # This will automatically log data access
    patient = get_object_or_404(Patient, id=patient_id)
    return render(request, 'patient_detail.html', {'patient': patient})
```

#### Generating Compliance Reports

```python
from audit.services import ComplianceReportGenerator
from django.utils import timezone
from datetime import timedelta

generator = ComplianceReportGenerator(
    report_type='hipaa_audit',
    start_date=timezone.now() - timedelta(days=30),
    end_date=timezone.now()
)

report = generator.generate(generated_by=request.user)
```

## Models

### AuditLog
Comprehensive audit trail for all system activities.

**Fields:**
- user, username, action_type, action_description
- severity (info, warning, error, critical)
- timestamp, ip_address, user_agent
- content_type, object_id (generic relation)
- old_value, new_value (JSON fields)
- success, error_message

### DataAccessLog
Patient data access tracking for HIPAA compliance.

**Fields:**
- accessor, accessor_role, patient
- data_type, data_id, access_type
- accessed_at, ip_address
- is_legitimate, flagged_for_review

### LoginAttempt
Track all login attempts for security monitoring.

**Fields:**
- username, success, timestamp
- ip_address, user_agent, failure_reason
- is_suspicious, blocked

### SecurityAlert
Real-time security alerts for suspicious activities.

**Fields:**
- alert_type, severity, description
- triggered_at, user, ip_address
- acknowledged, acknowledged_by, acknowledged_at
- resolution_notes, auto_blocked, admin_notified

### ComplianceReport
Generated compliance reports for regulatory review.

**Fields:**
- report_type (hipaa_audit, gdpr_compliance, access_review, security_audit, user_activity)
- generated_by, generated_at
- start_date, end_date
- summary, details (JSON fields)
- pdf_file

### DataRetentionPolicy
Define and enforce data retention policies.

**Fields:**
- data_type, retention_days, description
- is_active, auto_delete
- notify_before_days

### DataChange
Track changes to critical medical data.

**Fields:**
- content_type, object_id (generic relation)
- changed_by, changed_at
- field_name, old_value, new_value
- change_reason

## Testing

Run the comprehensive test suite:

```bash
# Run all audit tests
python manage.py test audit

# Run specific test class
python manage.py test audit.tests.AuditLogModelTest

# Run with verbosity
python manage.py test audit -v 2
```

## Security Monitoring

The module includes automatic security monitoring:

1. **Failed Login Detection**: Triggers alert after 5 failed attempts in 1 hour
2. **Unusual Access Patterns**: Detects when a user accesses 20+ patient records in 1 hour
3. **Automatic Signals**: Login/logout events are automatically logged
4. **Model Change Tracking**: Changes to Prediction and Patient models are automatically tracked

## Compliance

### HIPAA Compliance
- All patient data access is logged
- Access logs include accessor, patient, data type, timestamp, and IP address
- Flagging mechanism for suspicious access patterns
- Data access review reports available

### GDPR Compliance
- Users can view their own access history
- Data export tracking
- Data deletion tracking
- Retention policies configurable

## Admin Interface

All models are registered in the Django admin panel with appropriate list displays, filters, and search fields.

Access at: `/admin/audit/`

## Troubleshooting

### Issue: Migrations not applying
```bash
python manage.py migrate audit --fake-initial
```

### Issue: Foreign key constraints
Make sure the detection app is migrated first:
```bash
python manage.py migrate detection
python manage.py migrate audit
```

### Issue: Template not found
Verify templates are in: `audit/templates/audit/`

## Future Enhancements

- PDF report generation
- Email notifications for security alerts
- Automated data retention enforcement
- Integration with external SIEM systems
- Data anonymization tools
- Advanced analytics and dashboards

## Support

For issues or questions:
1. Check the test suite for usage examples
2. Review the specification: `specs/02_AUDIT_COMPLIANCE_MODULE_SPEC.md`
3. Check Django logs: `logs/django.log`

## License

Part of the COVID-19 Detection System
TAR UMT Bachelor of Data Science FYP
Author: Tan Ming Kai (24PMR12003)
