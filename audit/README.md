# Audit & Compliance Module

## Overview

The Audit & Compliance Module provides comprehensive tracking and monitoring for the COVID-19 Detection System to ensure medical compliance (HIPAA/GDPR) and system security.

## Features

### Core Audit Features
- **Comprehensive Audit Trail**: Tracks all user actions (create, read, update, delete, login, logout)
- **Data Access Logging**: HIPAA-compliant tracking of patient data access
- **Login Monitoring**: Tracks all login attempts with IP addresses and user agents
- **Change Tracking**: Complete history of changes to critical medical records
- **Security Alerts**: Real-time monitoring and alerts for suspicious activities

### Compliance Reporting
- HIPAA Audit Reports
- GDPR Compliance Reports
- Data Access Review Reports
- Security Audit Reports
- User Activity Reports

### Security Features
- Multiple failed login detection (5+ attempts triggers alert)
- Unusual access pattern detection (20+ patients/hour)
- IP address and user agent tracking
- Automatic security alerts
- Admin notification system

## Models

### AuditLog
Comprehensive audit trail for all system activities.

**Key Fields:**
- `user`: User who performed the action
- `username`: Username (stored even if user is deleted)
- `action_type`: Type of action (create, read, update, delete, login, etc.)
- `action_description`: Detailed description
- `severity`: Info, warning, error, critical
- `timestamp`: When the action occurred
- `ip_address`: IP address of the user
- `content_object`: Generic relation to affected object
- `old_value/new_value`: State before/after change

### DataAccessLog
HIPAA-compliant tracking for patient data access.

**Key Fields:**
- `accessor`: User who accessed the data
- `accessor_role`: Role of the accessor (doctor, admin, patient)
- `patient`: Patient whose data was accessed
- `data_type`: Type of data accessed
- `access_type`: View, download, export, print, share
- `flagged_for_review`: Flag for suspicious access
- `access_reason`: Purpose of access

### LoginAttempt
Security monitoring for login attempts.

**Key Fields:**
- `username`: Attempted username
- `success`: Whether login was successful
- `ip_address`: IP address of attempt
- `is_suspicious`: Flag for suspicious attempts
- `blocked`: Whether the attempt was blocked

### SecurityAlert
Real-time security alerts.

**Key Fields:**
- `alert_type`: Failed login, unusual access, bulk export, etc.
- `severity`: Low, medium, high, critical
- `acknowledged`: Whether admin has acknowledged
- `auto_blocked`: Whether automatic blocking occurred
- `admin_notified`: Whether admin was notified

### ComplianceReport
Generated compliance reports.

**Key Fields:**
- `report_type`: HIPAA, GDPR, security audit, etc.
- `start_date/end_date`: Report period
- `summary`: Summary statistics (JSONField)
- `details`: Detailed findings (JSONField)
- `pdf_file`: Optional PDF export

### DataChange
Complete change history for critical data.

**Key Fields:**
- `content_object`: The object that was changed
- `changed_by`: User who made the change
- `field_name`: Name of changed field
- `old_value/new_value`: Previous and new values
- `change_reason`: Reason for change

### DataRetentionPolicy
Data retention policy management.

**Key Fields:**
- `data_type`: Type of data
- `retention_days`: Number of days to retain
- `auto_delete`: Whether to automatically delete
- `notify_before_days`: Days before deletion to notify

## Services

### ComplianceReportGenerator
Generates compliance reports for regulatory review.

**Methods:**
- `generate(generated_by)`: Generate report based on type
- `_generate_hipaa_audit()`: HIPAA compliance report
- `_generate_gdpr_compliance()`: GDPR compliance report
- `_generate_access_review()`: Data access review
- `_generate_security_audit()`: Security audit report
- `_generate_user_activity()`: User activity report

### AuditExporter
Export audit logs to CSV.

**Methods:**
- `export_to_csv()`: Export filtered logs to CSV

### SecurityMonitor
Monitor for suspicious activities.

**Static Methods:**
- `check_failed_login_attempts(username, ip_address)`: Check for multiple failed logins
- `check_unusual_access_pattern(accessor, patient)`: Detect unusual access patterns

## Middleware

### AuditMiddleware
Automatically logs certain requests.

**Features:**
- Tracks request timing
- Logs file downloads
- Captures IP addresses and user agents

## Signals

### Login/Logout Tracking
- `user_logged_in`: Logs successful login
- `user_logged_out`: Logs logout
- `user_login_failed`: Logs failed login attempt and checks for suspicious activity

### Data Change Tracking
- `pre_save`: Tracks changes to Prediction and Patient models

## Views & URLs

### Admin Views (Admin Only)
- `/audit/logs/` - Audit log list with filtering
- `/audit/data-access/` - Patient data access logs
- `/audit/login-attempts/` - Login attempts monitoring
- `/audit/security/alerts/` - Security alerts dashboard
- `/audit/security/alert/<id>/acknowledge/` - Acknowledge alert
- `/audit/compliance/generate/` - Generate compliance report
- `/audit/compliance/view/<id>/` - View compliance report
- `/audit/export/csv/` - Export audit logs to CSV
- `/audit/changes/<content_type_id>/<object_id>/` - View change history

### User Views
- `/audit/my-history/` - User's own access history (transparency)

## Usage Examples

### Manual Audit Logging

```python
from audit.models import AuditLog

# Log an action
AuditLog.log(
    user=request.user,
    action_type='export',
    description='Exported patient data to PDF',
    severity='info',
    ip_address=request.META.get('REMOTE_ADDR')
)
```

### Log Patient Data Access

```python
from audit.models import DataAccessLog

DataAccessLog.objects.create(
    accessor=request.user,
    accessor_role=request.user.profile.role,
    patient=patient,
    data_type='xray_image',
    data_id=xray.id,
    access_type='view',
    ip_address=request.META.get('REMOTE_ADDR')
)
```

### Using the Decorator

```python
from audit.decorators import log_data_access

@login_required
@log_data_access(data_type='prediction')
def view_prediction(request, patient_id):
    # View automatically logged
    pass
```

### Generate Compliance Report

```python
from audit.services import ComplianceReportGenerator
from datetime import datetime, timedelta

generator = ComplianceReportGenerator(
    report_type='hipaa_audit',
    start_date=datetime.now() - timedelta(days=30),
    end_date=datetime.now()
)

report = generator.generate(generated_by=request.user)
```

## Integration with Other Modules

### Detection Module
- Logs all prediction views
- Tracks X-ray image access
- Records medical record changes

### Accounts Module
- Integrates with Django auth signals
- Tracks login/logout
- Monitors password changes

## Security Considerations

### Data Protection
- All audit logs are write-only (no editing)
- IP addresses and user agents are captured
- Sensitive data is hashed in logs where appropriate

### Access Control
- Admin-only views require `@admin_required` decorator
- Patients can only view their own access history
- Audit logs cannot be deleted (retention policy only)

### Alert Thresholds
- 5+ failed logins in 1 hour → High severity alert
- 20+ patient accesses in 1 hour → Medium severity alert
- Critical actions → Immediate admin notification

## Performance Optimization

### Database Indexes
All models include optimized indexes for:
- User + timestamp queries
- Action type + timestamp queries
- Content type + object ID queries
- Flagged items

### Query Optimization
- Uses `select_related()` for foreign key queries
- Limits result sets to prevent performance issues
- Pagination on all list views (50 items per page)

## Testing

Run the module test suite:

```bash
python test_audit_module.py
```

All 61 tests should pass with 100% success rate.

## Deployment Checklist

1. **Run Migrations**
   ```bash
   python manage.py makemigrations audit
   python manage.py migrate
   ```

2. **Create Data Retention Policies** (via Django admin)
   - Audit logs: 2 years
   - Login attempts: 90 days
   - Security alerts: 1 year

3. **Configure Security Alerts**
   - Set up email notifications for critical alerts
   - Configure alert thresholds if needed

4. **Test Functionality**
   - Test login/logout tracking
   - Test audit log creation
   - Test compliance report generation
   - Test security alert triggering

5. **User Training**
   - Train admins on compliance reporting
   - Show users their access history page
   - Document alert response procedures

## Maintenance

### Regular Tasks
- Review unacknowledged security alerts daily
- Generate monthly compliance reports
- Archive old audit logs according to retention policy
- Monitor database size and optimize if needed

### Monitoring
- Track failed login patterns
- Review flagged data access logs
- Monitor alert frequency and types
- Check for unusual activity patterns

## Support

For issues or questions:
1. Check the logs: `logs/django.log`
2. Review the Django admin interface
3. Check security alerts dashboard
4. Review this documentation

## License

Part of the COVID-19 Detection System FYP Project
TAR UMT - Student ID: 24PMR12003
