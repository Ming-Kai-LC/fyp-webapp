# Reporting Module - Detailed Specification

## Module Information
- **Module Name:** reporting
- **Priority:** CRITICAL (Phase 1)
- **Estimated Effort:** 2-3 days
- **Dependencies:** detection app (Prediction, XRayImage models)

## Purpose
Generate professional medical reports for COVID-19 predictions, enabling doctors to provide official documentation to patients and for medical records.

## Features

### Core Features
1. PDF report generation for individual predictions
2. Batch PDF generation for multiple patients
3. Multiple report templates (Standard, Detailed, Summary)
4. Print-optimized layouts
5. Doctor signature and hospital logo integration
6. Export predictions to CSV/Excel for research
7. Report preview before download
8. Report versioning and history

### Advanced Features
9. Multi-language support (English primary, add others as needed)
10. Custom report branding per hospital/clinic
11. QR code for report verification
12. Watermarking for authenticity

---

## Database Models

### File: `reporting/models.py`

```python
from django.db import models
from django.conf import settings
from detection.models import Prediction, Patient
import uuid

class ReportTemplate(models.Model):
    """
    Defines different report templates with customizable layouts
    """
    TEMPLATE_TYPES = (
        ('standard', 'Standard Report'),
        ('detailed', 'Detailed Report'),
        ('summary', 'Summary Report'),
        ('research', 'Research Export'),
    )

    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    description = models.TextField(blank=True)
    html_template = models.TextField(help_text="HTML template content")
    css_styles = models.TextField(blank=True, help_text="Custom CSS")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['template_type', 'name']

    def __str__(self):
        return f"{self.get_template_type_display()} - {self.name}"


class Report(models.Model):
    """
    Stores generated reports with metadata for tracking and versioning
    """
    REPORT_STATUS = (
        ('draft', 'Draft'),
        ('generated', 'Generated'),
        ('sent', 'Sent to Patient'),
        ('printed', 'Printed'),
    )

    report_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    prediction = models.ForeignKey(Prediction, on_delete=models.CASCADE, related_name='reports')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='reports')
    template = models.ForeignKey(ReportTemplate, on_delete=models.SET_NULL, null=True)

    # Report metadata
    title = models.CharField(max_length=200, default="COVID-19 Detection Report")
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='generated_reports')
    generated_at = models.DateTimeField(auto_now_add=True)

    # File storage
    pdf_file = models.FileField(upload_to='reports/pdf/%Y/%m/%d/', null=True, blank=True)
    file_size = models.IntegerField(null=True, blank=True, help_text="File size in bytes")

    # Status tracking
    status = models.CharField(max_length=20, choices=REPORT_STATUS, default='draft')
    version = models.IntegerField(default=1)

    # Signature and branding
    include_signature = models.BooleanField(default=True)
    include_hospital_logo = models.BooleanField(default=True)
    include_qr_code = models.BooleanField(default=True)

    # Delivery tracking
    sent_to_email = models.EmailField(blank=True, null=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    downloaded_count = models.IntegerField(default=0)
    last_downloaded_at = models.DateTimeField(null=True, blank=True)

    # Custom notes
    custom_notes = models.TextField(blank=True, help_text="Additional notes for the report")

    class Meta:
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['report_id']),
            models.Index(fields=['patient', '-generated_at']),
        ]

    def __str__(self):
        return f"Report {self.report_id} - {self.patient.user.get_full_name()} - {self.generated_at.strftime('%Y-%m-%d')}"

    def increment_download_count(self):
        from django.utils import timezone
        self.downloaded_count += 1
        self.last_downloaded_at = timezone.now()
        self.save(update_fields=['downloaded_count', 'last_downloaded_at'])


class BatchReportJob(models.Model):
    """
    Tracks batch report generation jobs for multiple patients
    """
    JOB_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    job_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Job configuration
    predictions = models.ManyToManyField(Prediction, related_name='batch_jobs')
    template = models.ForeignKey(ReportTemplate, on_delete=models.SET_NULL, null=True)

    # Status
    status = models.CharField(max_length=20, choices=JOB_STATUS, default='pending')
    total_reports = models.IntegerField(default=0)
    completed_reports = models.IntegerField(default=0)
    failed_reports = models.IntegerField(default=0)

    # Output
    zip_file = models.FileField(upload_to='reports/batch/%Y/%m/%d/', null=True, blank=True)
    error_log = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Batch Job {self.job_id} - {self.status}"

    def get_progress_percentage(self):
        if self.total_reports == 0:
            return 0
        return int((self.completed_reports / self.total_reports) * 100)
```

---

## Views

### File: `reporting/views.py`

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse, JsonResponse, Http404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Report, ReportTemplate, BatchReportJob
from detection.models import Prediction, Patient
from .forms import ReportGenerationForm, BatchReportForm, ReportTemplateForm
from .services import ReportGenerator, ExcelExporter, BatchReportProcessor
from .decorators import doctor_required
import mimetypes


@login_required
@doctor_required
def generate_report(request, prediction_id):
    """
    Generate a PDF report for a specific prediction
    """
    prediction = get_object_or_404(Prediction, id=prediction_id)

    # Check permissions (doctor can view all, patient only their own)
    if not request.user.profile.is_doctor() and not request.user.profile.is_admin():
        if prediction.xray.patient.user != request.user:
            messages.error(request, "You don't have permission to access this report.")
            return redirect('detection:patient_dashboard')

    if request.method == 'POST':
        form = ReportGenerationForm(request.POST)
        if form.is_valid():
            try:
                # Generate report using service
                generator = ReportGenerator(
                    prediction=prediction,
                    template=form.cleaned_data['template'],
                    include_signature=form.cleaned_data['include_signature'],
                    include_logo=form.cleaned_data['include_hospital_logo'],
                    include_qr=form.cleaned_data['include_qr_code'],
                    custom_notes=form.cleaned_data.get('custom_notes', '')
                )

                report = generator.generate(generated_by=request.user)

                messages.success(request, "Report generated successfully!")
                return redirect('reporting:view_report', report_id=report.report_id)

            except Exception as e:
                messages.error(request, f"Error generating report: {str(e)}")

    else:
        form = ReportGenerationForm()

    context = {
        'prediction': prediction,
        'form': form,
        'patient': prediction.xray.patient,
    }
    return render(request, 'reporting/generate_report.html', context)


@login_required
def view_report(request, report_id):
    """
    Preview report in browser before downloading
    """
    report = get_object_or_404(Report, report_id=report_id)

    # Check permissions
    if not request.user.profile.is_doctor() and not request.user.profile.is_admin():
        if report.patient.user != request.user:
            raise Http404("Report not found")

    context = {
        'report': report,
        'prediction': report.prediction,
        'patient': report.patient,
    }
    return render(request, 'reporting/view_report.html', context)


@login_required
def download_report(request, report_id):
    """
    Download PDF report file
    """
    report = get_object_or_404(Report, report_id=report_id)

    # Check permissions
    if not request.user.profile.is_doctor() and not request.user.profile.is_admin():
        if report.patient.user != request.user:
            raise Http404("Report not found")

    if not report.pdf_file:
        messages.error(request, "Report file not found. Please regenerate the report.")
        return redirect('reporting:view_report', report_id=report_id)

    # Increment download counter
    report.increment_download_count()

    # Serve file
    response = FileResponse(report.pdf_file.open('rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="COVID_Report_{report.report_id}.pdf"'
    return response


@login_required
@doctor_required
def report_list(request):
    """
    List all reports with filtering and search
    """
    reports = Report.objects.select_related('patient__user', 'prediction', 'generated_by').all()

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        reports = reports.filter(
            Q(patient__user__first_name__icontains=search_query) |
            Q(patient__user__last_name__icontains=search_query) |
            Q(report_id__icontains=search_query)
        )

    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        reports = reports.filter(status=status_filter)

    # Filter by date range
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if date_from:
        reports = reports.filter(generated_at__gte=date_from)
    if date_to:
        reports = reports.filter(generated_at__lte=date_to)

    context = {
        'reports': reports,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'reporting/report_list.html', context)


@login_required
@doctor_required
def batch_generate_reports(request):
    """
    Generate reports for multiple predictions at once
    """
    if request.method == 'POST':
        form = BatchReportForm(request.POST)
        if form.is_valid():
            try:
                # Create batch job
                job = BatchReportJob.objects.create(
                    created_by=request.user,
                    template=form.cleaned_data['template'],
                    total_reports=form.cleaned_data['predictions'].count()
                )
                job.predictions.set(form.cleaned_data['predictions'])

                # Process in background (or synchronously for now)
                processor = BatchReportProcessor(job)
                processor.process()

                messages.success(request, f"Batch job created! Generating {job.total_reports} reports...")
                return redirect('reporting:batch_job_status', job_id=job.job_id)

            except Exception as e:
                messages.error(request, f"Error creating batch job: {str(e)}")

    else:
        form = BatchReportForm()

    context = {
        'form': form,
    }
    return render(request, 'reporting/batch_generate.html', context)


@login_required
@doctor_required
def batch_job_status(request, job_id):
    """
    View status of batch report generation job
    """
    job = get_object_or_404(BatchReportJob, job_id=job_id)

    context = {
        'job': job,
        'progress': job.get_progress_percentage(),
    }
    return render(request, 'reporting/batch_job_status.html', context)


@login_required
@doctor_required
def download_batch_reports(request, job_id):
    """
    Download ZIP file containing all batch reports
    """
    job = get_object_or_404(BatchReportJob, job_id=job_id)

    if job.status != 'completed':
        messages.error(request, "Batch job is not completed yet.")
        return redirect('reporting:batch_job_status', job_id=job_id)

    if not job.zip_file:
        messages.error(request, "Batch report file not found.")
        return redirect('reporting:batch_job_status', job_id=job_id)

    # Serve ZIP file
    response = FileResponse(job.zip_file.open('rb'), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="COVID_Reports_Batch_{job.job_id}.zip"'
    return response


@login_required
@doctor_required
def export_to_excel(request):
    """
    Export predictions data to Excel for research
    """
    # Get filter parameters
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    diagnosis_filter = request.GET.get('diagnosis', '')

    # Filter predictions
    predictions = Prediction.objects.select_related('xray__patient__user').all()

    if date_from:
        predictions = predictions.filter(xray__upload_date__gte=date_from)
    if date_to:
        predictions = predictions.filter(xray__upload_date__lte=date_to)
    if diagnosis_filter:
        predictions = predictions.filter(final_diagnosis=diagnosis_filter)

    # Generate Excel file
    exporter = ExcelExporter(predictions)
    excel_file = exporter.generate()

    # Serve file
    response = HttpResponse(
        excel_file.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="COVID_Predictions_Export_{timezone.now().strftime("%Y%m%d")}.xlsx"'
    return response


@login_required
@doctor_required
def manage_templates(request):
    """
    Manage report templates (CRUD operations)
    """
    templates = ReportTemplate.objects.filter(is_active=True)

    context = {
        'templates': templates,
    }
    return render(request, 'reporting/manage_templates.html', context)


# API endpoint for AJAX progress checking
@login_required
@doctor_required
def batch_job_progress_api(request, job_id):
    """
    API endpoint to check batch job progress (for AJAX polling)
    """
    job = get_object_or_404(BatchReportJob, job_id=job_id)

    return JsonResponse({
        'status': job.status,
        'total_reports': job.total_reports,
        'completed_reports': job.completed_reports,
        'failed_reports': job.failed_reports,
        'progress': job.get_progress_percentage(),
    })
```

---

## Forms

### File: `reporting/forms.py`

```python
from django import forms
from .models import ReportTemplate, Report
from detection.models import Prediction


class ReportGenerationForm(forms.Form):
    """
    Form for configuring single report generation
    """
    template = forms.ModelChoiceField(
        queryset=ReportTemplate.objects.filter(is_active=True, template_type__in=['standard', 'detailed', 'summary']),
        required=True,
        label="Report Template",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    include_signature = forms.BooleanField(
        required=False,
        initial=True,
        label="Include Doctor Signature",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    include_hospital_logo = forms.BooleanField(
        required=False,
        initial=True,
        label="Include Hospital Logo",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    include_qr_code = forms.BooleanField(
        required=False,
        initial=True,
        label="Include QR Code for Verification",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    custom_notes = forms.CharField(
        required=False,
        label="Additional Notes",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Add any additional notes or recommendations for the report...'
        })
    )


class BatchReportForm(forms.Form):
    """
    Form for batch report generation
    """
    predictions = forms.ModelMultipleChoiceField(
        queryset=Prediction.objects.all(),
        required=True,
        label="Select Predictions",
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )

    template = forms.ModelChoiceField(
        queryset=ReportTemplate.objects.filter(is_active=True),
        required=True,
        label="Report Template",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show predictions that don't have reports yet (optional)
        # self.fields['predictions'].queryset = Prediction.objects.filter(reports__isnull=True)


class ReportTemplateForm(forms.ModelForm):
    """
    Form for creating/editing report templates
    """
    class Meta:
        model = ReportTemplate
        fields = ['name', 'template_type', 'description', 'html_template', 'css_styles', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'template_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'html_template': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'style': 'font-family: monospace;'}),
            'css_styles': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'style': 'font-family: monospace;'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
```

---

## Services

### File: `reporting/services.py`

```python
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from .models import Report, BatchReportJob
from io import BytesIO
import qrcode
import zipfile
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill


class ReportGenerator:
    """
    Service class for generating PDF reports from predictions
    """
    def __init__(self, prediction, template, include_signature=True,
                 include_logo=True, include_qr=True, custom_notes=''):
        self.prediction = prediction
        self.template = template
        self.include_signature = include_signature
        self.include_logo = include_logo
        self.include_qr = include_qr
        self.custom_notes = custom_notes

    def generate(self, generated_by):
        """
        Generate PDF report and save to database
        """
        # Create Report object
        report = Report.objects.create(
            prediction=self.prediction,
            patient=self.prediction.xray.patient,
            template=self.template,
            generated_by=generated_by,
            include_signature=self.include_signature,
            include_hospital_logo=self.include_logo,
            include_qr_code=self.include_qr,
            custom_notes=self.custom_notes,
            status='generated'
        )

        # Generate QR code if needed
        qr_code_data = None
        if self.include_qr:
            qr_code_data = self._generate_qr_code(report)

        # Prepare context for template
        context = {
            'report': report,
            'prediction': self.prediction,
            'patient': self.prediction.xray.patient,
            'xray': self.prediction.xray,
            'models': self.prediction.get_all_predictions(),
            'best_model': self.prediction.get_best_model(),
            'qr_code': qr_code_data,
            'generated_at': timezone.now(),
        }

        # Render HTML from template
        html_content = render_to_string(
            'reporting/pdf_templates/report_template.html',
            context
        )

        # Convert HTML to PDF using WeasyPrint or similar
        pdf_file = self._html_to_pdf(html_content)

        # Save PDF file
        report.pdf_file.save(
            f'report_{report.report_id}.pdf',
            pdf_file,
            save=True
        )

        report.file_size = report.pdf_file.size
        report.save(update_fields=['file_size'])

        return report

    def _generate_qr_code(self, report):
        """
        Generate QR code for report verification
        """
        # QR code contains report URL or verification code
        verification_url = f"{settings.SITE_URL}/reporting/verify/{report.report_id}/"

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(verification_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64 for embedding in HTML
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        import base64
        return base64.b64encode(buffer.getvalue()).decode()

    def _html_to_pdf(self, html_content):
        """
        Convert HTML content to PDF using WeasyPrint
        """
        # Import here to avoid dependency issues if not installed
        try:
            from weasyprint import HTML, CSS
            from django.core.files.base import ContentFile

            # Generate PDF
            pdf_bytes = HTML(string=html_content).write_pdf()

            return ContentFile(pdf_bytes)

        except ImportError:
            # Fallback: use xhtml2pdf or reportlab
            from xhtml2pdf import pisa

            pdf_buffer = BytesIO()
            pisa.CreatePDF(html_content, dest=pdf_buffer)
            pdf_buffer.seek(0)

            return ContentFile(pdf_buffer.getvalue())


class BatchReportProcessor:
    """
    Service class for processing batch report generation jobs
    """
    def __init__(self, batch_job):
        self.batch_job = batch_job

    def process(self):
        """
        Process all predictions in the batch job
        """
        self.batch_job.status = 'processing'
        self.batch_job.save()

        reports = []

        for prediction in self.batch_job.predictions.all():
            try:
                generator = ReportGenerator(
                    prediction=prediction,
                    template=self.batch_job.template,
                )

                report = generator.generate(generated_by=self.batch_job.created_by)
                reports.append(report)

                self.batch_job.completed_reports += 1
                self.batch_job.save(update_fields=['completed_reports'])

            except Exception as e:
                self.batch_job.failed_reports += 1
                self.batch_job.error_log += f"\nFailed for prediction {prediction.id}: {str(e)}"
                self.batch_job.save(update_fields=['failed_reports', 'error_log'])

        # Create ZIP file with all PDFs
        if reports:
            zip_file = self._create_zip(reports)
            self.batch_job.zip_file.save(
                f'batch_{self.batch_job.job_id}.zip',
                zip_file,
                save=True
            )

        self.batch_job.status = 'completed'
        self.batch_job.completed_at = timezone.now()
        self.batch_job.save()

    def _create_zip(self, reports):
        """
        Create ZIP file containing all report PDFs
        """
        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for report in reports:
                if report.pdf_file:
                    zip_file.writestr(
                        f'report_{report.report_id}.pdf',
                        report.pdf_file.read()
                    )

        zip_buffer.seek(0)
        from django.core.files.base import ContentFile
        return ContentFile(zip_buffer.getvalue())


class ExcelExporter:
    """
    Service class for exporting prediction data to Excel
    """
    def __init__(self, predictions_queryset):
        self.predictions = predictions_queryset

    def generate(self):
        """
        Generate Excel file with prediction data
        """
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "COVID-19 Predictions"

        # Define headers
        headers = [
            'Report ID', 'Patient Name', 'Patient Age', 'Patient Gender',
            'Upload Date', 'Final Diagnosis', 'Confidence', 'Best Model',
            'CrossViT Prediction', 'CrossViT Confidence',
            'ResNet-50 Prediction', 'ResNet-50 Confidence',
            'DenseNet-121 Prediction', 'DenseNet-121 Confidence',
            'EfficientNet Prediction', 'EfficientNet Confidence',
            'ViT Prediction', 'ViT Confidence',
            'Swin Prediction', 'Swin Confidence',
            'Inference Time (ms)', 'Validated', 'Doctor Notes'
        ]

        # Write headers
        for col, header in enumerate(headers, start=1):
            cell = sheet.cell(row=1, column=col)
            cell.value = header
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            cell.font = Font(bold=True, color="FFFFFF")

        # Write data
        for row, prediction in enumerate(self.predictions, start=2):
            patient = prediction.xray.patient

            data = [
                str(prediction.id),
                patient.user.get_full_name(),
                patient.age,
                patient.gender,
                prediction.xray.upload_date.strftime('%Y-%m-%d %H:%M'),
                prediction.final_diagnosis,
                f"{prediction.consensus_confidence:.2f}%",
                prediction.get_best_model(),
                prediction.crossvit_prediction,
                f"{prediction.crossvit_confidence:.2f}%",
                prediction.resnet50_prediction,
                f"{prediction.resnet50_confidence:.2f}%",
                prediction.densenet121_prediction,
                f"{prediction.densenet121_confidence:.2f}%",
                prediction.efficientnet_prediction,
                f"{prediction.efficientnet_confidence:.2f}%",
                prediction.vit_prediction,
                f"{prediction.vit_confidence:.2f}%",
                prediction.swin_prediction,
                f"{prediction.swin_confidence:.2f}%",
                f"{prediction.inference_time:.2f}",
                'Yes' if prediction.is_validated else 'No',
                prediction.doctor_notes or 'N/A'
            ]

            for col, value in enumerate(data, start=1):
                sheet.cell(row=row, column=col, value=value)

        # Auto-adjust column widths
        for column in sheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            sheet.column_dimensions[column_letter].width = adjusted_width

        # Save to BytesIO
        excel_buffer = BytesIO()
        workbook.save(excel_buffer)
        excel_buffer.seek(0)

        return excel_buffer
```

---

## URL Configuration

### File: `reporting/urls.py`

```python
from django.urls import path
from . import views

app_name = 'reporting'

urlpatterns = [
    # Report generation
    path('generate/<int:prediction_id>/', views.generate_report, name='generate_report'),
    path('view/<uuid:report_id>/', views.view_report, name='view_report'),
    path('download/<uuid:report_id>/', views.download_report, name='download_report'),

    # Report management
    path('list/', views.report_list, name='report_list'),
    path('templates/', views.manage_templates, name='manage_templates'),

    # Batch operations
    path('batch/generate/', views.batch_generate_reports, name='batch_generate'),
    path('batch/status/<uuid:job_id>/', views.batch_job_status, name='batch_job_status'),
    path('batch/download/<uuid:job_id>/', views.download_batch_reports, name='download_batch_reports'),

    # Export
    path('export/excel/', views.export_to_excel, name='export_to_excel'),

    # API
    path('api/batch/<uuid:job_id>/progress/', views.batch_job_progress_api, name='batch_job_progress_api'),
]
```

---

## Templates

### Required Templates

1. **reporting/generate_report.html** - Form to configure and generate report
2. **reporting/view_report.html** - Preview report before download
3. **reporting/report_list.html** - List all generated reports
4. **reporting/batch_generate.html** - Batch report generation form
5. **reporting/batch_job_status.html** - Batch job progress display
6. **reporting/manage_templates.html** - Template management interface
7. **reporting/pdf_templates/report_template.html** - PDF report layout

---

## Admin Configuration

### File: `reporting/admin.py`

```python
from django.contrib import admin
from .models import ReportTemplate, Report, BatchReportJob


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'is_active', 'created_at']
    list_filter = ['template_type', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['report_id', 'patient_name', 'diagnosis', 'generated_at', 'status', 'download_count']
    list_filter = ['status', 'generated_at', 'include_signature']
    search_fields = ['report_id', 'patient__user__first_name', 'patient__user__last_name']
    readonly_fields = ['report_id', 'generated_at', 'file_size', 'downloaded_count', 'last_downloaded_at']

    def patient_name(self, obj):
        return obj.patient.user.get_full_name()
    patient_name.short_description = 'Patient'

    def diagnosis(self, obj):
        return obj.prediction.final_diagnosis
    diagnosis.short_description = 'Diagnosis'

    def download_count(self, obj):
        return obj.downloaded_count
    download_count.short_description = 'Downloads'


@admin.register(BatchReportJob)
class BatchReportJobAdmin(admin.ModelAdmin):
    list_display = ['job_id', 'created_by', 'status', 'progress_display', 'created_at', 'completed_at']
    list_filter = ['status', 'created_at']
    readonly_fields = ['job_id', 'created_at', 'completed_at', 'total_reports', 'completed_reports', 'failed_reports']

    def progress_display(self, obj):
        return f"{obj.get_progress_percentage()}%"
    progress_display.short_description = 'Progress'
```

---

## Decorators

### File: `reporting/decorators.py`

```python
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def doctor_required(view_func):
    """
    Decorator to ensure user is a doctor or admin
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            messages.error(request, "You don't have permission to access this page.")
            return redirect('detection:home')

        if not (request.user.profile.is_doctor() or request.user.profile.is_admin()):
            messages.error(request, "Only doctors can access this page.")
            return redirect('detection:patient_dashboard')

        return view_func(request, *args, **kwargs)

    return wrapper
```

---

## Dependencies

### Additional Python Packages (add to requirements.txt)

```
weasyprint==60.1          # For HTML to PDF conversion (primary)
xhtml2pdf==0.2.13         # Fallback PDF generator
openpyxl==3.1.2          # Excel file generation
qrcode[pil]==7.4.2       # QR code generation
Pillow==10.1.0           # Already installed (image processing)
```

---

## Integration Points

### 1. Update `config/settings.py`

```python
INSTALLED_APPS = [
    # ... existing apps ...
    'reporting',
]

# Report settings
SITE_URL = 'http://localhost:8000'  # Change in production
REPORT_LOGO_PATH = BASE_DIR / 'static' / 'images' / 'hospital_logo.png'
REPORT_SIGNATURE_PATH = BASE_DIR / 'media' / 'signatures'
```

### 2. Update `config/urls.py`

```python
urlpatterns = [
    # ... existing patterns ...
    path('reporting/', include('reporting.urls')),
]
```

### 3. Add Links in Templates

Add report generation buttons in:
- `detection/results.html` - "Generate Report" button
- `detection/doctor_dashboard.html` - "Batch Reports" link
- `detection/history.html` - "Export to Excel" button

---

## Testing Requirements

### Unit Tests (`reporting/tests.py`)

1. Test report generation for all template types
2. Test batch report processing
3. Test Excel export functionality
4. Test QR code generation
5. Test report permissions (doctor vs patient)
6. Test download counter increment
7. Test batch job progress tracking

### Integration Tests

1. Test end-to-end report generation flow
2. Test batch report ZIP creation
3. Test report verification via QR code

---

## Migration Steps

1. Create Django app: `python manage.py startapp reporting`
2. Add models and run migrations: `python manage.py makemigrations reporting && python manage.py migrate`
3. Install dependencies: `pip install weasyprint xhtml2pdf openpyxl qrcode[pil]`
4. Create default report templates via admin or data migration
5. Create media directories for reports
6. Update templates with report generation links

---

## Notes for Implementation

1. **PDF Generation:** WeasyPrint is recommended for production-quality PDFs, but requires system dependencies (cairo, pango). For simpler setup, use xhtml2pdf as fallback.

2. **Background Processing:** For large batch jobs, consider using Celery for asynchronous processing. Current implementation is synchronous.

3. **Storage:** Reports can consume significant storage. Consider implementing automatic cleanup of old reports or moving to cloud storage (S3).

4. **Security:** Report files contain sensitive medical data. Ensure proper access controls and consider encryption at rest.

5. **Templates:** Create beautiful, professional PDF templates using HTML/CSS. Test print output carefully.

6. **QR Codes:** Implement a verification endpoint that validates report authenticity using the QR code.

---

## Success Criteria

- ✅ Doctors can generate professional PDF reports for any prediction
- ✅ Reports include all prediction details, patient info, and visualizations
- ✅ Batch report generation works for multiple patients
- ✅ Excel export provides research-ready data
- ✅ Reports are tracked with download counts and versioning
- ✅ QR codes enable report verification
- ✅ Print-optimized layouts produce clean, professional output
