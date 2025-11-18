# Enhanced Patient Records Module

## Overview
Comprehensive medical history management system for COVID-19 risk assessment and patient care.

## Features Implemented

### Core Features
1. ✅ Complete medical history timeline
2. ✅ Document upload (lab results, prescriptions, discharge summaries, vaccination certificates)
3. ✅ Allergy tracking and alerts
4. ✅ Current medications management
5. ✅ Vaccination records (especially COVID-19 vaccines)
6. ✅ Family medical history
7. ✅ Previous diagnoses and conditions
8. ✅ Surgical history
9. ✅ Search and filter patient records

### Advanced Features
10. ✅ Medical condition risk scoring
11. ✅ Integration with existing Patient model
12. ✅ Patient data export (for patient requests)
13. ✅ Document versioning
14. ✅ Medical summary generation
15. ✅ COVID-19 risk assessment algorithm

## Database Models

### MedicalCondition
Track patient's medical conditions and diagnoses with:
- Severity levels (mild, moderate, severe)
- Status (active, resolved, chronic)
- COVID-19 risk flag
- ICD-10 codes

### Allergy
Track patient allergies with:
- Severity levels (mild, moderate, severe/anaphylaxis)
- Allergy types (medication, food, environmental, other)
- Doctor verification status

### Medication
Track current and past medications with:
- Dosage and frequency
- Status (current, discontinued, completed)
- Prescribing doctor information

### Vaccination
Track vaccination records with:
- COVID-19 vaccine tracking (Pfizer, Moderna, AstraZeneca, Sinovac, etc.)
- Dose number tracking
- Verification document upload
- Adverse reaction tracking

### Surgery
Track surgical history with:
- Procedure codes (CPT)
- Surgeon and hospital information
- Complications and outcomes

### FamilyHistory
Track family medical history for risk assessment

### MedicalDocument
Store medical documents with:
- Document type categorization
- Version control
- OCR text extraction (placeholder)
- Sensitive document flagging

### LifestyleInformation
Track lifestyle factors relevant to COVID-19 risk:
- Smoking status
- Alcohol use
- Exercise level
- Occupational exposure risk

### COVIDRiskScore
Calculate and store COVID-19 risk scores with:
- Age-based scoring
- Comorbidity scoring
- Lifestyle factor scoring
- Vaccination protection scoring
- Personalized recommendations

## URL Routes

```
/medical-records/conditions/ - List medical conditions
/medical-records/conditions/add/ - Add new condition
/medical-records/conditions/<id>/edit/ - Edit condition
/medical-records/conditions/<id>/delete/ - Delete condition

/medical-records/allergies/ - List allergies
/medical-records/allergies/add/ - Add new allergy
/medical-records/allergies/<id>/edit/ - Edit allergy

/medical-records/medications/ - List medications
/medical-records/medications/add/ - Add new medication
/medical-records/medications/<id>/edit/ - Edit medication

/medical-records/vaccinations/ - List vaccinations
/medical-records/vaccinations/add/ - Add new vaccination

/medical-records/documents/ - List medical documents
/medical-records/documents/upload/ - Upload new document
/medical-records/documents/<uuid>/ - View document details
/medical-records/documents/<uuid>/download/ - Download document

/medical-records/summary/<patient_id>/ - Comprehensive medical summary
/medical-records/risk-assessment/<patient_id>/ - COVID-19 risk assessment
```

## Risk Assessment Algorithm

The COVID-19 risk assessment algorithm calculates a comprehensive risk score based on:

### Age Score (0-30 points)
- 80+ years: 30 points
- 70-79 years: 20 points
- 60-69 years: 15 points
- 50-59 years: 10 points
- <50 years: 0 points

### Comorbidity Score (5-15 points per condition)
High-risk conditions include:
- Diabetes
- Heart disease
- Hypertension
- COPD/Asthma
- Chronic kidney disease
- Cancer
- Immunocompromised conditions
- Obesity

Scoring:
- Severe condition: +15 points
- Moderate condition: +10 points
- Mild condition: +5 points

### Lifestyle Score (0-35 points)
- Current smoker: +15 points
- Former smoker: +5 points
- Sedentary lifestyle: +10 points
- Light activity: +5 points
- Occupational exposure: +10 points

### Vaccination Score (-20 to +15 points)
- 4+ doses: -20 points (excellent protection)
- 3 doses: -15 points (good protection)
- 2 doses: -10 points (moderate protection)
- 1 dose: -5 points (basic protection)
- Unvaccinated: +15 points (increased risk)
- Waning immunity (>6 months): +5 points

### Risk Levels
- **Low Risk**: Score < 15
- **Moderate Risk**: Score 15-29
- **High Risk**: Score 30-49
- **Very High Risk**: Score ≥ 50

## Installation & Setup

### 1. Migrations
```bash
python manage.py makemigrations medical_records
python manage.py migrate
```

### 2. Create Superuser (if not exists)
```bash
python manage.py createsuperuser
```

### 3. Access the Module
Navigate to `/medical-records/` after logging in.

## Testing

Run the test suite:
```bash
python manage.py test medical_records
```

Test coverage includes:
- Model creation and validation
- Risk assessment algorithm
- View permissions and access control
- CRUD operations

## File Structure

```
medical_records/
├── __init__.py
├── admin.py           # Django admin configuration
├── apps.py            # App configuration
├── forms.py           # ModelForms for all models
├── models.py          # 9 database models
├── services.py        # Risk assessment service
├── tests.py           # Comprehensive test suite
├── urls.py            # URL routing
├── views.py           # View functions for CRUD operations
├── migrations/        # Database migrations
│   └── __init__.py
├── templates/
│   └── medical_records/
│       ├── base_medical.html           # Base template with sidebar
│       ├── condition_list.html         # Medical conditions list
│       ├── condition_form.html         # Add/Edit condition form
│       ├── condition_confirm_delete.html
│       ├── allergy_list.html           # Allergies list
│       ├── allergy_form.html           # Add/Edit allergy form
│       ├── medication_list.html        # Medications list
│       ├── medication_form.html        # Add/Edit medication form
│       ├── vaccination_list.html       # Vaccinations list
│       ├── vaccination_form.html       # Add vaccination form
│       ├── document_list.html          # Documents list
│       ├── document_form.html          # Upload document form
│       ├── document_detail.html        # Document details
│       ├── medical_summary.html        # Comprehensive summary
│       └── risk_assessment.html        # COVID-19 risk assessment
└── README.md          # This file
```

## Security Considerations

1. **Access Control**: All views require login (`@login_required`)
2. **Patient Privacy**: Users can only access their own medical records
3. **Doctor Access**: Doctors can view patient records with proper permissions
4. **Sensitive Documents**: Flag for documents requiring additional authorization
5. **Audit Trail**: All records track who created/updated them and when

## Integration Points

- **Detection App**: Links to Patient model via ForeignKey
- **Config URLs**: Included at `/medical-records/`
- **Settings**: Added to `INSTALLED_APPS`
- **Media Files**: Documents stored in `media/medical_records/`

## Future Enhancements

1. Document OCR and text extraction (currently placeholder)
2. Drug interaction checking
3. Medical summary PDF export
4. Email notifications for medication reminders
5. Integration with external health APIs
6. Multi-language support

## Developer Notes

- Follow Django best practices and OOP principles
- Use service layer (services.py) for business logic
- Maintain test coverage above 80%
- All forms use Bootstrap 5 styling via crispy_forms
- Mobile-responsive design throughout

## Module Completion Checklist

- [x] Database models defined
- [x] Forms created
- [x] Views implemented
- [x] URL routing configured
- [x] Admin interface configured
- [x] Templates created (14 templates)
- [x] Risk assessment algorithm implemented
- [x] Tests written
- [x] Settings updated
- [x] Documentation created
- [ ] Migrations run (requires Django environment)
- [ ] Production deployment

## Author
Implemented according to specifications in `specs/03_PATIENT_RECORDS_MODULE_SPEC.md`

## License
Part of TAR UMT FYP - COVID-19 Detection System
