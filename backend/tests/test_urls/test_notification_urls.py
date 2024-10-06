import pytest
from django.urls import reverse, resolve
from movies.views import MyNotificationView, MarkReadNotificationView

@pytest.mark.django_db
class TestNotificationURLs:
    """Test URL patterns for the notification-related views."""

    def test_notification_list_url(self):
        """Test that the notification list URL resolves to the correct view."""
        url = reverse('my_notifications')  # Ensure 'notification_list' matches your URL name
        assert resolve(url).func.view_class == MyNotificationView

    def test_mark_read_notification_url(self):
        """Test that the mark-read notification URL resolves to the correct view."""
        url = reverse('mark_read_notification', kwargs={'pk': '1'})
        assert resolve(url).func.view_class == MarkReadNotificationView