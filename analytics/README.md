# Advanced Analytics Module

## Overview

The Advanced Analytics Module provides comprehensive data-driven insights for the COVID-19 Detection System. It includes dashboards, trend analysis, model comparison, demographic insights, and data export capabilities for research purposes.

## Features

### Core Features

1. **Hospital-wide Statistics Dashboard** - Real-time overview of key metrics
2. **Disease Trend Analysis** - Track COVID cases and predictions over time
3. **Model Performance Analytics** - Compare all 6 AI models (CrossViT, ResNet-50, DenseNet-121, EfficientNet-B0, ViT-Base, Swin-Tiny)
4. **Doctor Productivity Metrics** - Track reviews and uploads by doctors
5. **Patient Demographics Analysis** - Analyze predictions by age, gender, and diagnosis
6. **Geographic Heatmaps** - Visualize data by region (future enhancement)
7. **Export for Research Papers** - Export data in CSV, Excel, or JSON formats
8. **Time-series Analysis** - Analyze trends over customizable time periods

### Advanced Features

9. **Predictive Analytics** - Outbreak predictions (future enhancement)
10. **Machine Learning Model Drift Detection** - Monitor model performance over time
11. **Comparative Analysis** - Compare data across different time periods
12. **Custom Report Builder** - Create and save custom analytics reports
13. **Data Visualization Library** - Interactive charts using Chart.js
14. **Real-time Analytics Dashboard** - Live updates of key metrics
15. **Cohort Analysis** - Group and analyze patient cohorts (future enhancement)

## Installation

### Prerequisites

- Django 4.2.7+
- Python 3.9+
- pandas 2.1.3
- plotly 5.18.0

### Setup Steps

1. **Install Dependencies**
   ```bash
   pip install pandas==2.1.3 plotly==5.18.0
   ```

2. **Run Migrations**
   ```bash
   python manage.py makemigrations analytics
   python manage.py migrate analytics
   ```

3. **Verify Installation**
   - The analytics app should now appear in Django admin
   - Navigate to http://localhost:8000/analytics/dashboard/

## Usage

### Accessing Analytics

- **URL**: `/analytics/dashboard/`
- **Permissions**: Login required (accessible to doctors and admins)
- **Navigation**: Available in the main navigation bar for authenticated doctors

### Available Endpoints

- `/analytics/dashboard/` - Main analytics dashboard
- `/analytics/trends/` - Detailed trend analysis
- `/analytics/models/` - AI model comparison
- `/analytics/demographics/` - Demographic analysis
- `/analytics/predictions/` - Prediction analytics
- `/analytics/reports/` - Custom reports listing
- `/analytics/reports/create/` - Create custom report
- `/analytics/reports/<id>/` - View specific report
- `/analytics/export/` - Data export interface

### API Endpoints

- `/analytics/api/snapshot/<date>/` - Get snapshot for specific date (YYYY-MM-DD)
- `/analytics/api/trends/<days>/` - Get trend data for last N days

### Management Commands

#### Generate Analytics Snapshots

Generate daily snapshots of key metrics:

```bash
# Generate snapshot for today
python manage.py generate_snapshots

# Generate snapshot for specific date
python manage.py generate_snapshots --date 2024-01-15
```

**Recommended**: Set up a cron job to run this daily:
```bash
0 0 * * * cd /path/to/project && python manage.py generate_snapshots
```

## Database Models

### AnalyticsSnapshot
Stores daily/weekly/monthly snapshots of key metrics including:
- Total predictions, COVID cases, normal cases
- Patient statistics
- Model performance metrics

### ModelPerformanceMetric
Tracks individual model performance over time:
- Average confidence and inference time
- Accuracy metrics (when validation data available)
- Agreement rates with other models

### CustomReport
User-defined custom analytics reports with:
- Configurable filters and parameters
- Multiple chart types (line, bar, pie, heatmap, table)
- Public/private sharing options

### DataExport
Tracks data exports for research:
- Export type and format
- Applied filters and date ranges
- Anonymization status

## Data Export

### Export Options

1. **Export Types**:
   - Predictions Data
   - Demographics
   - Full Dataset
   - Custom Query

2. **File Formats**:
   - CSV (Comma-separated values)
   - XLSX (Excel)
   - JSON

3. **Privacy Options**:
   - Anonymize patient data (recommended for research)
   - Include/exclude sensitive fields

### Example Export Usage

1. Navigate to `/analytics/export/`
2. Select export type and format
3. Apply filters (date range, diagnosis type)
4. Choose anonymization options
5. Click "Export Data"
6. File will be downloaded automatically

## Custom Reports

### Creating Custom Reports

1. Navigate to `/analytics/reports/create/`
2. Fill in report details:
   - Name and description
   - Report type (prediction trends, demographics, etc.)
   - Chart type (line, bar, pie, heatmap, table)
   - Date range filters
   - Make public (optional)
3. Click "Create Report"

### Viewing Reports

- **Your Reports**: Reports you created
- **Public Reports**: Reports shared by other users
- Access from `/analytics/reports/`

## Integration Points

The Analytics module integrates with:

- **Detection Module**: Analyzes predictions and X-ray data
- **Medical Records**: Patient demographics and history
- **Audit Module**: Tracks data access for analytics
- **Reporting Module**: Can be integrated for comprehensive reports
- **Notifications**: Can trigger alerts based on analytics thresholds (future)

## Security Considerations

- All views require authentication
- Data exports are tracked in DataExport model
- Anonymization option available for research exports
- HIPAA/GDPR compliance should be verified for production use
- Implement role-based access control for sensitive analytics

## Future Enhancements

1. **Predictive Analytics**: Machine learning-based outbreak predictions
2. **Geographic Heatmaps**: Visualize data by region/location
3. **Real-time Alerts**: Trigger notifications based on analytics thresholds
4. **Advanced Cohort Analysis**: More sophisticated patient grouping
5. **Model Drift Detection**: Automated alerts for model performance degradation
6. **Integration with External BI Tools**: Export to Tableau, Power BI, etc.
7. **Mobile-responsive Dashboards**: Enhanced mobile views
8. **Scheduled Reports**: Automated report generation and email delivery

## Troubleshooting

### Common Issues

1. **No data in dashboard**
   - Run `python manage.py generate_snapshots` to create initial snapshot
   - Ensure predictions exist in the database

2. **Import errors**
   - Verify pandas and plotly are installed
   - Check Python version compatibility

3. **Chart not displaying**
   - Check browser console for JavaScript errors
   - Ensure Chart.js CDN is accessible
   - Verify data format in template context

4. **Export fails**
   - Check file permissions on media/analytics/exports/
   - Verify openpyxl is installed for Excel exports
   - Ensure sufficient data exists for export

## Development Notes

- Follow Django best practices for views and models
- Use Bootstrap 5 for consistent UI styling
- Implement pagination for large datasets
- Add caching for frequently accessed analytics
- Optimize database queries with select_related() and prefetch_related()
- Add tests for critical analytics calculations

## Support

For issues or questions:
- Check the specification: `specs/06_ADVANCED_ANALYTICS_SPEC.md`
- Review Django documentation
- Contact the development team

## License

Part of the COVID-19 Detection System
TAR UMT Bachelor of Data Science FYP
Author: Tan Ming Kai (24PMR12003)
