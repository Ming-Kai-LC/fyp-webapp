from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Notification, NotificationPreference
from .forms import NotificationPreferenceForm


@login_required
def notification_list(request):
    """
    Display list of notifications for the current user
    """
    notifications = Notification.objects.filter(recipient=request.user)

    # Filter by status if provided
    status_filter = request.GET.get('status', 'all')
    if status_filter == 'unread':
        notifications = notifications.exclude(status='read')
    elif status_filter == 'read':
        notifications = notifications.filter(status='read')

    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Count unread notifications
    unread_count = Notification.objects.filter(
        recipient=request.user,
        status__in=['pending', 'sent']
    ).count()

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'unread_count': unread_count,
    }
    return render(request, 'notifications/notification_list.html', context)


@login_required
def mark_as_read(request, notification_id):
    """
    Mark a single notification as read
    """
    notification = get_object_or_404(
        Notification,
        notification_id=notification_id,
        recipient=request.user
    )
    notification.mark_as_read()

    # If AJAX request, return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})

    # Otherwise redirect back
    messages.success(request, 'Notification marked as read.')
    return redirect('notifications:notification_list')


@login_required
def mark_all_as_read(request):
    """
    Mark all notifications as read for the current user
    """
    if request.method == 'POST':
        notifications = Notification.objects.filter(
            recipient=request.user,
            status__in=['pending', 'sent']
        )

        count = notifications.count()
        for notification in notifications:
            notification.mark_as_read()

        messages.success(request, f'Marked {count} notifications as read.')

    return redirect('notifications:notification_list')


@login_required
def notification_preferences(request):
    """
    Manage notification preferences
    """
    # Get or create preferences
    try:
        preferences = NotificationPreference.objects.get(user=request.user)
    except NotificationPreference.DoesNotExist:
        preferences = NotificationPreference.objects.create(user=request.user)

    if request.method == 'POST':
        form = NotificationPreferenceForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notification preferences updated successfully.')
            return redirect('notifications:preferences')
    else:
        form = NotificationPreferenceForm(instance=preferences)

    context = {
        'form': form,
        'preferences': preferences,
    }
    return render(request, 'notifications/preferences.html', context)


# ============================================================================
# API Endpoints for AJAX
# ============================================================================

@login_required
def unread_count_api(request):
    """
    API endpoint to get unread notification count
    """
    count = Notification.objects.filter(
        recipient=request.user,
        status__in=['pending', 'sent']
    ).count()

    return JsonResponse({'count': count})


@login_required
def latest_notifications_api(request):
    """
    API endpoint to get latest notifications (for real-time updates)
    """
    limit = int(request.GET.get('limit', 5))

    notifications = Notification.objects.filter(
        recipient=request.user
    )[:limit]

    data = []
    for notification in notifications:
        data.append({
            'id': str(notification.notification_id),
            'title': notification.title,
            'message': notification.message,
            'priority': notification.priority,
            'status': notification.status,
            'created_at': notification.created_at.isoformat(),
            'action_url': notification.action_url,
        })

    return JsonResponse({'notifications': data})
