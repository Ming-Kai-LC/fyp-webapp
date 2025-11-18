# Enhanced Dashboards Module

## Overview
The Enhanced Dashboards Module provides role-specific, comprehensive dashboard interfaces for the COVID-19 Detection System. It integrates all system features into unified, customizable views for doctors, patients, and administrators.

## Features

### Core Features
- ✅ Enhanced Doctor Dashboard with today's schedule
- ✅ Enhanced Patient Dashboard with health timeline
- ✅ Enhanced Admin Dashboard with system health monitoring
- ✅ Quick actions and shortcuts
- ✅ Real-time notifications panel
- ✅ Widget-based customizable layout
- ✅ Recent activities feed

### Advanced Features
- ✅ Dashboard customization preferences
- ✅ Theme support (Light/Dark)
- ✅ Auto-refresh settings
- ✅ Mobile-optimized responsive design
- ✅ Bootstrap 5 based UI

## Installation & Setup

### 1. Run Migrations
```bash
python manage.py migrate dashboards
```

### 2. Access Dashboards

**Doctor Dashboard:**
```
http://localhost:8000/dashboards/doctor/
```

**Patient Dashboard:**
```
http://localhost:8000/dashboards/patient/
```

**Admin Dashboard:**
```
http://localhost:8000/dashboards/admin/
```

**Preferences:**
```
http://localhost:8000/dashboards/preferences/
```

## File Structure

```
dashboards/
├── __init__.py
├── admin.py                 # Django admin configuration
├── apps.py
├── models.py                # Database models
├── urls.py                  # URL routing
├── views.py                 # View functions
├── migrations/
│   ├── __init__.py
│   └── 0001_initial.py     # Initial migration
├── templates/
│   └── dashboards/
│       ├── doctor_dashboard_enhanced.html
│       ├── patient_dashboard_enhanced.html
│       ├── admin_dashboard_enhanced.html
│       └── preferences.html
└── README.md
```

## Models

### DashboardPreference
Stores user-specific dashboard customization settings:
- Theme (light/dark)
- Widget layout and visibility
- Auto-refresh settings
- Refresh interval

### DashboardWidget
Defines available dashboard widgets:
- Widget type and metadata
- Role-based access control
- Default size and position
- Active status

## Views

### enhanced_doctor_dashboard
**URL:** `/dashboards/doctor/`
**Access:** Authenticated users

**Widgets:**
- Today's appointments
- Pending validations
- Recent predictions
- Statistics cards
- Quick actions
- Notifications

### enhanced_patient_dashboard
**URL:** `/dashboards/patient/`
**Access:** Authenticated users with patient profile

**Widgets:**
- Health summary card
- Test results timeline
- Upcoming appointments
- Health trends chart
- Quick actions
- Notifications

### enhanced_admin_dashboard
**URL:** `/dashboards/admin/`
**Access:** Admin users only

**Widgets:**
- System health monitoring
- User statistics
- Hospital statistics
- Recent activities
- Security alerts
- Model performance metrics
- Compliance status

### dashboard_preferences
**URL:** `/dashboards/preferences/`
**Access:** Authenticated users

Allows users to customize their dashboard settings.

### toggle_widget
**URL:** `/dashboards/widgets/toggle/`
**Method:** POST (AJAX)
**Access:** Authenticated users

Toggle widget visibility dynamically.

## Templates

All templates extend `base.html` and are fully responsive using Bootstrap 5.

### Key Template Features
- Mobile-first responsive design
- Bootstrap 5 components
- Chart.js integration for health trends
- Auto-refresh functionality
- Real-time updates

## Integration Points

### Dependencies
- `detection` app (Prediction, Patient, XRayImage models)
- `appointments` app (Appointment model)
- `notifications` app (Notification model)
- `audit` app (AuditLog, SecurityAlert models)
- `analytics` app (for advanced analytics)
- `medical_records` app (optional, for risk scores)

### URLs Referenced
The dashboards link to various parts of the system:
- Detection module URLs
- Appointments URLs
- Notifications URLs
- Analytics URLs
- Medical Records URLs
- Reporting URLs
- Audit URLs

## Customization

### Adding New Widgets
1. Create widget template in `dashboards/templates/dashboards/widgets/`
2. Add widget definition to `DashboardWidget` model via admin
3. Update relevant dashboard view to include widget data
4. Add widget to dashboard template

### Theming
Users can switch between light and dark themes via preferences page.

### Auto-Refresh
Dashboards auto-refresh at configurable intervals:
- Doctor dashboard: 60 seconds (default)
- Patient dashboard: No auto-refresh (manual only)
- Admin dashboard: 30 seconds (for real-time monitoring)

## Security

### Access Control
- All views require authentication (`@login_required`)
- Role-based access checking (doctor, patient, admin)
- Patient dashboard requires patient profile
- Admin dashboard requires admin role

### CSRF Protection
All POST requests include CSRF tokens.

## Performance Optimization

### Database Queries
- Uses `select_related()` and `prefetch_related()` for optimal query performance
- Limited result sets (e.g., last 10 items)
- Indexed fields for fast lookups

### Caching (Future Enhancement)
Consider adding Django cache framework for:
- Dashboard statistics
- Widget data
- User preferences

## Testing

To be implemented:
- Unit tests for models
- View tests for all dashboard endpoints
- Template rendering tests
- Integration tests with other modules

## Future Enhancements

### Planned Features
- [ ] Drag-and-drop widget customization
- [ ] Dashboard presets/templates
- [ ] Export dashboard data
- [ ] Real-time WebSocket updates
- [ ] Advanced data visualization
- [ ] Custom widget builder
- [ ] Dashboard sharing

## Troubleshooting

### Common Issues

**Issue:** Dashboard shows "No data"
**Solution:** Ensure dependencies (predictions, appointments, etc.) have data

**Issue:** Admin dashboard access denied
**Solution:** Verify user has admin role in UserProfile

**Issue:** Preferences not saving
**Solution:** Check CSRF token and form submission

## Support

For issues and questions:
- Check the main project documentation
- Review the specification: `specs/07_ENHANCED_DASHBOARDS_SPEC.md`
- Contact the development team

## Version History

### v1.0.0 (Current)
- Initial implementation
- All core features completed
- Doctor, Patient, and Admin dashboards
- Preferences management
- Mobile-responsive design
