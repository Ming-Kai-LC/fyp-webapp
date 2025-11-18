from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Notification, NotificationPreference
from .forms import NotificationPreferenceForm


@login_required
def notification_list(request):
    """
    Display all notifications for the current user
    """
    notifications = Notification.objects.filter(recipient=request.user)

    # Filter by status if requested
    status_filter = request.GET.get('status')
    if status_filter:
        notifications = notifications.filter(status=status_filter)

    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Count unread notifications
    unread_count = Notification.objects.filter(
        recipient=request.user,
        status='sent'
    ).count()

    context = {
        'page_obj': page_obj,
        'unread_count': unread_count,
        'status_filter': status_filter,
    }

    return render(request, 'notifications/notification_list.html', context)


@login_required
@require_http_methods(["POST"])
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

    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': 'Notification marked as read'})

    messages.success(request, 'Notification marked as read')
    return redirect('notifications:notification_list')


@login_required
@require_http_methods(["POST"])
def mark_all_as_read(request):
    """
    Mark all unread notifications as read
    """
    from django.utils import timezone

    updated = Notification.objects.filter(
        recipient=request.user,
        status='sent'
    ).update(
        status='read',
        read_at=timezone.now()
    )

    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': f'{updated} notifications marked as read',
            'count': updated
        })

    messages.success(request, f'{updated} notifications marked as read')
    return redirect('notifications:notification_list')


@login_required
def notification_preferences(request):
    """
    View and update notification preferences
    """
    try:
        preferences = NotificationPreference.objects.get(user=request.user)
    except NotificationPreference.DoesNotExist:
        preferences = NotificationPreference.objects.create(user=request.user)

    if request.method == 'POST':
        form = NotificationPreferenceForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notification preferences updated successfully')
            return redirect('notifications:preferences')
    else:
        form = NotificationPreferenceForm(instance=preferences)

    context = {
        'form': form,
        'preferences': preferences,
    }

    return render(request, 'notifications/notification_preferences.html', context)


@login_required
def unread_count_api(request):
    """
    API endpoint to get unread notification count
    """
    count = Notification.objects.filter(
        recipient=request.user,
        status='sent'
    ).count()

    return JsonResponse({'unread_count': count})


@login_required
def latest_notifications_api(request):
    """
    API endpoint to get latest notifications
    """
    limit = int(request.GET.get('limit', 10))

    notifications = Notification.objects.filter(
        recipient=request.user
    )[:limit]

    data = [{
        'id': str(n.notification_id),
        'title': n.title,
        'message': n.message,
        'status': n.status,
        'priority': n.priority,
        'created_at': n.created_at.isoformat(),
        'action_url': n.action_url,
    } for n in notifications]

    return JsonResponse({'notifications': data})
