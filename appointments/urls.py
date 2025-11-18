"""
Appointment & Scheduling Module - URL Configuration

This module defines URL patterns for appointment-related views.

URL Patterns:
    - /book/: Book a new appointment
    - /available-slots/: API endpoint for available slots
    - /my-appointments/: List user's appointments
    - /<uuid>/: View appointment details
    - /<uuid>/cancel/: Cancel appointment
    - /<uuid>/reschedule/: Reschedule appointment
    - /<uuid>/complete/: Complete appointment (doctor only)
    - /doctor/schedule/: Manage doctor's schedule
    - /doctor/appointments/: View doctor's appointments
    - /waitlist/join/: Join waitlist
"""

from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    # Booking
    path('book/', views.book_appointment, name='book_appointment'),
    path('available-slots/', views.get_available_slots_api, name='available_slots_api'),

    # Management
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('<uuid:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('<uuid:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('<uuid:appointment_id>/reschedule/', views.reschedule_appointment, name='reschedule_appointment'),
    path('<uuid:appointment_id>/complete/', views.complete_appointment, name='complete_appointment'),

    # Doctor schedule
    path('doctor/schedule/', views.manage_schedule, name='manage_schedule'),
    path('doctor/appointments/', views.doctor_appointments, name='doctor_appointments'),

    # Waitlist
    path('waitlist/join/', views.join_waitlist, name='join_waitlist'),
]
