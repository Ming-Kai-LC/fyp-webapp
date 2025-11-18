# analytics/views.py
"""
Analytics views for dashboard, trends, and data visualization
Provides comprehensive analytics interface for hospital management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
import json
import csv

from .models import AnalyticsSnapshot, CustomReport, DataExport
from .services import AnalyticsEngine
from detection.models import Prediction


@login_required
def analytics_dashboard(request):
    """
    Main analytics dashboard with overview metrics
    """
    # Get summary statistics
    summary = AnalyticsEngine.get_dashboard_summary()

    # Get recent trend data (last 30 days)
    trend_data = AnalyticsEngine.get_trend_data(days=30)

    # Get latest snapshot
    latest_snapshot = AnalyticsSnapshot.objects.filter(
        period_type='daily'
    ).first()

    context = {
        'summary': summary,
        'trend_data': json.dumps(trend_data),  # For JavaScript charts
        'latest_snapshot': latest_snapshot,
        'page_title': 'Analytics Dashboard',
    }

    return render(request, 'analytics/dashboard.html', context)


@login_required
def trend_analysis(request):
    """
    Detailed trend analysis with configurable time periods
    """
    # Get time period from request (default: 30 days)
    days = int(request.GET.get('days', 30))

    # Get trend data
    trend_data = AnalyticsEngine.get_trend_data(days=days)

    # Get snapshots for table view
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)

    snapshots = AnalyticsSnapshot.objects.filter(
        period_type='daily',
        snapshot_date__range=[start_date, end_date]
    ).order_by('-snapshot_date')

    context = {
        'trend_data': json.dumps(trend_data),
        'snapshots': snapshots,
        'days': days,
        'page_title': 'Trend Analysis',
    }

    return render(request, 'analytics/trends.html', context)


@login_required
def model_comparison(request):
    """
    Compare performance of all AI models
    """
    # Get model comparison data
    comparison_data = AnalyticsEngine.get_model_comparison()

    # Get recent predictions for detailed analysis
    recent_predictions = Prediction.objects.select_related(
        'xray__patient__user'
    ).order_by('-created_at')[:100]

    context = {
        'comparison_data': comparison_data,
        'comparison_json': json.dumps(comparison_data),
        'recent_predictions': recent_predictions,
        'page_title': 'Model Comparison',
    }

    return render(request, 'analytics/model_comparison.html', context)


@login_required
def demographic_analysis(request):
    """
    Patient demographic analysis and insights
    """
    # Get demographic data
    demographic_data = AnalyticsEngine.get_demographic_analysis()

    context = {
        'demographic_data': demographic_data,
        'demographic_json': json.dumps(demographic_data),
        'page_title': 'Demographic Analysis',
    }

    return render(request, 'analytics/demographics.html', context)


@login_required
def prediction_analytics(request):
    """
    Detailed prediction analytics and patterns
    """
    # Get all predictions with statistics
    predictions = Prediction.objects.select_related(
        'xray__patient__user'
    ).order_by('-created_at')

    # Apply filters if provided
    diagnosis_filter = request.GET.get('diagnosis')
    if diagnosis_filter:
        predictions = predictions.filter(final_diagnosis=diagnosis_filter)

    date_from = request.GET.get('date_from')
    if date_from:
        predictions = predictions.filter(created_at__date__gte=date_from)

    date_to = request.GET.get('date_to')
    if date_to:
        predictions = predictions.filter(created_at__date__lte=date_to)

    # Paginate results
    from django.core.paginator import Paginator
    paginator = Paginator(predictions, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'filters': {
            'diagnosis': diagnosis_filter,
            'date_from': date_from,
            'date_to': date_to,
        },
        'page_title': 'Prediction Analytics',
    }

    return render(request, 'analytics/predictions.html', context)


@login_required
def custom_reports(request):
    """
    View and manage custom reports
    """
    # Get user's reports
    user_reports = CustomReport.objects.filter(created_by=request.user)

    # Get public reports
    public_reports = CustomReport.objects.filter(is_public=True).exclude(
        created_by=request.user
    )

    context = {
        'user_reports': user_reports,
        'public_reports': public_reports,
        'page_title': 'Custom Reports',
    }

    return render(request, 'analytics/custom_reports.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def create_custom_report(request):
    """
    Create a new custom report
    """
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        report_type = request.POST.get('report_type')
        description = request.POST.get('description', '')
        chart_type = request.POST.get('chart_type')
        is_public = request.POST.get('is_public') == 'on'

        # Build filters from form
        filters = {}
        if request.POST.get('date_from'):
            filters['date_from'] = request.POST.get('date_from')
        if request.POST.get('date_to'):
            filters['date_to'] = request.POST.get('date_to')
        if request.POST.get('diagnosis'):
            filters['diagnosis'] = request.POST.get('diagnosis')

        # Create report
        report = CustomReport.objects.create(
            name=name,
            report_type=report_type,
            description=description,
            filters=filters,
            chart_type=chart_type,
            created_by=request.user,
            is_public=is_public,
        )

        messages.success(request, f'Report "{name}" created successfully!')
        return redirect('analytics:view_custom_report', report_id=report.id)

    context = {
        'page_title': 'Create Custom Report',
    }

    return render(request, 'analytics/create_custom_report.html', context)


@login_required
def view_custom_report(request, report_id):
    """
    View a custom report with data visualization
    """
    report = get_object_or_404(CustomReport, id=report_id)

    # Check permissions
    if not report.is_public and report.created_by != request.user:
        messages.error(request, 'You do not have permission to view this report.')
        return redirect('analytics:custom_reports')

    # Generate report data based on type and filters
    report_data = _generate_report_data(report)

    context = {
        'report': report,
        'report_data': report_data,
        'report_data_json': json.dumps(report_data),
        'page_title': report.name,
    }

    return render(request, 'analytics/view_custom_report.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def export_data(request):
    """
    Export analytics data for research
    """
    if request.method == 'POST':
        export_type = request.POST.get('export_type')
        file_format = request.POST.get('file_format', 'csv')
        anonymize = request.POST.get('anonymize') == 'on'

        # Build filters
        filters = {}
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        diagnosis = request.POST.get('diagnosis')

        if date_from:
            filters['date_start'] = date_from
        if date_to:
            filters['date_end'] = date_to
        if diagnosis:
            filters['diagnosis'] = diagnosis

        # Export data
        df = AnalyticsEngine.export_to_dataframe(filters=filters)

        # Anonymize if requested
        if anonymize:
            df = df.drop(columns=['patient_id'], errors='ignore')

        # Create export record
        data_export = DataExport.objects.create(
            export_type=export_type,
            exported_by=request.user,
            file_format=file_format,
            filters_applied=filters,
            date_range_start=date_from,
            date_range_end=date_to,
            record_count=len(df),
            anonymized=anonymize,
        )

        # Generate file
        if file_format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="analytics_export_{data_export.id}.csv"'
            df.to_csv(response, index=False)
            return response

        elif file_format == 'xlsx':
            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="analytics_export_{data_export.id}.xlsx"'
            df.to_excel(response, index=False, engine='openpyxl')
            return response

        elif file_format == 'json':
            response = HttpResponse(content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="analytics_export_{data_export.id}.json"'
            response.write(df.to_json(orient='records', date_format='iso'))
            return response

    # GET request - show export form
    # Get recent exports
    recent_exports = DataExport.objects.filter(
        exported_by=request.user
    ).order_by('-exported_at')[:10]

    context = {
        'recent_exports': recent_exports,
        'page_title': 'Export Data',
    }

    return render(request, 'analytics/export_data.html', context)


# ============================================================================
# API Endpoints
# ============================================================================

@login_required
def snapshot_api(request, date):
    """
    API endpoint to get snapshot data for a specific date
    """
    try:
        snapshot = AnalyticsSnapshot.objects.get(
            period_type='daily',
            snapshot_date=date
        )
        data = {
            'date': snapshot.snapshot_date.isoformat(),
            'total_predictions': snapshot.total_predictions,
            'covid_positive': snapshot.covid_positive,
            'normal_cases': snapshot.normal_cases,
            'viral_pneumonia': snapshot.viral_pneumonia,
            'lung_opacity': snapshot.lung_opacity,
            'avg_confidence': snapshot.avg_confidence,
            'avg_inference_time': snapshot.avg_inference_time,
        }
        return JsonResponse(data)
    except AnalyticsSnapshot.DoesNotExist:
        return JsonResponse({'error': 'Snapshot not found'}, status=404)


@login_required
def trends_api(request, days):
    """
    API endpoint to get trend data for N days
    """
    trend_data = AnalyticsEngine.get_trend_data(days=days)
    return JsonResponse(trend_data)


# ============================================================================
# Helper Functions
# ============================================================================

def _generate_report_data(report: CustomReport) -> dict:
    """
    Generate data for a custom report based on its type and filters
    """
    filters = report.filters

    if report.report_type == 'prediction_trends':
        days = filters.get('days', 30)
        return AnalyticsEngine.get_trend_data(days=days)

    elif report.report_type == 'demographic_analysis':
        return AnalyticsEngine.get_demographic_analysis()

    elif report.report_type == 'model_comparison':
        return AnalyticsEngine.get_model_comparison()

    elif report.report_type == 'doctor_productivity':
        days = filters.get('days', 30)
        return {'doctors': AnalyticsEngine.get_doctor_productivity(days=days)}

    else:
        # Custom query - return empty data for now
        return {}
