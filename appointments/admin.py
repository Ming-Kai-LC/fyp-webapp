"""
Appointment & Scheduling Module - Admin Configuration

This module configures the Django admin interface for appointment models.

Admin Classes:
    - DoctorScheduleAdmin: Admin for doctor schedules
    - AppointmentAdmin: Admin for appointments
    - AppointmentReminderAdmin: Admin for appointment reminders
    - WaitlistAdmin: Admin for waitlist entries
    - DoctorLeaveAdmin: Admin for doctor leaves
"""

from django.contrib import admin
from .models import DoctorSchedule, Appointment, AppointmentReminder, Waitlist, DoctorLeave


@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    """
    Admin interface for DoctorSchedule model.

    Features:
    - List display with key fields
    - Filtering by doctor, day, and active status
    - Search by doctor name
    - Inline editing
    """
    list_display = [
        'doctor',
        'get_day_display',
        'start_time',
        'end_time',
        'slot_duration',
        'max_appointments_per_slot',
        'is_active'
    ]
    list_filter = ['day_of_week', 'is_active', 'doctor']
    search_fields = ['doctor__username', 'doctor__first_name', 'doctor__last_name']
    list_editable = ['is_active']
    ordering = ['doctor', 'day_of_week', 'start_time']

    fieldsets = (
        ('Doctor Information', {
            'fields': ('doctor',)
        }),
        ('Schedule Details', {
            'fields': ('day_of_week', 'start_time', 'end_time', 'is_active')
        }),
        ('Slot Configuration', {
            'fields': ('slot_duration', 'max_appointments_per_slot')
        }),
    )

    def get_day_display(self, obj):
        """Display day of week as text."""
        return obj.get_day_of_week_display()
    get_day_display.short_description = 'Day of Week'


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """
    Admin interface for Appointment model.

    Features:
    - List display with key fields
    - Filtering by status, date, type, and doctor
    - Search by patient and doctor names
    - Date hierarchy
    - Readonly fields for tracking data
    """
    list_display = [
        'appointment_id',
        'patient',
        'doctor',
        'appointment_date',
        'appointment_time',
        'appointment_type',
        'status',
        'is_virtual'
    ]
    list_filter = [
        'status',
        'appointment_type',
        'is_virtual',
        'appointment_date',
        'doctor'
    ]
    search_fields = [
        'patient__user__username',
        'patient__user__first_name',
        'patient__user__last_name',
        'doctor__username',
        'doctor__first_name',
        'doctor__last_name',
        'appointment_id'
    ]
    date_hierarchy = 'appointment_date'
    readonly_fields = [
        'appointment_id',
        'created_at',
        'confirmed_at',
        'completed_at',
        'cancelled_at',
        'reminder_sent_at',
        'end_time'
    ]
    ordering = ['-appointment_date', '-appointment_time']

    fieldsets = (
        ('Appointment Information', {
            'fields': ('appointment_id', 'patient', 'doctor')
        }),
        ('Date & Time', {
            'fields': ('appointment_date', 'appointment_time', 'duration', 'end_time')
        }),
        ('Appointment Details', {
            'fields': ('appointment_type', 'reason', 'notes', 'is_virtual', 'video_link')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Booking Information', {
            'fields': ('booked_by', 'created_at'),
            'classes': ('collapse',)
        }),
        ('Confirmation', {
            'fields': ('confirmed_at', 'confirmation_sent'),
            'classes': ('collapse',)
        }),
        ('Reminders', {
            'fields': ('reminder_sent', 'reminder_sent_at'),
            'classes': ('collapse',)
        }),
        ('Completion', {
            'fields': ('completed_at', 'doctor_notes'),
            'classes': ('collapse',)
        }),
        ('Cancellation', {
            'fields': ('cancelled_at', 'cancellation_reason'),
            'classes': ('collapse',)
        }),
        ('Follow-up', {
            'fields': ('is_follow_up', 'parent_appointment'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('patient', 'patient__user', 'doctor', 'booked_by')


@admin.register(AppointmentReminder)
class AppointmentReminderAdmin(admin.ModelAdmin):
    """
    Admin interface for AppointmentReminder model.

    Features:
    - List display with key fields
    - Filtering by reminder type, sent status, and channel
    - Search by appointment ID
    - Readonly fields for tracking data
    """
    list_display = [
        'appointment',
        'reminder_type',
        'scheduled_for',
        'sent',
        'sent_at',
        'channel'
    ]
    list_filter = ['reminder_type', 'sent', 'channel']
    search_fields = ['appointment__appointment_id']
    readonly_fields = ['sent_at']
    ordering = ['scheduled_for']

    fieldsets = (
        ('Reminder Information', {
            'fields': ('appointment', 'reminder_type', 'channel')
        }),
        ('Scheduling', {
            'fields': ('scheduled_for',)
        }),
        ('Status', {
            'fields': ('sent', 'sent_at')
        }),
    )

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('appointment', 'appointment__patient', 'appointment__doctor')


@admin.register(Waitlist)
class WaitlistAdmin(admin.ModelAdmin):
    """
    Admin interface for Waitlist model.

    Features:
    - List display with key fields
    - Filtering by active status, doctor, and date
    - Search by patient and doctor names
    - Readonly fields for tracking data
    """
    list_display = [
        'patient',
        'doctor',
        'preferred_date',
        'preferred_time_start',
        'preferred_time_end',
        'appointment_type',
        'is_active',
        'notified',
        'created_at'
    ]
    list_filter = [
        'is_active',
        'notified',
        'appointment_type',
        'preferred_date',
        'doctor'
    ]
    search_fields = [
        'patient__user__username',
        'patient__user__first_name',
        'patient__user__last_name',
        'doctor__username',
        'doctor__first_name',
        'doctor__last_name'
    ]
    readonly_fields = ['created_at', 'notified_at']
    ordering = ['created_at']

    fieldsets = (
        ('Patient & Doctor', {
            'fields': ('patient', 'doctor')
        }),
        ('Preferences', {
            'fields': (
                'preferred_date',
                'preferred_time_start',
                'preferred_time_end',
                'appointment_type',
                'reason'
            )
        }),
        ('Status', {
            'fields': ('is_active', 'notified', 'notified_at', 'converted_to_appointment')
        }),
        ('Tracking', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('patient', 'patient__user', 'doctor', 'converted_to_appointment')


@admin.register(DoctorLeave)
class DoctorLeaveAdmin(admin.ModelAdmin):
    """
    Admin interface for DoctorLeave model.

    Features:
    - List display with key fields
    - Filtering by approval status and doctor
    - Search by doctor name
    - Date hierarchy
    - Readonly fields for tracking data
    """
    list_display = [
        'doctor',
        'start_date',
        'end_date',
        'reason',
        'is_approved',
        'created_at'
    ]
    list_filter = ['is_approved', 'doctor', 'start_date']
    search_fields = [
        'doctor__username',
        'doctor__first_name',
        'doctor__last_name',
        'reason'
    ]
    date_hierarchy = 'start_date'
    readonly_fields = ['created_at']
    ordering = ['-start_date']
    list_editable = ['is_approved']

    fieldsets = (
        ('Doctor Information', {
            'fields': ('doctor',)
        }),
        ('Leave Period', {
            'fields': ('start_date', 'end_date', 'reason')
        }),
        ('Approval', {
            'fields': ('is_approved',)
        }),
        ('Tracking', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('doctor')
