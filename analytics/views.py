"""
Analytics Module - Views
TAR UMT Bachelor of Data Science FYP
Author: Tan Ming Kai (24PMR12003)
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
import json
import csv

from .services import AnalyticsEngine
from .models import CustomReport, DataExport, AnalyticsSnapshot
from detection.models import Prediction


@login_required
def analytics_dashboard(request):
    """
    Main analytics dashboard with key metrics
    """
    # Get dashboard statistics
    stats = AnalyticsEngine.get_dashboard_stats()

    # Get trend data for the last 30 days
    trend_data = AnalyticsEngine.get_trend_data(days=30)

    # Get recent snapshots
    recent_snapshots = AnalyticsSnapshot.objects.filter(
        period_type='daily'
    )[:7]

    context = {
        'stats': stats,
        'trend_data': json.dumps(trend_data),
        'recent_snapshots': recent_snapshots,
    }

    return render(request, 'analytics/dashboard.html', context)


@login_required
def trend_analysis(request):
    """
    Detailed trend analysis view
    """
    # Get number of days from query params, default 30
    days = int(request.GET.get('days', 30))

    # Get trend data
    trend_data = AnalyticsEngine.get_trend_data(days=days)

    context = {
        'days': days,
        'trend_data': json.dumps(trend_data),
    }

    return render(request, 'analytics/trends.html', context)


@login_required
def model_comparison(request):
    """
    Compare AI model performance
    """
    # Get model comparison data
    comparison_data = AnalyticsEngine.get_model_comparison()

    context = {
        'comparison_data': comparison_data,
        'comparison_json': json.dumps(comparison_data),
    }

    return render(request, 'analytics/model_comparison.html', context)


@login_required
def demographic_analysis(request):
    """
    Analyze predictions by demographics
    """
    # Get demographic analysis
    demographics = AnalyticsEngine.get_demographic_analysis()

    context = {
        'demographics': demographics,
        'demographics_json': json.dumps(demographics),
    }

    return render(request, 'analytics/demographics.html', context)


@login_required
def prediction_analytics(request):
    """
    Detailed prediction analytics
    """
    # Get recent predictions
    predictions = Prediction.objects.select_related(
        'xray__patient__user'
    ).order_by('-created_at')[:100]

    # Get statistics
    total_predictions = Prediction.objects.count()
    validated_count = Prediction.objects.filter(is_validated=True).count()
    validation_rate = (validated_count / total_predictions * 100) if total_predictions > 0 else 0

    context = {
        'predictions': predictions,
        'total_predictions': total_predictions,
        'validated_count': validated_count,
        'validation_rate': round(validation_rate, 2),
    }

    return render(request, 'analytics/predictions.html', context)


@login_required
def custom_reports(request):
    """
    List custom reports
    """
    # Get user's reports and public reports
    user_reports = CustomReport.objects.filter(created_by=request.user)
    public_reports = CustomReport.objects.filter(is_public=True).exclude(
        created_by=request.user
    )

    context = {
        'user_reports': user_reports,
        'public_reports': public_reports,
    }

    return render(request, 'analytics/custom_reports.html', context)


@login_required
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

        # Get filters from POST data
        filters = {
            'start_date': request.POST.get('start_date'),
            'end_date': request.POST.get('end_date'),
            'diagnosis': request.POST.get('diagnosis'),
        }

        # Create report
        report = CustomReport.objects.create(
            name=name,
            report_type=report_type,
            description=description,
            chart_type=chart_type,
            filters=filters,
            created_by=request.user,
            is_public=is_public,
        )

        messages.success(request, 'Custom report created successfully!')
        return redirect('analytics:view_custom_report', report_id=report.id)

    return render(request, 'analytics/create_custom_report.html')


@login_required
def view_custom_report(request, report_id):
    """
    View a custom report
    """
    report = get_object_or_404(CustomReport, id=report_id)

    # Check permissions
    if not report.is_public and report.created_by != request.user:
        messages.error(request, 'You do not have permission to view this report.')
        return redirect('analytics:custom_reports')

    # Generate report data based on report type
    report_data = {}

    if report.report_type == 'prediction_trends':
        days = 30
        if report.filters.get('start_date') and report.filters.get('end_date'):
            start = datetime.strptime(report.filters['start_date'], '%Y-%m-%d').date()
            end = datetime.strptime(report.filters['end_date'], '%Y-%m-%d').date()
            days = (end - start).days
        report_data = AnalyticsEngine.get_trend_data(days=days)

    elif report.report_type == 'demographic_analysis':
        report_data = AnalyticsEngine.get_demographic_analysis()

    elif report.report_type == 'model_comparison':
        report_data = AnalyticsEngine.get_model_comparison()

    elif report.report_type == 'doctor_productivity':
        report_data = AnalyticsEngine.get_doctor_productivity()

    context = {
        'report': report,
        'report_data': report_data,
        'report_data_json': json.dumps(report_data),
    }

    return render(request, 'analytics/view_custom_report.html', context)


@login_required
def export_data(request):
    """
    Export analytics data
    """
    if request.method == 'POST':
        export_type = request.POST.get('export_type')
        file_format = request.POST.get('file_format', 'csv')
        anonymized = request.POST.get('anonymized') == 'on'

        # Get filters
        filters = {}
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        diagnosis = request.POST.get('diagnosis')

        if start_date:
            filters['start_date'] = datetime.strptime(start_date, '%Y-%m-%d').date()
        if end_date:
            filters['end_date'] = datetime.strptime(end_date, '%Y-%m-%d').date()
        if diagnosis:
            filters['diagnosis'] = diagnosis

        # Export to DataFrame
        df = AnalyticsEngine.export_to_dataframe(filters=filters)

        # Anonymize if requested
        if anonymized:
            df = df.drop(columns=['patient_id'], errors='ignore')

        # Generate filename
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f'analytics_export_{timestamp}'

        # Export based on format
        if file_format == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
            df.to_csv(response, index=False)

        elif file_format == 'xlsx':
            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
            df.to_excel(response, index=False, engine='openpyxl')

        elif file_format == 'json':
            response = HttpResponse(content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="{filename}.json"'
            df.to_json(response, orient='records', date_format='iso')

        # Track export
        DataExport.objects.create(
            export_type=export_type,
            exported_by=request.user,
            filters_applied=filters,
            date_range_start=filters.get('start_date'),
            date_range_end=filters.get('end_date'),
            file_format=file_format,
            record_count=len(df),
            anonymized=anonymized,
        )

        return response

    return render(request, 'analytics/export_data.html')


@login_required
def snapshot_api(request, date):
    """
    API endpoint to get snapshot for a specific date
    """
    try:
        snapshot_date = datetime.strptime(date, '%Y-%m-%d').date()
        snapshot = AnalyticsSnapshot.objects.get(
            period_type='daily',
            snapshot_date=snapshot_date
        )

        data = {
            'date': snapshot.snapshot_date.strftime('%Y-%m-%d'),
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
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)


@login_required
def trends_api(request, days):
    """
    API endpoint to get trend data for N days
    """
    try:
        if days > 365:
            return JsonResponse({'error': 'Maximum 365 days allowed'}, status=400)

        trend_data = AnalyticsEngine.get_trend_data(days=days)
        return JsonResponse(trend_data)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
