# Advanced Analytics Module

## Overview
The Advanced Analytics Module provides comprehensive data-driven insights, trend analysis, and predictive analytics for the COVID-19 Detection System.

## Features

### Core Features
- Hospital-wide statistics dashboard
- Disease trend analysis (COVID cases over time)
- Model performance analytics and comparison
- Doctor productivity metrics
- Patient demographics analysis
- Geographic heatmaps (by region/age/gender)
- Export for research papers
- Time-series analysis

### Advanced Features
- Predictive analytics (outbreak predictions)
- Machine learning model drift detection
- Comparative analysis across time periods
- Custom report builder
- Data visualization library (charts, graphs, heatmaps)
- Real-time analytics dashboard
- Cohort analysis

## Installation

### 1. Install Dependencies
```bash
pip install pandas plotly openpyxl
```

### 2. Run Migrations
```bash
python manage.py makemigrations analytics
python manage.py migrate analytics
```

### 3. Generate Initial Snapshots
```bash
# Generate daily snapshot for today
python manage.py generate_snapshots --period daily

# Backfill last 30 days
python manage.py generate_snapshots --backfill 30

# Generate all periods (daily, weekly, monthly)
python manage.py generate_snapshots --period all
```

## Usage

### Accessing the Analytics Dashboard
1. Navigate to `/analytics/dashboard/` to view the main analytics dashboard
2. Access specific analytics:
   - Trend Analysis: `/analytics/trends/`
   - Model Comparison: `/analytics/models/`
   - Demographics: `/analytics/demographics/`
   - Custom Reports: `/analytics/reports/`
   - Data Export: `/analytics/export/`

### Creating Custom Reports
1. Go to `/analytics/reports/create/`
2. Select report type, chart type, and filters
3. Save and view your custom report

### Exporting Data
1. Navigate to `/analytics/export/`
2. Choose export type, file format (CSV, Excel, JSON)
3. Apply filters and anonymization options
4. Download the exported data

### API Endpoints
- Get snapshot: `/analytics/api/snapshot/<date>/`
- Get trends: `/analytics/api/trends/<days>/`

## Models

### AnalyticsSnapshot
Stores daily/weekly/monthly snapshots of key metrics.

### ModelPerformanceMetric
Tracks individual model performance over time.

### CustomReport
User-defined custom analytics reports.

### DataExport
Tracks data exports for research and auditing.

## Management Commands

### generate_snapshots
Generate analytics snapshots for specified periods.

```bash
# Daily snapshot
python manage.py generate_snapshots --period daily

# Weekly snapshot
python manage.py generate_snapshots --period weekly

# Monthly snapshot
python manage.py generate_snapshots --period monthly

# Backfill historical data
python manage.py generate_snapshots --backfill 90
```

## Scheduled Tasks (Optional)

To automate snapshot generation, add to crontab:

```bash
# Generate daily snapshot at midnight
0 0 * * * cd /path/to/project && python manage.py generate_snapshots --period daily

# Generate weekly snapshot on Sunday
0 1 * * 0 cd /path/to/project && python manage.py generate_snapshots --period weekly

# Generate monthly snapshot on first day of month
0 2 1 * * cd /path/to/project && python manage.py generate_snapshots --period monthly
```

## Testing

Run tests:
```bash
python manage.py test analytics
```

## Integration

The analytics module integrates with:
- **detection** app: Accesses prediction and patient data
- **accounts** app: User and role-based access control
- **dashboards** app: Links from doctor/admin dashboards

## Security

- All views require authentication (`@login_required`)
- Custom reports have ownership and privacy controls
- Data exports can be anonymized for research
- Export history is tracked for auditing

## Performance Optimization

- Database indexes on frequently queried fields
- Snapshot pre-aggregation for fast dashboard loading
- Efficient queries using `select_related` and `prefetch_related`
- Chart.js for client-side rendering of visualizations

## Future Enhancements

- Real-time WebSocket updates for live dashboards
- Advanced predictive analytics using ML models
- Geographic heatmaps with actual location data
- PDF report generation
- Email scheduled reports
- Data warehousing for historical analysis

## Support

For issues or questions, contact the development team or refer to the main project documentation.
