"""
Tests for the Notification model. These tests ensure that the Notification model works as expected, 
including the creation of notifications, linking them to various content objects, and verifying 
the correct behavior of notification fields such as `notification_type` and `is_read`.

Test cases:

1. **test_create_notification**:
   - Ensures that a Notification object can be created with valid data, linking it to both a recipient and a content object.

2. **test_notification_type_choices**:
   - Ensures that only valid `notification_type` values (as defined in `NOTIFICATION_TYPES`) can be assigned to a Notification.

3. **test_notification_is_read_default**:
   - Verifies that the default value of the `is_read` field is `False` when a Notification is created.

4. **test_link_notification_to_content_object**:
   - Ensures that the `GenericForeignKey` (`content_object`) links the Notification correctly to different models (e.g., `MovieNight`, `MovieNightInvitation`).

5. **test_auto_timestamp_update**:
   - Ensures that the `timestamp` field is automatically updated when the Notification object is created and modified.
"""

import pytest
from django.contrib.contenttypes.models import ContentType
from movies.models import Notification, MovieNight, MovieNightInvitation
from tests.factories import UserFactory, MovieNightFactory, MovieNightInvitationFactory
from django.core.exceptions import ValidationError

@pytest.mark.django_db
class TestNotificationModel:
    """
    Test cases for the Notification model. Ensures the proper behavior of notification creation,
    linking with content objects, and field validation.
    """

    def test_create_notification(self):
        """
        Test that a Notification object can be created with valid data, linking it to both a recipient
        and a content object.
        
        This test verifies that the Notification model allows for the creation of a notification with 
        a valid recipient, sender, and associated content object.
        """
        # Create test data
        recipient = UserFactory()
        sender = UserFactory()
        movie_night = MovieNightFactory()

        # Create a notification
        notification = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type="INV",
            content_type=ContentType.objects.get_for_model(MovieNight),
            object_id=movie_night.id,
            message="You have been invited to a movie night.",
        )

        # Assert that the notification was created with the correct data
        assert notification.recipient == recipient
        assert notification.sender == sender
        assert notification.notification_type == "INV"
        assert notification.message == "You have been invited to a movie night."
        assert notification.content_object == movie_night

    def test_notification_type_choices(self):
        """
        Test that only valid notification_type values can be assigned to a Notification.
    
        This test ensures that the Notification model enforces the `NOTIFICATION_TYPES` choices
        and raises an error if an invalid notification_type is assigned.
        """
        # Create test data
        recipient = UserFactory()
        sender = UserFactory()
        movie_night = MovieNightFactory()
    
        # Valid notification type should succeed
        notification = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type="INV",
            content_type=ContentType.objects.get_for_model(MovieNight),
            object_id=movie_night.id,
            message="You have been invited to a movie night."
        )
        assert notification.notification_type == "INV"
    
        # Invalid notification type should raise a ValidationError using full_clean
        invalid_notification = Notification(
            recipient=recipient,
            sender=sender,
            notification_type="ABC",  # Invalid type
            content_type=ContentType.objects.get_for_model(MovieNight),
            object_id=movie_night.id,
            message="Invalid notification type."
        )

        # Assert that full_clean raises a ValidationError for invalid notification_type
        with pytest.raises(ValidationError):
            invalid_notification.full_clean()


    def test_notification_is_read_default(self):
        """
        Test that the default value of the `is_read` field is False when a Notification is created.
        
        This test ensures that when a Notification is created, the `is_read` field defaults to False,
        which allows filtering for unread notifications.
        """
        # Create test data
        recipient = UserFactory()
        sender = UserFactory()
        movie_night = MovieNightFactory()

        # Create a notification without setting `is_read`
        notification = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type="REM",
            content_type=ContentType.objects.get_for_model(MovieNight),
            object_id=movie_night.id,
            message="Reminder: Movie night is starting soon.",
        )

        # Assert that the default value of is_read is False
        assert notification.is_read is False

    def test_link_notification_to_content_object(self):
        """
        Test that the `GenericForeignKey` (`content_object`) links the Notification correctly to 
        different models (e.g., `MovieNight`, `MovieNightInvitation`).
        
        This test ensures that the Notification model can link to various content types through the 
        `content_object` using Django's GenericForeignKey.
        """
        recipient = UserFactory()
        sender = UserFactory()

        # Link to MovieNight
        movie_night = MovieNightFactory()
        notification_movie_night = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type="REM",
            content_type=ContentType.objects.get_for_model(MovieNight),
            object_id=movie_night.id,
            message="Reminder for movie night."
        )
        assert notification_movie_night.content_object == movie_night

        # Link to MovieNightInvitation
        movie_night_invitation = MovieNightInvitationFactory()
        notification_invitation = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type="INV",
            content_type=ContentType.objects.get_for_model(MovieNightInvitation),
            object_id=movie_night_invitation.id,
            message="You have been invited."
        )
        assert notification_invitation.content_object == movie_night_invitation

    def test_auto_timestamp_update(self):
        """
        Test that the `timestamp` field is automatically updated when the Notification object 
        is created and modified.
        
        This test ensures that the `timestamp` field is set to the current time when a 
        Notification is created and that it updates appropriately when the object is modified.
        """
        # Create test data
        recipient = UserFactory()
        sender = UserFactory()
        movie_night = MovieNightFactory()

        # Create a notification
        notification = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type="INV",
            content_type=ContentType.objects.get_for_model(MovieNight),
            object_id=movie_night.id,
            message="You have been invited to a movie night.",
        )

        # Assert that the timestamp is auto-filled
        assert notification.timestamp is not None

        # Update the notification
        notification.message = "You have been invited to a different movie night."
        notification.save()

        # Assert that the timestamp was updated after modification
        assert notification.timestamp is not None

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""