# Audit Module Migration Guide

This guide will help you set up the Audit & Compliance Module in your Django project.

## Prerequisites

- Django 3.2+ installed
- Existing Django project with User authentication
- Python 3.8+

## Step 1: Initial Setup

The module has already been added to the project. Verify the configuration:

### Check settings.py

Ensure `audit` is in `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... other apps ...
    'audit',
]
```

Ensure `AuditMiddleware` is in `MIDDLEWARE`:

```python
MIDDLEWARE = [
    # ... other middleware ...
    'audit.middleware.AuditMiddleware',
]
```

### Check urls.py

Ensure audit URLs are included:

```python
urlpatterns = [
    # ... other patterns ...
    path('audit/', include('audit.urls')),
]
```

## Step 2: Create Database Tables

Run migrations to create the audit module tables:

```bash
# Create migration files
python manage.py makemigrations audit

# Apply migrations
python manage.py migrate audit
```

Expected output:
```
Migrations for 'audit':
  audit/migrations/0001_initial.py
    - Create model AuditLog
    - Create model DataAccessLog
    - Create model LoginAttempt
    - Create model DataChange
    - Create model ComplianceReport
    - Create model DataRetentionPolicy
    - Create model SecurityAlert
```

## Step 3: Verify Database Tables

Check that all tables were created:

```bash
python manage.py shell
```

```python
from audit.models import *

# Test model imports
print("AuditLog:", AuditLog.objects.count())
print("DataAccessLog:", DataAccessLog.objects.count())
print("LoginAttempt:", LoginAttempt.objects.count())
print("SecurityAlert:", SecurityAlert.objects.count())
```

## Step 4: Create Superuser (if needed)

```bash
python manage.py createsuperuser
```

## Step 5: Configure Data Retention Policies

1. Start the development server:
   ```bash
   python manage.py runserver
   ```

2. Access Django Admin: `http://localhost:8000/admin/`

3. Navigate to: **Audit & Compliance > Data Retention Policies**

4. Create policies for:

   **Audit Logs**
   - Data Type: `audit_logs`
   - Retention Days: `730` (2 years)
   - Description: "General audit trail logs"
   - Auto Delete: `False` (manual review required)
   - Notify Before Days: `30`

   **Login Attempts**
   - Data Type: `login_attempts`
   - Retention Days: `90` (3 months)
   - Description: "Login attempt logs"
   - Auto Delete: `True`
   - Notify Before Days: `7`

   **Security Alerts**
   - Data Type: `security_alerts`
   - Retention Days: `365` (1 year)
   - Description: "Security alert logs"
   - Auto Delete: `False`
   - Notify Before Days: `30`

   **Data Access Logs**
   - Data Type: `data_access_logs`
   - Retention Days: `2555` (7 years - HIPAA requirement)
   - Description: "Patient data access logs for HIPAA compliance"
   - Auto Delete: `False` (never auto-delete)
   - Notify Before Days: `90`

## Step 6: Test the Module

### Test Audit Logging

1. Log in to the system
2. Navigate to `/audit/logs/`
3. You should see a login audit log entry

### Test Security Monitoring

1. Log out
2. Try to log in with wrong credentials 6 times
3. Navigate to `/audit/security/alerts/`
4. You should see a security alert for multiple failed logins

### Test Compliance Reports

1. Navigate to `/audit/compliance/generate/`
2. Select "Security Audit" report type
3. Set date range for last 30 days
4. Generate report
5. Review the generated report

### Test User Access History

1. As a regular user, navigate to `/audit/my-history/`
2. You should see your own activity history

## Step 7: Integration with Detection Module

The audit module automatically tracks:
- User logins/logouts
- Failed login attempts
- Data changes to Patient and Prediction models

For manual integration, add audit logging to your views:

```python
from audit.models import AuditLog

def some_view(request):
    # Your code here

    # Log the action
    AuditLog.log(
        user=request.user,
        action_type='create',
        description='Created new prediction',
        severity='info',
        ip_address=request.META.get('REMOTE_ADDR')
    )
```

## Step 8: Production Deployment

### Security Settings

1. Ensure SSL/HTTPS is enabled
2. Set up regular database backups
3. Configure email notifications for critical alerts
4. Review and test all security alert triggers

### Performance Optimization

1. Set up database connection pooling
2. Configure caching for read-heavy operations
3. Set up log rotation for audit logs
4. Monitor database size and plan for archival

### Monitoring Setup

1. Set up monitoring for:
   - Failed login rates
   - Security alert frequency
   - Database table sizes
   - Suspicious activity patterns

2. Create automated reports:
   - Daily: Critical security alerts
   - Weekly: Failed login summary
   - Monthly: Full compliance report
   - Quarterly: Data access review

## Troubleshooting

### Issue: Migrations fail with "table already exists"

**Solution:**
```bash
python manage.py migrate audit --fake-initial
```

### Issue: No audit logs are being created

**Check:**
1. Verify signals are connected (check `audit/apps.py` has `ready()` method)
2. Check middleware is loaded: `python manage.py diffsettings | grep MIDDLEWARE`
3. Verify imports in `audit/__init__.py`

### Issue: Templates not found

**Check:**
1. Verify `APP_DIRS` is `True` in `TEMPLATES` setting
2. Check template file paths: `audit/templates/audit/*.html`
3. Restart Django development server

### Issue: Permission denied on audit views

**Check:**
1. User has necessary permissions
2. Admin decorator is working: `@admin_required`
3. User profile has correct role

## Verification Checklist

- [ ] All migrations applied successfully
- [ ] Can log in and see audit log entry
- [ ] Failed login creates security alert
- [ ] Can generate compliance reports
- [ ] User can view their access history
- [ ] Admin can view all audit logs
- [ ] Data retention policies are configured
- [ ] Security alerts appear on dashboard
- [ ] CSV export works for audit logs
- [ ] All tests pass: `python test_audit_module.py`

## Next Steps

1. **Customize Alert Thresholds**: Edit `SecurityMonitor` methods in `audit/services.py`
2. **Add Custom Reports**: Extend `ComplianceReportGenerator` class
3. **Integrate with Other Modules**: Add audit logging to your custom views
4. **Set Up Notifications**: Configure email alerts for critical security events
5. **Create Backup Procedures**: Set up regular backups of audit data

## Support

For issues or questions:
- Check `logs/django.log` for error messages
- Review Django admin for detailed error traces
- Consult the main `README.md` for usage examples

## Compliance Notes

### HIPAA Compliance
- Patient data access logs retained for 7 years minimum
- All access is logged with accessor identity and purpose
- Patients can view who accessed their data

### GDPR Compliance
- Users can view their own access history
- Data deletion requests are logged
- Export functionality for user data

### Security Standards
- All actions are logged with timestamp and IP address
- Failed login attempts trigger automatic alerts
- Suspicious patterns are flagged for review
- Admin actions are fully auditable

---

**Migration Complete!**

Your Audit & Compliance Module is now ready for use.
