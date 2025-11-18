# Appointment & Scheduling Module

## Overview

The Appointment & Scheduling module provides comprehensive appointment management functionality for the COVID-19 Detection System, enabling seamless scheduling between patients and doctors.

## Features

### Core Features
- ✅ Calendar-based appointment booking
- ✅ Doctor availability management
- ✅ Patient appointment history
- ✅ Automated reminders (email/SMS)
- ✅ Appointment status tracking (scheduled, completed, cancelled, no-show)
- ✅ Multiple appointment types (consultation, follow-up, X-ray review, virtual)
- ✅ Waitlist management

### Advanced Features
- ✅ Recurring doctor schedules
- ✅ Virtual consultation support
- ✅ Multi-doctor scheduling
- ✅ Appointment analytics
- ✅ No-show tracking

## Module Structure

```
appointments/
├── __init__.py
├── apps.py                 # App configuration
├── models.py              # Database models
├── services.py            # Business logic layer
├── forms.py               # Form definitions
├── views.py               # View functions
├── urls.py                # URL routing
├── admin.py               # Admin panel configuration
├── templates/
│   └── appointments/
│       ├── base.html
│       ├── components/
│       │   └── appointment_card.html
│       └── pages/
│           ├── book_appointment.html
│           ├── my_appointments.html
│           ├── appointment_detail.html
│           ├── reschedule_appointment.html
│           ├── manage_schedule.html
│           ├── doctor_appointments.html
│           └── join_waitlist.html
└── README.md
```

## Models

### DoctorSchedule
Defines doctor's weekly working hours and availability.

**Fields:**
- `doctor`: ForeignKey to User (doctor)
- `day_of_week`: Integer (0=Monday, 6=Sunday)
- `start_time`: TimeField
- `end_time`: TimeField
- `slot_duration`: Integer (minutes)
- `max_appointments_per_slot`: Integer
- `is_active`: Boolean

### Appointment
Individual appointment instances.

**Key Fields:**
- `appointment_id`: UUID (unique identifier)
- `patient`: ForeignKey to Patient
- `doctor`: ForeignKey to User (doctor)
- `appointment_date`: DateField
- `appointment_time`: TimeField
- `duration`: Integer (minutes)
- `appointment_type`: CharField (choices)
- `status`: CharField (choices)
- `reason`: TextField
- `doctor_notes`: TextField

**Status Choices:**
- `scheduled`: Initial state
- `confirmed`: Confirmed by patient/doctor
- `in_progress`: Currently happening
- `completed`: Finished
- `cancelled_patient`: Cancelled by patient
- `cancelled_doctor`: Cancelled by doctor
- `no_show`: Patient didn't show up
- `rescheduled`: Appointment was rescheduled

### AppointmentReminder
Tracks scheduled reminders for appointments.

**Fields:**
- `appointment`: ForeignKey to Appointment
- `reminder_type`: CharField ('24h', '2h', 'custom')
- `scheduled_for`: DateTimeField
- `sent`: Boolean
- `channel`: CharField ('email', 'sms', 'both')

### Waitlist
Manages waitlist for fully booked slots.

**Fields:**
- `patient`: ForeignKey to Patient
- `doctor`: ForeignKey to User (doctor)
- `preferred_date`: DateField
- `preferred_time_start`: TimeField
- `preferred_time_end`: TimeField
- `is_active`: Boolean
- `notified`: Boolean

### DoctorLeave
Tracks doctor leaves/holidays to block appointments.

**Fields:**
- `doctor`: ForeignKey to User (doctor)
- `start_date`: DateField
- `end_date`: DateField
- `reason`: CharField
- `is_approved`: Boolean

## Services

### AppointmentScheduler

Business logic service for appointment management.

**Key Methods:**

#### `get_available_slots(doctor, date)`
Returns list of available time slots for a doctor on a specific date.

```python
from datetime import date
from appointments.services import AppointmentScheduler

slots = AppointmentScheduler.get_available_slots(doctor, date(2025, 11, 20))
# Returns: [{'time': time(9, 0), 'duration': 30, 'available_spots': 1}, ...]
```

#### `book_appointment(patient, doctor, appointment_date, appointment_time, **kwargs)`
Books a new appointment and schedules reminders.

```python
appointment = AppointmentScheduler.book_appointment(
    patient=patient_obj,
    doctor=doctor_obj,
    appointment_date=date(2025, 11, 20),
    appointment_time=time(9, 0),
    reason="COVID-19 test results discussion",
    appointment_type="results_discussion",
    duration=30
)
```

#### `schedule_reminders(appointment)`
Creates reminder records for an appointment (24h and 2h before).

#### `send_due_reminders()`
Sends all due reminders (should be called periodically via Celery).

#### `cancel_appointment(appointment, cancelled_by, reason)`
Cancels an appointment and notifies the other party.

#### `complete_appointment(appointment, doctor_notes)`
Marks an appointment as completed with doctor's notes.

## URL Patterns

| URL Pattern | View | Description |
|------------|------|-------------|
| `/appointments/book/` | `book_appointment` | Book new appointment |
| `/appointments/available-slots/` | `get_available_slots_api` | API endpoint for available slots |
| `/appointments/my-appointments/` | `my_appointments` | List user's appointments |
| `/appointments/<uuid>/` | `appointment_detail` | View appointment details |
| `/appointments/<uuid>/cancel/` | `cancel_appointment` | Cancel appointment |
| `/appointments/<uuid>/reschedule/` | `reschedule_appointment` | Reschedule appointment |
| `/appointments/<uuid>/complete/` | `complete_appointment` | Mark as completed (doctor) |
| `/appointments/doctor/schedule/` | `manage_schedule` | Manage doctor's schedule |
| `/appointments/doctor/appointments/` | `doctor_appointments` | View doctor's appointments |
| `/appointments/waitlist/join/` | `join_waitlist` | Join waitlist |

## Usage Examples

### Patient: Book an Appointment

1. Navigate to `/appointments/book/`
2. Select a doctor
3. Choose a date
4. View available time slots (automatically fetched via AJAX)
5. Select a time slot
6. Fill in appointment details (type, reason, notes)
7. Submit the form
8. Receive confirmation notification

### Doctor: Manage Schedule

1. Navigate to `/appointments/doctor/schedule/`
2. Add schedule entries for each working day
3. Set:
   - Day of week
   - Start/end time
   - Slot duration (e.g., 30 minutes)
   - Max appointments per slot (usually 1)
4. Toggle active/inactive status

### Doctor: View Today's Appointments

1. Navigate to `/appointments/doctor/appointments/`
2. View today's appointments
3. View upcoming appointments (next 7 days)
4. Click on appointment to view details
5. Mark appointments as completed with notes

### Patient: Reschedule an Appointment

1. Navigate to `/appointments/my-appointments/`
2. Click on the appointment to reschedule
3. Click "Reschedule" button
4. Select new date and time
5. Submit the form
6. Old appointment is marked as "rescheduled"
7. New appointment is created

## Integration with Notifications Module

The appointments module integrates with the notifications module to send:

1. **Appointment Confirmation** (`appointment_confirmed`)
   - Sent when appointment is booked
   - Contains: patient name, doctor name, date, time, type

2. **Appointment Reminder** (`appointment_reminder`)
   - Sent 24 hours before appointment (email)
   - Sent 2 hours before appointment (SMS)
   - Contains: patient name, doctor name, date, time

3. **Appointment Cancellation** (`appointment_cancelled`)
   - Sent to the other party when appointment is cancelled
   - Contains: patient name, doctor name, date, time, cancelled_by, reason

### Setting Up Notification Templates

Notification templates should be created through the Django admin panel:

1. Go to `/admin/notifications/notificationtemplate/`
2. Create templates for:
   - `appointment_confirmed` (email/in_app)
   - `appointment_reminder` (email/sms)
   - `appointment_cancelled` (email/in_app)

**Example Template Body:**

```
Dear {patient_name},

Your appointment with {doctor_name} has been confirmed for {date} at {time}.

Appointment Type: {appointment_type}
Reason: {reason}

Please arrive 10-15 minutes early.

Best regards,
COVID-19 Detection System
```

## Admin Panel

All models are registered in the Django admin panel with:
- List views with filters and search
- Optimized querysets (select_related/prefetch_related)
- Readonly fields for tracking data
- Date hierarchies for appointments and leaves
- Inline editing where appropriate

Access admin at: `/admin/appointments/`

## Testing

### Manual Testing Checklist

1. **Appointment Booking**
   - [ ] Book appointment with available slot
   - [ ] Try booking unavailable slot (should fail)
   - [ ] Try booking past date (should fail)
   - [ ] Check confirmation notification sent
   - [ ] Check reminders scheduled

2. **Doctor Schedule**
   - [ ] Add schedule for doctor
   - [ ] Check available slots generated correctly
   - [ ] Toggle schedule active/inactive
   - [ ] Check schedule validation (end time > start time)

3. **Appointment Management**
   - [ ] View appointment details
   - [ ] Cancel appointment (patient)
   - [ ] Cancel appointment (doctor)
   - [ ] Reschedule appointment
   - [ ] Complete appointment (doctor only)

4. **Waitlist**
   - [ ] Join waitlist when slots full
   - [ ] Check time range validation

5. **Doctor Leave**
   - [ ] Add leave period
   - [ ] Check appointments blocked during leave
   - [ ] Approve/reject leave (admin)

## Dependencies

- **Django 4.2+**
- **detection app**: For Patient model
- **notifications app**: For sending notifications
- **crispy_forms**: For form styling
- **Bootstrap 5**: For UI components

## Future Enhancements

- [ ] Google Calendar integration
- [ ] Zoom/Google Meet integration for virtual appointments
- [ ] Recurring appointments
- [ ] Appointment analytics dashboard
- [ ] SMS reminders via Twilio
- [ ] Patient no-show penalties
- [ ] Bulk appointment scheduling
- [ ] Appointment export (PDF, iCal)

## Migration & Setup

After implementing this module:

1. Run migrations:
   ```bash
   python manage.py makemigrations appointments
   python manage.py migrate
   ```

2. Create notification templates in admin panel

3. Set up Celery periodic task for sending reminders:
   ```python
   # In celery.py
   @periodic_task(run_every=timedelta(minutes=5))
   def send_appointment_reminders():
       from appointments.services import AppointmentScheduler
       count = AppointmentScheduler.send_due_reminders()
       logger.info(f"Sent {count} appointment reminders")
   ```

4. Add navigation links to base template:
   ```html
   <li class="nav-item">
       <a class="nav-link" href="{% url 'appointments:my_appointments' %}">
           <i class="bi bi-calendar-check"></i> Appointments
       </a>
   </li>
   ```

## Support

For issues or questions about this module, refer to:
- Module specification: `specs/05_APPOINTMENT_SCHEDULING_SPEC.md`
- Development guide: `MODULE_DEVELOPMENT_GUIDE.md`
- Project documentation: `README.md`

## License

Part of the COVID-19 Detection System FYP project.
Student: Tan Ming Kai (24PMR12003)
Supervisor: Angkay A/P Subramaniam
Institution: TAR UMT
