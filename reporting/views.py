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
