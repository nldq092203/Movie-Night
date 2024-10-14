from django.urls import path
from notifications.views import (
    MyNotificationView,
    MarkReadNotificationView,
    MarkAllAsSeenView
)

urlpatterns = [
    path('notifications/', MyNotificationView.as_view(), name='my_notifications'),
    path('notifications/<str:pk>/mark-read/', MarkReadNotificationView.as_view(), name='mark_read_notification'),
    path('notifications/mark-all-seen/', MarkAllAsSeenView.as_view(), name='mark_all_seen'),
]