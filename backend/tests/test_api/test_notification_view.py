"""
Test cases for Notification-related API views including:

1. **TestMyNotificationView**:
   - Tests for listing, filtering, and accessing notifications for the authenticated user.
   - Ensures that the correct notifications are displayed and the user can filter by `is_read`, `notification_type`, and `timestamp`.
   - Validates that unauthenticated users cannot access the notification list.

2. **TestMarkReadNotificationView**:
   - Tests for marking notifications as read.
   - Ensures that the authenticated user can mark their notifications as read, and the API properly handles already-read notifications.
   - Verifies that users cannot mark notifications for others and handles non-existent notifications gracefully.

The tests cover both authenticated and unauthenticated access, ensuring that the API correctly enforces permissions and allows proper filtering and updating of notifications.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from movies.models import Notification
from tests.factories import UserFactory, NotificationFactory
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@pytest.mark.django_db
class TestMyNotificationView:
    def test_list_notifications(self, authenticated_client, user):
        """
        Test that the authenticated user can list their notifications.
        """
        # Create notifications for the authenticated user
        NotificationFactory(recipient=user, is_read=False)
        NotificationFactory(recipient=user, is_read=True)

        # Create notifications for another user
        other_user = UserFactory()
        NotificationFactory(recipient=other_user, is_read=False)

        url = reverse('my_notifications')  # Ensure this is the correct URL name
        response = authenticated_client.get(url)

        # Assert that only the user's notifications are listed
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2  # Two notifications for the user

    def test_filter_notifications_by_is_read(self, authenticated_client, user):
        """
        Test that notifications can be filtered by 'is_read' status.
        """
        # Create notifications for the authenticated user
        NotificationFactory(recipient=user, is_read=False)
        NotificationFactory(recipient=user, is_read=True)

        url = reverse('my_notifications') + '?is_read=true'
        response = authenticated_client.get(url)

        # Assert that only read notifications are listed
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['is_read'] is True

    def test_filter_notifications_by_notification_type(self, authenticated_client, user):
        """
        Test that notifications can be filtered by 'notification_type'.
        """
        # Create notifications with different types for the authenticated user
        NotificationFactory(recipient=user, notification_type='INV')
        NotificationFactory(recipient=user, notification_type='UPD')

        url = reverse('my_notifications') + '?notification_type=INV'
        response = authenticated_client.get(url)

        # Assert that only notifications of type 'INV' are listed
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['notification_type'] == 'INV'

    def test_unauthenticated_user_cannot_access_notifications(self, any_client):
        """
        Test that unauthenticated users cannot access the notification list.
        """
        url = reverse('my_notifications')
        response = any_client.get(url)

        # Assert that the response is 401 Unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestMarkReadNotificationView:
    
    def test_mark_notification_as_read(self, authenticated_client, user):
        """
        Test that a user can mark their notification as read.
        """
        # Create a notification for the user
        notification = NotificationFactory(recipient=user, is_read=False)

        # Send PATCH request to mark the notification as read
        url = reverse('mark_read_notification', kwargs={'pk': notification.pk})
        response = authenticated_client.patch(url)

        # Assert that the notification was marked as read
        assert response.status_code == status.HTTP_200_OK
        notification.refresh_from_db()
        assert notification.is_read is True

    def test_already_read_notification(self, authenticated_client, user):
        """
        Test that if a notification is already read, the API responds with a message indicating so.
        """
        # Create a notification that is already read
        notification = NotificationFactory(recipient=user, is_read=True)

        # Send PATCH request to mark the already-read notification as read
        url = reverse('mark_read_notification', kwargs={'pk': notification.pk})
        response = authenticated_client.patch(url)

        # Assert that the response indicates the notification is already read
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == "Notification already marked as read."

    def test_unauthorized_user_cannot_mark_notification(self, authenticated_client):
        """
        Test that a user cannot mark a notification as read if they are not the recipient.
        """
        # Create a notification for another user
        other_user = UserFactory()
        notification = NotificationFactory(recipient=other_user, is_read=False)

        # Send PATCH request to mark the notification as read with an unauthorized user
        url = reverse('mark_read_notification', kwargs={'pk': notification.pk})
        response = authenticated_client.patch(url)

        # Assert that the response is 404, as the notification isn't found for this user
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_notification_not_found(self, authenticated_client, user):
        """
        Test that a 404 response is returned if the notification does not exist.
        """
        # Send PATCH request for a non-existing notification
        url = reverse('mark_read_notification', kwargs={'pk': 9999})  # Assuming this ID doesn't exist
        response = authenticated_client.patch(url)

        # Assert that the response is 404 Not Found
        assert response.status_code == status.HTTP_404_NOT_FOUND


"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""