# COVID-19 Detection System - Module Details

**Project:** COVID-19 Detection using CrossViT
**Student:** Tan Ming Kai (24PMR12003)
**Supervisor:** Angkay A/P Subramaniam
**University:** TAR UMT

---

## System Overview

This Django-based web application provides a comprehensive COVID-19 detection system using AI models (CrossViT and 5 baseline models) with complete patient management, medical records, appointments, reporting, and audit capabilities.

The system consists of **10 custom Django modules** working together to provide a complete healthcare management solution.

---

## Module Details

### 1. Detection Module (`detection/`)

**Purpose:** Core COVID-19 detection system with AI model integration and patient management

**Key Responsibilities:**
- Patient profile and demographic management
- X-ray image upload and preprocessing (CLAHE enhancement)
- Multi-model AI prediction (6 models: CrossViT, ResNet-50, DenseNet-121, EfficientNet-B0, ViT-Base, Swin-Tiny)
- Explainability visualizations (Grad-CAM heatmaps, attention maps)
- Prediction validation by doctors

**Database Models:**
- `UserProfile` - Extended user information with role-based access control (admin, doctor, patient)
- `Patient` - Patient demographics, medical history, contact information
- `XRayImage` - Uploaded chest X-ray images with original and processed versions
- `Prediction` - Multi-model predictions with consensus diagnosis, confidence scores, and explainability data

**Key Features:**
- **Spotlight 1:** Multi-Model Comparison - All 6 AI models run on each X-ray for comparison
- **Spotlight 2:** Explainability - Grad-CAM and CrossViT attention maps show AI decision-making
- Role-based access control (patients see own data, doctors see all)
- Automatic UserProfile creation via Django signals

**File Locations:**
- Models: `detection/models.py:14-403`
- Views: `detection/views.py`
- Services: `detection/services.py`

---

### 2. Medical Records Module (`medical_records/`)

**Purpose:** Comprehensive electronic medical records (EMR) system for patient health history

**Key Responsibilities:**
- Track patient medical conditions, diagnoses, and treatments
- Manage allergies and adverse reactions
- Record current and past medications
- Vaccination tracking (especially COVID-19 vaccines)
- Surgical history
- Family medical history
- Document management (lab results, prescriptions, certificates)
- Lifestyle information tracking
- COVID-19 risk assessment

**Database Models:**
- `MedicalCondition` - Diagnoses, conditions, severity, status (active/resolved/chronic)
- `Allergy` - Allergens, severity, reaction details, verification status
- `Medication` - Current and past medications, dosage, frequency, purpose
- `Vaccination` - COVID-19 and other vaccines with verification documents
- `Surgery` - Surgical history with dates, surgeons, outcomes
- `FamilyHistory` - Family medical conditions for genetic risk assessment
- `MedicalDocument` - PDF/image storage with OCR text extraction for searchability
- `LifestyleInformation` - Smoking, alcohol, exercise, occupational exposure
- `COVIDRiskScore` - Calculated COVID-19 risk based on age, comorbidities, lifestyle, vaccination

**Key Features:**
- ICD-10 code support for standardized diagnosis tracking
- Document versioning and replacement tracking
- Sensitive document access control
- Risk factor identification for COVID-19
- HIPAA-compliant medical record keeping

**File Location:** `medical_records/models.py:1-464`

---

### 3. Dashboards Module (`dashboards/`)

**Purpose:** Customizable role-based dashboards with widgets

**Key Responsibilities:**
- User dashboard customization and preferences
- Widget layout management
- Role-based widget visibility
- Theme and auto-refresh settings

**Database Models:**
- `DashboardPreference` - User-specific dashboard settings, widget layout, theme (light/dark)
- `DashboardWidget` - Available widgets (statistics, charts, tables, calendars, notifications)

**Key Features:**
- Drag-and-drop widget positioning (via JSON storage)
- Role-based widget access control
- Auto-refresh capabilities
- Multiple widget types (statistics cards, charts, tables, calendars, notifications, quick actions)

**File Location:** `dashboards/models.py:1-100`

---

### 4. Reporting Module (`reporting/`)

**Purpose:** Generate, store, and distribute PDF reports for predictions and medical data

**Key Responsibilities:**
- Generate PDF reports from predictions
- Template-based report generation
- Batch report processing
- Report delivery tracking
- Digital signatures and QR codes

**Database Models:**
- `ReportTemplate` - Customizable HTML/CSS templates for different report types
- `Report` - Generated PDF reports with metadata, delivery tracking, version control
- `BatchReportJob` - Batch generation jobs for multiple reports with progress tracking

**Key Features:**
- Multiple report types (standard, detailed, summary, research)
- Hospital branding (logo, signature, QR code)
- Email delivery and download tracking
- Batch processing for multiple patients
- Report versioning and status tracking (draft, generated, sent, printed)

**File Location:** `reporting/models.py:1-134`

---

### 5. Audit Module (`audit/`)

**Purpose:** Comprehensive audit trail, security monitoring, and HIPAA/GDPR compliance

**Key Responsibilities:**
- Log all system activities and user actions
- Track patient data access (HIPAA compliance)
- Monitor login attempts and security threats
- Track data changes with before/after values
- Generate compliance reports
- Enforce data retention policies
- Real-time security alerting

**Database Models:**
- `AuditLog` - Comprehensive activity logging (create, read, update, delete, login, export, etc.)
- `DataAccessLog` - Patient data access tracking for HIPAA compliance
- `LoginAttempt` - All login attempts with security flags for suspicious activity
- `DataChange` - Change history for critical medical data with field-level tracking
- `ComplianceReport` - HIPAA, GDPR, security audit reports
- `DataRetentionPolicy` - Define and enforce data retention rules
- `SecurityAlert` - Real-time security alerts (failed logins, unusual access, bulk exports)

**Key Features:**
- Full audit trail with who, what, when, where context
- IP address and user agent tracking
- Generic foreign keys for tracking changes to any model
- Before/after value comparison
- Automated security alerts with severity levels
- Compliance reporting for regulatory review
- Data retention policy enforcement

**File Location:** `audit/models.py:1-352`

---

### 6. Notifications Module (`notifications/`)

**Purpose:** Multi-channel notification system for patient and doctor communication

**Key Responsibilities:**
- Send notifications via email, SMS, and in-app channels
- Manage notification templates
- Track notification delivery status
- User notification preferences
- Priority-based delivery
- Quiet hours support

**Database Models:**
- `NotificationTemplate` - Email/SMS/in-app templates with placeholder support
- `Notification` - Individual notification instances with status tracking
- `NotificationPreference` - User-specific notification settings and quiet hours
- `NotificationLog` - Delivery attempt logging for debugging

**Key Features:**
- Multi-channel delivery (email, SMS, in-app)
- Template-based notifications with variable substitution
- Priority levels (low, normal, high, critical)
- Critical notifications bypass user preferences
- Quiet hours scheduling
- Daily digest option
- Read/unread status tracking
- Related object linking (predictions, appointments)

**Notification Types:**
- Prediction results ready
- Critical COVID-19 positive results
- Appointment reminders and confirmations
- Report generation completion
- Doctor notes added
- Test result updates

**File Location:** `notifications/models.py:1-197`

---

### 7. Appointments Module (`appointments/`)

**Purpose:** Complete appointment scheduling and management system

**Key Responsibilities:**
- Manage doctor schedules and availability
- Book and manage patient appointments
- Send appointment reminders
- Handle waitlist for fully booked slots
- Track doctor leave and holidays
- Support virtual consultations

**Database Models:**
- `DoctorSchedule` - Weekly recurring schedules, working hours, slot duration
- `Appointment` - Individual appointments with status tracking, reminders, and follow-ups
- `AppointmentReminder` - Automated reminders (24h, 2h before)
- `Waitlist` - Patient waitlist for fully booked slots
- `DoctorLeave` - Doctor leave/holiday tracking to block appointments

**Key Features:**
- Recurring weekly schedules for doctors
- Configurable appointment slot duration
- Multiple appointment types (consultation, follow-up, X-ray review, virtual, emergency)
- Status tracking (scheduled, confirmed, in progress, completed, cancelled, no-show)
- Automated reminders via email/SMS
- Virtual consultation support with video links
- Follow-up appointment linking
- No-show tracking
- Doctor notes after appointment completion

**Appointment Types:**
- General consultation
- Follow-up appointments
- X-ray review
- Results discussion
- Virtual consultation
- Emergency

**File Location:** `appointments/models.py:1-351`

---

### 8. Analytics Module (`analytics/`)

**Purpose:** Track system metrics, model performance, and generate custom analytics reports

**Key Responsibilities:**
- Daily/weekly/monthly statistical snapshots
- Model performance tracking over time
- Custom report generation
- Data export for research
- Trend analysis

**Database Models:**
- `AnalyticsSnapshot` - Daily/weekly/monthly snapshots of key metrics
- `ModelPerformanceMetric` - Individual model performance tracking (accuracy, precision, recall, F1)
- `CustomReport` - User-defined custom reports with filters and chart types
- `DataExport` - Track data exports with anonymization options

**Key Features:**
- Automated daily snapshots of system metrics
- Per-model performance tracking (all 6 AI models)
- Model agreement rate analysis
- Demographic analysis
- Doctor productivity reports
- Patient outcome tracking
- Multiple chart types (line, bar, pie, heatmap, table)
- Data export in CSV, Excel, JSON formats
- Anonymization for research data

**Tracked Metrics:**
- Total predictions and breakdown by diagnosis
- Patient statistics
- Model accuracy and confidence
- Inference time performance
- Model consensus/agreement rates

**File Location:** `analytics/models.py:1-170`

---

### 9. API Module (`api/`)

**Purpose:** RESTful API for mobile apps and third-party integrations with JWT authentication

**Key Responsibilities:**
- Provide REST API endpoints for all major features
- JWT token-based authentication
- Role-based API access control
- API documentation via Swagger/OpenAPI
- Mobile app integration

**API Endpoints:**

#### Authentication
- `POST /api/register/` - User registration with JWT tokens
- `POST /api/login/` - Login and get JWT access/refresh tokens
- `POST /api/logout/` - Logout and blacklist refresh token

#### Predictions
- `GET /api/predictions/` - List predictions (filtered by role)
- `GET /api/predictions/{id}/` - Get prediction details
- `POST /api/predictions/upload/` - Upload X-ray and get prediction
- `GET /api/predictions/{id}/explain/` - Get explainability data (Grad-CAM, attention maps)
- `PATCH /api/predictions/{id}/validate/` - Validate prediction (doctor only)

#### Patients
- `GET /api/patients/` - List patients (doctor/admin only)
- `GET /api/patients/{id}/` - Get patient details
- `GET /api/patients/me/` - Get own patient profile
- `PATCH /api/patients/me/` - Update own patient profile
- `GET /api/patients/{id}/predictions/` - Get patient's predictions
- `GET /api/patients/{id}/appointments/` - Get patient's appointments

#### Appointments
- `GET /api/appointments/` - List appointments (filtered by role)
- `POST /api/appointments/` - Book new appointment
- `GET /api/appointments/{id}/` - Get appointment details
- `PATCH /api/appointments/{id}/` - Update appointment
- `DELETE /api/appointments/{id}/` - Cancel appointment
- `GET /api/appointments/available_slots/` - Get available time slots

**Key Features:**
- JWT authentication with token refresh and blacklisting
- Role-based access control via custom permissions
- API throttling (100/day for anonymous, 1000/day for authenticated)
- Swagger/OpenAPI documentation
- CORS support for cross-origin requests
- Pagination (20 items per page)

**File Locations:**
- Views: `api/views.py:1-344`
- Serializers: `api/serializers.py`
- Permissions: `api/permissions.py`
- URLs: `api/urls.py`

---

### 10. Accounts Module (`accounts/`)

**Purpose:** User authentication, registration, and account management (web interface)

**Key Responsibilities:**
- User registration and login (web forms)
- Password reset and change
- User profile management
- Session management

**Note:** This module handles web-based authentication, while the `api` module handles JWT-based API authentication. The `UserProfile` model is actually defined in the `detection` module and shared across the system.

**File Location:** `accounts/` (uses `detection.models.UserProfile`)

---

## Module Dependencies

### Core Dependencies
- **Detection Module** - Core module used by most others (Patient, Prediction models)
- **Accounts/Detection** - UserProfile used throughout system

### Module Integration
```
detection (core)
├── medical_records → Patient
├── reporting → Prediction, Patient
├── notifications → Prediction, Patient
├── appointments → Patient
├── dashboards → User preferences
├── audit → All models (via generic foreign keys)
├── analytics → Prediction data
└── api → All modules (REST interface)
```

---

## Technology Stack

**Backend Framework:**
- Django 4.x
- Django REST Framework (API)
- Django REST Framework SimpleJWT (authentication)

**Database:**
- SQLite (development)
- PostgreSQL (production-ready)

**Frontend:**
- Bootstrap 5 (responsive design)
- Crispy Forms (form styling)
- Chart.js (analytics visualizations)

**API & Documentation:**
- DRF YASG (Swagger/OpenAPI)
- CORS Headers (cross-origin support)

**AI/ML (Planned):**
- PyTorch (model inference)
- CrossViT, ResNet-50, DenseNet-121, EfficientNet-B0, ViT-Base, Swin-Tiny
- Grad-CAM for explainability

**Security & Compliance:**
- HIPAA-compliant audit logging
- GDPR data retention policies
- JWT authentication with token blacklisting
- Role-based access control (RBAC)
- IP address and user agent tracking

---

## User Roles

### 1. Patient
- View own medical records and X-rays
- Upload X-rays (via doctor)
- View own predictions and reports
- Book appointments
- Receive notifications

### 2. Doctor
- View all patients and medical records
- Upload and analyze X-rays
- Validate predictions
- Add doctor notes
- Manage appointments
- Generate reports

### 3. Administrator
- Full system access
- User management
- Audit log review
- Compliance reporting
- System configuration
- Analytics and exports

---

## Key Features Summary

### AI & Detection
- Multi-model COVID-19 detection (6 models)
- Explainable AI with Grad-CAM and attention maps
- CLAHE preprocessing for enhanced X-rays
- Model comparison and consensus

### Medical Records
- Complete EMR system
- Allergy and medication tracking
- Vaccination records
- COVID-19 risk assessment
- Document management with OCR

### Compliance & Security
- Full audit trail
- HIPAA/GDPR compliance
- Security monitoring and alerts
- Data retention policies
- Access logging

### Patient Care
- Appointment scheduling
- Multi-channel notifications
- Report generation and delivery
- Virtual consultation support
- Waitlist management

### Analytics & Reporting
- Real-time dashboards
- Model performance tracking
- Custom reports
- Data exports for research
- Trend analysis

### Integration
- RESTful API for mobile apps
- JWT authentication
- Swagger documentation
- CORS support
- Third-party integration ready

---

## File Structure Summary

```
fyp-webapp/
├── accounts/              # Web-based authentication
├── analytics/             # Analytics and reporting
├── api/                   # REST API with JWT
├── appointments/          # Appointment scheduling
├── audit/                 # Audit logging and compliance
├── config/                # Django settings and configuration
├── dashboards/            # Customizable dashboards
├── detection/             # Core COVID-19 detection (MAIN MODULE)
├── medical_records/       # Electronic medical records
├── notifications/         # Multi-channel notifications
├── reporting/             # PDF report generation
├── static/                # CSS, JavaScript, images
├── templates/             # HTML templates
├── media/                 # Uploaded files (X-rays, documents)
│   ├── xrays/            # X-ray images
│   ├── heatmaps/         # Grad-CAM visualizations
│   ├── attention/        # Attention maps
│   ├── medical_records/  # Medical documents
│   ├── reports/          # Generated PDFs
│   └── ...
├── tests/                 # Test suite
├── manage.py              # Django management script
└── requirements.txt       # Python dependencies
```

---

## Database Models Count

- **Detection:** 4 models (UserProfile, Patient, XRayImage, Prediction)
- **Medical Records:** 9 models (MedicalCondition, Allergy, Medication, Vaccination, Surgery, FamilyHistory, MedicalDocument, LifestyleInformation, COVIDRiskScore)
- **Dashboards:** 2 models (DashboardPreference, DashboardWidget)
- **Reporting:** 3 models (ReportTemplate, Report, BatchReportJob)
- **Audit:** 7 models (AuditLog, DataAccessLog, LoginAttempt, DataChange, ComplianceReport, DataRetentionPolicy, SecurityAlert)
- **Notifications:** 4 models (NotificationTemplate, Notification, NotificationPreference, NotificationLog)
- **Appointments:** 5 models (DoctorSchedule, Appointment, AppointmentReminder, Waitlist, DoctorLeave)
- **Analytics:** 4 models (AnalyticsSnapshot, ModelPerformanceMetric, CustomReport, DataExport)

**Total: 38 custom database models**

---

## System Configuration (from settings.py)

**Timezone:** Asia/Kuala_Lumpur
**Debug Mode:** True (development)
**Database:** SQLite (development), PostgreSQL-ready
**Media Storage:** Local filesystem with organized subdirectories
**Static Files:** Bootstrap 5, custom CSS/JS
**File Upload Limit:** 10MB
**Allowed Image Formats:** .jpg, .jpeg, .png, .dcm

**ML Settings:**
- Inference Batch Size: 1 (optimized for RTX 4060 8GB VRAM)
- Mixed Precision: Enabled
- Model Weights Directory: `static/ml_models/`

**API Settings:**
- Authentication: JWT (SimpleJWT)
- Access Token Lifetime: 60 minutes
- Refresh Token Lifetime: 7 days
- Token Rotation: Enabled
- Rate Limiting: 100/day (anonymous), 1000/day (authenticated)

---

## Next Steps for Implementation

1. **ML Model Integration** - Implement actual PyTorch model loading and inference
2. **Email/SMS Configuration** - Configure SMTP and Twilio for notifications
3. **Production Deployment** - Configure PostgreSQL, HTTPS, environment variables
4. **Frontend Enhancement** - Add AJAX, real-time updates, better visualizations
5. **Mobile App** - Build React Native/Flutter app using the REST API
6. **Testing** - Complete unit tests, integration tests, E2E tests
7. **Documentation** - User manual, API documentation, deployment guide

---

**Document Generated:** 2025-11-20
**System Version:** 1.0.0
**Status:** Development Phase
