#!/usr/bin/env python
"""
Create sample announcements for testing the announcements module.
Demonstrates all priority levels and various scenarios.
"""
import os
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from announcements.models import Announcement

def create_sample_announcements():
    """Create sample announcements with different priorities and states."""

    # Get admin user as author
    try:
        admin_user = User.objects.get(username='admin')
    except User.DoesNotExist:
        print("[ERROR] Admin user not found. Please create admin user first.")
        return

    # Clear existing announcements (for clean testing)
    existing_count = Announcement.objects.count()
    if existing_count > 0:
        print(f"[INFO] Deleting {existing_count} existing announcements...")
        Announcement.objects.all().delete()

    announcements_data = [
        {
            'title': 'COVID-19 Vaccination Drive',
            'message': 'Free COVID-19 vaccination available at our clinic this week. Walk-ins welcome. Please bring your identification card.',
            'priority': 'warning',
            'is_active': True,
            'expires_at': timezone.now() + timedelta(days=7),
        },
        {
            'title': 'System Maintenance Schedule',
            'message': 'The COVID-19 detection system will undergo maintenance on Saturday, 10 PM - 2 AM. Service may be temporarily unavailable.',
            'priority': 'urgent',
            'is_active': True,
            'expires_at': timezone.now() + timedelta(days=3),
        },
        {
            'title': 'New Testing Guidelines Released',
            'message': 'The Ministry of Health has released updated COVID-19 testing guidelines. All staff should review the new protocols.',
            'priority': 'info',
            'is_active': True,
            'expires_at': None,  # No expiration
        },
        {
            'title': 'Holiday Clinic Hours',
            'message': 'Please note that our clinic hours will be reduced during the upcoming public holidays. Emergency services remain available 24/7.',
            'priority': 'info',
            'is_active': True,
            'expires_at': timezone.now() + timedelta(days=14),
        },
        {
            'title': 'Critical: PPE Stock Low',
            'message': 'URGENT: Personal Protective Equipment (PPE) stock is running low. All departments must conserve supplies and order immediately.',
            'priority': 'urgent',
            'is_active': True,
            'expires_at': timezone.now() + timedelta(hours=48),
        },
        {
            'title': 'Patient Portal Updates',
            'message': 'Our patient portal has been updated with new features including appointment scheduling and test result viewing.',
            'priority': 'info',
            'is_active': True,
            'expires_at': None,
        },
        {
            'title': 'Staff Meeting Reminder',
            'message': 'Monthly staff meeting scheduled for next Monday at 2 PM in Conference Room A. Attendance is mandatory.',
            'priority': 'warning',
            'is_active': True,
            'expires_at': timezone.now() + timedelta(days=5),
        },
        {
            'title': 'Test Announcement (Inactive)',
            'message': 'This is a test announcement that has been deactivated. It should not appear in the active list.',
            'priority': 'info',
            'is_active': False,  # Inactive announcement
            'expires_at': None,
        },
        {
            'title': 'Expired Announcement',
            'message': 'This announcement has expired and should not appear in the active list.',
            'priority': 'info',
            'is_active': True,
            'expires_at': timezone.now() - timedelta(days=1),  # Expired yesterday
        },
        {
            'title': 'New X-Ray Equipment Installation',
            'message': 'State-of-the-art X-ray imaging equipment will be installed next month, improving our COVID-19 detection capabilities.',
            'priority': 'info',
            'is_active': True,
            'expires_at': timezone.now() + timedelta(days=30),
        },
        {
            'title': 'Training Session: New ML Model',
            'message': 'All radiologists and staff are invited to attend a training session on our new CrossViT-based COVID-19 detection model.',
            'priority': 'warning',
            'is_active': True,
            'expires_at': timezone.now() + timedelta(days=10),
        },
        {
            'title': 'Data Privacy Policy Update',
            'message': 'Our patient data privacy policy has been updated in compliance with new healthcare regulations. Please review at your earliest convenience.',
            'priority': 'info',
            'is_active': True,
            'expires_at': None,
        },
    ]

    print(f"[INFO] Creating {len(announcements_data)} sample announcements...")
    created_count = 0

    for data in announcements_data:
        announcement = Announcement.objects.create(
            author=admin_user,
            **data
        )
        priority_display = announcement.get_priority_display()
        status = "Active" if announcement.is_active else "Inactive"
        expires = f"Expires: {announcement.expires_at.strftime('%Y-%m-%d')}" if announcement.expires_at else "No expiration"

        print(f"[CREATED] {announcement.title}")
        print(f"          Priority: {priority_display} | Status: {status} | {expires}")
        created_count += 1

    print(f"\n[SUCCESS] Created {created_count} announcements successfully!")

    # Show statistics
    total = Announcement.objects.count()
    active = Announcement.objects.filter(is_active=True).count()
    info_count = Announcement.objects.filter(priority='info').count()
    warning_count = Announcement.objects.filter(priority='warning').count()
    urgent_count = Announcement.objects.filter(priority='urgent').count()

    print(f"\n[STATS] Database Statistics:")
    print(f"        Total announcements: {total}")
    print(f"        Active: {active}")
    print(f"        Priority breakdown:")
    print(f"          - Info: {info_count}")
    print(f"          - Warning: {warning_count}")
    print(f"          - Urgent: {urgent_count}")

    print(f"\n[NEXT] Test the announcements module:")
    print(f"       1. Visit http://localhost:8000/announcements/")
    print(f"       2. Login with:")
    print(f"          - admin/[password] (full access)")
    print(f"          - test1/[password] (staff access)")
    print(f"          - try/[password] (patient read-only)")
    print(f"       3. Follow test plan: .claude/ANNOUNCEMENTS_TEST_PLAN.md")

if __name__ == '__main__':
    create_sample_announcements()
