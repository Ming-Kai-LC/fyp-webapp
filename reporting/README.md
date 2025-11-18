# Reporting Module

## Overview
The Reporting Module provides comprehensive report generation and management capabilities for the COVID-19 Detection System. It enables doctors to generate professional PDF reports, export data to Excel for research, and manage batch report generation.

## Features

### Core Features
1. **PDF Report Generation** - Generate professional medical reports for individual predictions
2. **Batch Report Generation** - Generate multiple reports at once
3. **Multiple Report Templates** - Standard, Detailed, and Summary templates
4. **Excel Export** - Export prediction data for research purposes
5. **Report History & Tracking** - Track downloads and report versions
6. **QR Code Verification** - Include QR codes for report authenticity verification
7. **Digital Signatures** - Include doctor signatures and hospital logos

### Advanced Features
- Report preview before download
- Customizable report templates
- Report versioning
- Download tracking
- Batch job progress monitoring
- Multi-model comparison in reports

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements-reporting.txt
```

### 2. Run Migrations

```bash
python manage.py makemigrations reporting
python manage.py migrate reporting
```

### 3. Create Default Templates

Create default report templates through Django admin or run:

```bash
python manage.py shell
from reporting.models import ReportTemplate
# Create templates (see below)
```

## Usage

### Generating a Single Report

```python
from reporting.services import ReportGenerator
from detection.models import Prediction

# Get prediction
prediction = Prediction.objects.get(id=1)

# Initialize generator
generator = ReportGenerator(
    prediction=prediction,
    template=template,
    include_signature=True,
    include_logo=True,
    include_qr=True,
    custom_notes="Additional medical notes"
)

# Generate report
report = generator.generate(generated_by=request.user)
```

### Batch Report Generation

```python
from reporting.services import BatchReportProcessor
from reporting.models import BatchReportJob

# Create batch job
job = BatchReportJob.objects.create(
    created_by=user,
    template=template,
    total_reports=predictions.count()
)
job.predictions.set(predictions)

# Process batch
processor = BatchReportProcessor(job)
processor.process()
```

### Excel Export

```python
from reporting.services import ExcelExporter
from detection.models import Prediction

# Get predictions
predictions = Prediction.objects.all()

# Generate Excel file
exporter = ExcelExporter(predictions)
excel_file = exporter.generate()
```

## URL Endpoints

- `/reporting/generate/<prediction_id>/` - Generate report form
- `/reporting/view/<report_id>/` - View report details
- `/reporting/download/<report_id>/` - Download PDF report
- `/reporting/list/` - List all reports
- `/reporting/batch/generate/` - Batch generation form
- `/reporting/batch/status/<job_id>/` - Batch job status
- `/reporting/export/excel/` - Export to Excel
- `/reporting/templates/` - Manage templates

## Models

### ReportTemplate
Stores different report templates with customizable HTML and CSS.

### Report
Stores generated reports with metadata, tracking downloads and versions.

### BatchReportJob
Tracks batch report generation jobs with progress monitoring.

## Testing

Run tests with:

```bash
python manage.py test reporting
```

Test coverage includes:
- Model creation and methods
- Report generation
- Excel export
- Batch processing
- View permissions

## Configuration

### Settings (config/settings.py)

```python
# Report settings
SITE_URL = 'http://localhost:8000'  # Change in production
REPORT_LOGO_PATH = BASE_DIR / 'static' / 'images' / 'hospital_logo.png'
REPORT_SIGNATURE_PATH = MEDIA_ROOT / 'signatures'
```

## Dependencies

- **weasyprint** (60.1) - Primary PDF generator
- **xhtml2pdf** (0.2.13) - Fallback PDF generator
- **openpyxl** (3.1.2) - Excel file generation
- **qrcode[pil]** (7.4.2) - QR code generation
- **Pillow** (10.1.0) - Image processing

## Security Considerations

1. **Access Control** - Only doctors and admins can generate reports
2. **Patient Privacy** - Reports contain sensitive medical data
3. **QR Verification** - Reports include QR codes for authenticity
4. **Audit Trail** - All report generations are logged

## File Structure

```
reporting/
├── __init__.py
├── admin.py           # Admin configurations
├── apps.py            # App configuration
├── decorators.py      # Custom decorators (doctor_required)
├── forms.py           # Report generation forms
├── models.py          # Database models
├── services.py        # Business logic (PDF, Excel, Batch)
├── tests.py           # Unit tests
├── urls.py            # URL routing
├── views.py           # View functions
├── migrations/        # Database migrations
└── templates/
    └── reporting/
        ├── generate_report.html
        ├── view_report.html
        ├── report_list.html
        ├── batch_generate.html
        ├── batch_job_status.html
        ├── manage_templates.html
        └── pdf_templates/
            └── report_template.html
```

## Future Enhancements

1. **Multi-language Support** - Add support for multiple languages
2. **Custom Branding** - Per-hospital/clinic branding
3. **Email Reports** - Send reports directly to patients
4. **Report Analytics** - Track report usage and statistics
5. **Celery Integration** - Async batch processing for large jobs
6. **Cloud Storage** - S3 integration for report storage
7. **Report Watermarking** - Enhanced authenticity features

## Support

For issues or questions, please contact:
- Student: Tan Ming Kai (24PMR12003)
- Supervisor: Angkay A/P Subramaniam
- Institution: TAR UMT

## License

This module is part of the COVID-19 Detection System FYP project.
