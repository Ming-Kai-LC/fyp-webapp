"""
Announcements Views
Demonstrates usage of foundation components and role-based permissions
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone

# ✅ FOUNDATION: Use decorators from existing modules
from reporting.decorators import staff_required

from .models import Announcement
from .forms import AnnouncementForm
from .constants import (
    SUCCESS_ANNOUNCEMENT_CREATED,
    SUCCESS_ANNOUNCEMENT_UPDATED,
    ANNOUNCEMENTS_PER_PAGE,
    VIEW_ANNOUNCEMENT_LIST,
)


@login_required
def announcement_list(request):
    """
    List all active announcements.

    ✅ Accessible to all authenticated users
    ✅ Shows only active, non-expired announcements
    ✅ Demonstrates use of template components and tags
    """
    # Get all active announcements
    announcements = Announcement.objects.filter(is_active=True)

    # Filter out expired announcements
    now = timezone.now()
    active_announcements = [
        a for a in announcements
        if a.expires_at is None or a.expires_at > now
    ]

    # Paginate results
    paginator = Paginator(active_announcements, ANNOUNCEMENTS_PER_PAGE)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'announcements': page_obj,
        'page_obj': page_obj,
        'total_count': len(active_announcements),
    }

    return render(request, 'announcements/announcement_list.html', context)


@staff_required  # ✅ FOUNDATION: Staff/admin only
def announcement_create(request):
    """
    Create a new announcement.

    ✅ Staff/Admin only
    ✅ Demonstrates use of Bootstrap widgets in forms
    ✅ Uses success messages
    """
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.author = request.user
            announcement.save()

            messages.success(request, SUCCESS_ANNOUNCEMENT_CREATED)
            return redirect(VIEW_ANNOUNCEMENT_LIST)
    else:
        form = AnnouncementForm()

    context = {
        'form': form,
        'title': 'Create Announcement',
    }

    return render(request, 'announcements/announcement_form.html', context)


@staff_required  # ✅ FOUNDATION: Staff/admin only
def announcement_update(request, pk):
    """
    Update an existing announcement.

    ✅ Staff/Admin only
    ✅ Can only update own announcements (unless admin)
    """
    announcement = get_object_or_404(Announcement, pk=pk)

    # Check if user can edit this announcement
    if not request.user.profile.is_admin():
        if announcement.author != request.user:
            messages.error(request, "You can only edit your own announcements.")
            return redirect(VIEW_ANNOUNCEMENT_LIST)

    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, SUCCESS_ANNOUNCEMENT_UPDATED)
            return redirect(VIEW_ANNOUNCEMENT_LIST)
    else:
        form = AnnouncementForm(instance=announcement)

    context = {
        'form': form,
        'announcement': announcement,
        'title': 'Update Announcement',
    }

    return render(request, 'announcements/announcement_form.html', context)


@login_required
def announcement_detail(request, pk):
    """
    View announcement details.

    ✅ Accessible to all authenticated users
    ✅ Shows full announcement information
    """
    announcement = get_object_or_404(Announcement, pk=pk)

    # Check if announcement is active and not expired
    if not announcement.is_active or announcement.is_expired():
        if not request.user.profile.is_staff_or_admin():
            messages.error(request, "This announcement is no longer available.")
            return redirect(VIEW_ANNOUNCEMENT_LIST)

    context = {
        'announcement': announcement,
    }

    return render(request, 'announcements/announcement_detail.html', context)
