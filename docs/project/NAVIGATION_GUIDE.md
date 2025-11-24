# Navigation Guide - Where to Find All Modules
## COVID-19 Detection Webapp

**Last Updated:** 2025-11-20

---

## The Issue: Modules Are Hidden Until Login!

All 10 modules are fully implemented, but **you can only see them AFTER logging in**. The navigation menu changes based on your user role (Doctor/Patient/Admin).

---

## Quick Access Map

### Before Login (Public Pages):
```
├── Home Page (/)
├── Login (/accounts/login/)
└── Register (/register/)
```

### After Login - DOCTOR Role:
The navigation dropdown appears with these options:

```
Menu Dropdown (Top Right):
├── Dashboard → /detection/doctor-dashboard/
├── Enhanced Dashboard → /dashboards/doctor/
├── ─────────────────────
├── Upload X-Ray → /detection/upload/
├── Appointments → /appointments/doctor/
├── ─────────────────────
├── Analytics → /analytics/
├── Reports → /reporting/reports/
└── Audit Logs → /audit/logs/
```

### After Login - PATIENT Role:
```
Menu Dropdown (Top Right):
├── Dashboard → /detection/patient-dashboard/
├── Enhanced Dashboard → /dashboards/patient/
├── ─────────────────────
├── My Results → /detection/history/
├── Medical Records → /medical-records/summary/{patient_id}/
└── My Appointments → /appointments/my-appointments/
```

### After Login - ADMIN Role:
```
Menu Dropdown (Top Right):
├── Admin Dashboard → /dashboards/admin/
├── ─────────────────────
├── Analytics → /analytics/
├── Audit Logs → /audit/logs/
├── Security Alerts → /audit/security-alerts/
└── Compliance → /audit/compliance/
```

---

## How to Access Each Module

### 1. DETECTION MODULE ✅
**Location:** Accessible after login based on role

**For Doctors:**
- Upload X-Ray: Menu → "Upload X-Ray" → `/detection/upload/`
- Doctor Dashboard: Menu → "Dashboard" → `/detection/doctor-dashboard/`

**For Patients:**
- Patient Dashboard: Menu → "Dashboard" → `/detection/patient-dashboard/`
- My Results: Menu → "My Results" → `/detection/history/`

**Features Available:**
- Multi-model X-ray analysis (6 AI models)
- Grad-CAM explainability visualization
- Prediction history
- Doctor validation workflow

---

### 2. MEDICAL RECORDS MODULE ✅
**Location:** Menu → "Medical Records" (Patient role only)

**Direct URLs:**
```
/medical-records/summary/{patient_id}/     # Medical summary
/medical-records/conditions/               # Medical conditions
/medical-records/allergies/                # Allergies
/medical-records/medications/              # Medications
/medical-records/vaccinations/             # Vaccinations
/medical-records/documents/                # Medical documents
/medical-records/risk-assessment/          # COVID risk score
```

**Features Available:**
- Complete medical history
- Allergy tracking
- Medication management
- Vaccination records
- Document storage (OCR-ready)
- COVID-19 risk scoring

**Note:** Patient menu only shows this if `user.patient_info` exists

---

### 3. APPOINTMENTS MODULE ✅
**Location:** Menu → "Appointments" or "My Appointments"

**For Doctors:**
- Doctor Appointments: Menu → "Appointments" → `/appointments/doctor/`
- Manage Schedule: `/appointments/manage-schedule/`

**For Patients:**
- My Appointments: Menu → "My Appointments" → `/appointments/my-appointments/`
- Book Appointment: `/appointments/book/`

**Direct URLs:**
```
/appointments/book/                   # Book new appointment
/appointments/my-appointments/        # Patient's appointments
/appointments/doctor/                 # Doctor's appointments
/appointments/manage-schedule/        # Doctor schedule management
/appointments/{id}/                   # Appointment details
/appointments/{id}/reschedule/        # Reschedule
/appointments/waitlist/join/          # Join waitlist
```

**Features Available:**
- Online booking
- Schedule management
- Waitlist system
- Virtual consultation support
- Appointment reminders
- No-show tracking

---

### 4. ANALYTICS MODULE ✅
**Location:** Menu → "Analytics" (Doctor and Admin roles)

**Direct URLs:**
```
/analytics/                           # Main analytics dashboard
/analytics/trends/                    # Trend analysis
/analytics/models/                    # Model comparison
/analytics/demographics/              # Demographic analysis
/analytics/predictions/               # Prediction analytics
/analytics/custom-reports/            # Custom reports
/analytics/export/                    # Data export
```

**Features Available:**
- Dashboard with key metrics
- 30-day trend analysis
- AI model performance comparison
- Demographic breakdowns
- Custom report builder
- Data export (CSV/JSON)

---

### 5. AUDIT MODULE ✅
**Location:** Menu → "Audit Logs" or "Security Alerts" (Doctor and Admin roles)

**Direct URLs:**
```
/audit/logs/                          # All audit logs
/audit/data-access/                   # Data access logs (HIPAA)
/audit/login-attempts/                # Login attempts
/audit/security-alerts/               # Security alerts dashboard
/audit/compliance/                    # Compliance reports (Admin only)
/audit/my-access-history/             # Personal access history
/audit/data-changes/                  # Data change history
```

**Features Available:**
- Comprehensive audit trail
- HIPAA compliance tracking
- Security alerts
- Login attempt monitoring
- Data change history
- Compliance report generation

---

### 6. DASHBOARDS MODULE ✅
**Location:** Menu → "Enhanced Dashboard" (All roles)

**Direct URLs:**
```
/dashboards/doctor/                   # Enhanced doctor dashboard
/dashboards/patient/                  # Enhanced patient dashboard
/dashboards/admin/                    # Enhanced admin dashboard
/dashboards/preferences/              # Dashboard preferences
```

**Features Available:**
- Role-specific dashboards
- Widget customization
- Theme preferences
- Auto-refresh settings
- Real-time statistics
- Aggregated data from all modules

---

### 7. NOTIFICATIONS MODULE ✅
**Location:** Bell icon (top navigation) and User dropdown

**Direct URLs:**
```
/notifications/                       # All notifications
/notifications/preferences/           # Notification settings
/notifications/{id}/mark-read/        # Mark as read
/notifications/mark-all-read/         # Mark all as read
```

**Features Available:**
- In-app notifications
- Notification preferences
- Read/unread tracking
- Real-time badge updates
- Priority-based alerts

---

### 8. REPORTING MODULE ✅
**Location:** Menu → "Reports" (Doctor role)

**Direct URLs:**
```
/reporting/reports/                   # Report list
/reporting/generate/                  # Generate report
/reporting/batch-generate/            # Batch generation
/reporting/templates/                 # Template management
/reporting/reports/{id}/              # View report
/reporting/reports/{id}/download/     # Download PDF
/reporting/export-excel/              # Excel export
```

**Features Available:**
- PDF report generation
- Batch processing
- Custom templates
- QR code inclusion
- Hospital branding
- Excel data export
- Email delivery (when configured)

---

### 9. API MODULE ✅
**Location:** Programmatic access via `/api/v1/`

**API Documentation:**
```
/api/docs/                            # Swagger UI documentation
/api/redoc/                           # ReDoc documentation
/api/schema/                          # OpenAPI JSON schema
```

**Main Endpoints:**
```
POST   /api/v1/register/              # User registration
POST   /api/v1/login/                 # JWT login
GET    /api/v1/predictions/           # List predictions
POST   /api/v1/predictions/upload/    # Upload X-ray
GET    /api/v1/patients/              # List patients
GET    /api/v1/appointments/          # List appointments
POST   /api/v1/appointments/          # Book appointment
```

**Features Available:**
- RESTful API
- JWT authentication
- Role-based access
- Mobile app integration
- Third-party integrations

---

### 10. ACCOUNTS MODULE ✅
**Location:** Built-in Django authentication

**Direct URLs:**
```
/accounts/login/                      # Login page
/accounts/logout/                     # Logout
/accounts/password_change/            # Change password
/accounts/password_reset/             # Reset password
/register/                            # Registration
```

**Features Available:**
- User registration (with role selection)
- Login/logout
- Password reset
- Password change
- Session management

---

## Step-by-Step: How to See All Modules

### Step 1: Create a Doctor Account
1. Go to `http://localhost:8000/`
2. Click "Register"
3. Fill in the form
4. Select Role: **Doctor**
5. Submit

### Step 2: Login
1. Login with your new account
2. You will be redirected to the home page

### Step 3: Access the Dropdown Menu
1. Look at the **top navigation bar**
2. Find the "Menu" dropdown (with grid icon)
3. Click it to see all available modules:
   - Dashboard
   - Enhanced Dashboard
   - Upload X-Ray
   - Appointments
   - Analytics
   - Reports
   - Audit Logs

### Step 4: Explore Each Module
- Click on any menu item to access that module
- Each module has its own sub-pages and features

---

## Visual Navigation Structure

```
┌─────────────────────────────────────────────────────────┐
│  COVID-19 Detection    [Home]  [Menu ▼]  [🔔]  [User ▼] │
└─────────────────────────────────────────────────────────┘
                              │
                              ├─ Menu Dropdown (DOCTOR):
                              │  ├─ Dashboard
                              │  ├─ Enhanced Dashboard
                              │  ├─ ────────────────
                              │  ├─ Upload X-Ray ────────► Detection Module
                              │  ├─ Appointments ─────────► Appointments Module
                              │  ├─ ────────────────
                              │  ├─ Analytics ────────────► Analytics Module
                              │  ├─ Reports ──────────────► Reporting Module
                              │  └─ Audit Logs ───────────► Audit Module
                              │
                              ├─ Bell Icon:
                              │  └─ Notifications ────────► Notifications Module
                              │
                              └─ User Dropdown:
                                 ├─ Notification Settings
                                 └─ Logout
```

---

## Why You Only Saw Login/Register

The system uses **role-based access control**. Before login:
- ✅ You can see: Home, Login, Register
- ❌ You cannot see: Any module pages (protected by authentication)

After login:
- ✅ Navigation menu appears with role-specific options
- ✅ All modules become accessible via dropdowns
- ✅ Each role sees different menu options

---

## Current Navigation Issues to Fix

Based on the code review, here are potential issues:

### Issue 1: Medical Records Link Dependency
```html
<!-- templates/base.html line 138-142 -->
{% if user.patient_info %}
<a class="dropdown-item" href="{% url 'medical_records:medical_summary' user.patient_info.id %}">
    <i class="bi bi-heart-pulse"></i> Medical Records
</a>
{% endif %}
```

**Problem:** Only shows if `user.patient_info` exists
**Solution:** Create Patient record when patient registers

### Issue 2: Navigation Relies on UserProfile
```python
# base.html uses user.profile.is_doctor, user.profile.is_patient
```

**Problem:** If UserProfile doesn't exist, navigation fails
**Solution:** Ensure signal creates UserProfile on user creation

---

## Testing the Navigation

### Test as Doctor:
```bash
# 1. Register as doctor
# 2. Login
# 3. You should see:
- Menu dropdown with 8 items
- Upload X-Ray option
- Analytics access
- Reports access
- Audit Logs access
```

### Test as Patient:
```bash
# 1. Register as patient
# 2. Login
# 3. You should see:
- Menu dropdown with 5 items
- My Results option
- Medical Records option (if patient_info exists)
- My Appointments option
```

### Test as Admin:
```bash
# 1. Create superuser: python manage.py createsuperuser
# 2. Login
# 3. You should see:
- Admin Dashboard
- Analytics
- Audit Logs
- Security Alerts
- Compliance
```

---

## All Module URLs Reference

### Detection URLs (detection/urls.py):
```python
path('upload/', upload_xray, name='upload_xray')
path('results/<int:prediction_id>/', view_results, name='view_results')
path('explain/<int:prediction_id>/', explain_prediction, name='explain_prediction')
path('history/', prediction_history, name='prediction_history')
path('doctor-dashboard/', doctor_dashboard, name='doctor_dashboard')
path('patient-dashboard/', patient_dashboard, name='patient_dashboard')
path('add-notes/<int:prediction_id>/', add_doctor_notes, name='add_doctor_notes')
```

### Medical Records URLs (medical_records/urls.py):
```python
path('summary/<int:patient_id>/', medical_summary, name='medical_summary')
path('conditions/', condition_list, name='condition_list')
path('conditions/add/', add_condition, name='add_condition')
path('allergies/', allergy_list, name='allergy_list')
path('medications/', medication_list, name='medication_list')
path('vaccinations/', vaccination_list, name='vaccination_list')
path('documents/', document_list, name='document_list')
path('risk-assessment/', calculate_risk_score, name='risk_assessment')
```

### Appointments URLs (appointments/urls.py):
```python
path('book/', book_appointment, name='book_appointment')
path('my-appointments/', my_appointments, name='my_appointments')
path('doctor/', doctor_appointments, name='doctor_appointments')
path('manage-schedule/', manage_schedule, name='manage_schedule')
path('<int:appointment_id>/', appointment_detail, name='appointment_detail')
path('waitlist/join/', join_waitlist, name='join_waitlist')
```

### Analytics URLs (analytics/urls.py):
```python
path('', analytics_dashboard, name='dashboard')
path('trends/', trend_analysis, name='trends')
path('models/', model_comparison, name='model_comparison')
path('demographics/', demographic_analysis, name='demographics')
path('predictions/', prediction_analytics, name='predictions')
path('custom-reports/', custom_reports, name='custom_reports')
path('export/', export_data, name='export_data')
```

### Audit URLs (audit/urls.py):
```python
path('logs/', audit_log_list, name='audit_log_list')
path('data-access/', data_access_log_list, name='data_access_log_list')
path('login-attempts/', login_attempts_list, name='login_attempts_list')
path('security-alerts/', security_alerts_dashboard, name='security_alerts_dashboard')
path('compliance/', compliance_dashboard, name='compliance_dashboard')
path('my-access-history/', my_access_history, name='my_access_history')
```

### Dashboards URLs (dashboards/urls.py):
```python
path('doctor/', enhanced_doctor_dashboard, name='doctor')
path('patient/', enhanced_patient_dashboard, name='patient')
path('admin/', enhanced_admin_dashboard, name='admin')
path('preferences/', dashboard_preferences, name='preferences')
```

### Notifications URLs (notifications/urls.py):
```python
path('', notification_list, name='notification_list')
path('<int:notification_id>/mark-read/', mark_as_read, name='mark_as_read')
path('mark-all-read/', mark_all_as_read, name='mark_all_as_read')
path('preferences/', notification_preferences, name='preferences')
```

### Reporting URLs (reporting/urls.py):
```python
path('reports/', report_list, name='report_list')
path('generate/', generate_report, name='generate_report')
path('batch-generate/', batch_generate_reports, name='batch_generate')
path('reports/<int:report_id>/', view_report, name='view_report')
path('reports/<int:report_id>/download/', download_report, name='download_report')
path('templates/', manage_templates, name='manage_templates')
```

---

## Quick Fix: Make Modules More Visible

If you want to make modules more visible on the home page, you can:

### Option 1: Add Quick Links on Home Page
Edit `templates/home.html` to add a "Features" section with direct links

### Option 2: Add Breadcrumb Navigation
Add breadcrumbs to show current location in the app

### Option 3: Add Sidebar Navigation
Create a persistent sidebar with all module links

### Option 4: Add Dashboard Cards
Replace dropdown with dashboard cards showing all modules

---

## Summary

**All 10 modules ARE implemented and accessible!**

The reason you only saw Login/Register is because:
1. Navigation is **hidden until you login**
2. Navigation is **role-based** (different menus for Doctor/Patient/Admin)
3. Modules are in **dropdown menus**, not main navigation

**To access all modules:**
1. Register as a Doctor
2. Login
3. Click the "Menu" dropdown in the top navigation
4. Explore each module!

**Each module has full functionality with multiple sub-pages and features.**

---

**Created:** 2025-11-20
**Purpose:** Help users find all implemented modules
