from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Notification list
    path('', views.notification_list, name='notification_list'),
    path('<uuid:notification_id>/read/', views.mark_as_read, name='mark_as_read'),
    path('mark-all-read/', views.mark_all_as_read, name='mark_all_as_read'),

    # Preferences
    path('preferences/', views.notification_preferences, name='preferences'),

    # API for AJAX
    path('api/unread-count/', views.unread_count_api, name='unread_count_api'),
    path('api/latest/', views.latest_notifications_api, name='latest_notifications_api'),
]
