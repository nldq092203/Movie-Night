"""
Tests for the NotificationSerializer that handles serializing and deserializing 
Notification objects.

Test cases:

1. **test_valid_notification_serialization**:
   - Tests that a valid Notification object is serialized correctly.

2. **test_invalid_notification_type**:
   - Ensures that an invalid `notification_type` raises a ValidationError.

3. **test_serialize_movie_night_content_object**:
   - Verifies that when the `content_object` is a `MovieNight`, it is serialized correctly.

4. **test_serialize_movie_night_invitation_content_object**:
   - Verifies that when the `content_object` is a `MovieNightInvitation`, it is serialized correctly.

5. **test_notification_serialization_without_sender**:
   - Ensures that notifications without a sender are serialized correctly.
"""

import pytest
from rest_framework.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from notifications.serializers import NotificationSerializer
from movies.models import Notification, MovieNight
from tests.factories import UserFactory, MovieNightFactory, MovieNightInvitationFactory, NotificationFactory


@pytest.mark.django_db
class TestNotificationSerializer:
    """
    Test cases for NotificationSerializer to ensure it serializes and deserializes 
    Notification objects correctly.
    """

    def test_valid_notification_serialization(self):
        """
        Test that a valid Notification object is serialized correctly.
        
        This test ensures that all fields of the NotificationSerializer are properly 
        serialized when provided with a valid Notification object, including the 
        `recipient_email`, `sender_email`, `notification_type`, and `content_object`.
        """
        # Create test data
        recipient = UserFactory(email="recipient@example.com")
        sender = UserFactory(email="sender@example.com")
        movie_night = MovieNightFactory()
        
        # Create a notification
        notification = NotificationFactory(
            recipient=recipient, 
            sender=sender, 
            content_object=movie_night, 
            notification_type="INV"
        )
        
        # Serialize the notification
        serializer = NotificationSerializer(notification)
        data = serializer.data
        
        # Assert the serialized data matches the object
        assert data['recipient_email'] == recipient.email
        assert data['sender_email'] == sender.email
        assert data['notification_type'] == "INV"
        assert data['content_object']['id'] == movie_night.id
        assert 'timestamp' in data  # Check that timestamp is present

    def test_invalid_notification_type(self):
        """
        Test that an invalid notification_type raises a ValidationError.
    
        This test ensures that when an invalid `notification_type` is provided to the
        serializer, a ValidationError is raised. It checks that the serializer's
        validation logic works as expected for the `notification_type` field.
        """
        # Create test data
        recipient = UserFactory(email="recipient@example.com")
        sender = UserFactory(email="sender@example.com")
        movie_night = MovieNightFactory()
    
        # Create an invalid notification payload
        data = {
            "recipient_email": recipient.email,
            "sender_email": sender.email,
            "notification_type": "ABC",  # Invalid type
            "content_type": ContentType.objects.get_for_model(MovieNight).id,
            "object_id": movie_night.id,
            "message": "Invalid notification type",
        }
    
        # Create serializer instance with invalid data
        serializer = NotificationSerializer(data=data)
    
        # Assert that the serializer is invalid and raises the correct error
        assert not serializer.is_valid()
        assert "notification_type" in serializer.errors
        # Update the assertion to match the actual error message produced by Django
        assert '"ABC" is not a valid choice.' in str(serializer.errors["notification_type"])

    def test_serialize_movie_night_content_object(self):
        """
        Test that the content_object is serialized correctly when it's a MovieNight.
        
        This test ensures that when the `content_object` of a Notification is a `MovieNight`, 
        the serializer correctly serializes the content object using the `MovieNightSerializer`. 
        It checks the serialized fields and data structure.
        """
        # Create test data
        recipient = UserFactory()
        sender = UserFactory()
        movie_night = MovieNightFactory()

        # Create a notification with MovieNight as the content object
        notification = NotificationFactory(
            recipient=recipient,
            sender=sender,
            content_object=movie_night,
            notification_type="REM"
        )

        # Serialize the notification
        serializer = NotificationSerializer(notification)
        data = serializer.data

        # Assert that the content_object is serialized as a MovieNight
        assert data["content_object"]["id"] == movie_night.id
        assert data["content_object"]["movie"] == movie_night.movie.id

    def test_serialize_movie_night_invitation_content_object(self):
        """
        Test that the content_object is serialized correctly when it's a MovieNightInvitation.
        
        This test ensures that when the `content_object` of a Notification is a 
        `MovieNightInvitation`, the serializer correctly serializes the content object 
        using the `MovieNightInvitationSerializer`. It checks the serialized fields and 
        data structure.
        """
        # Create test data
        recipient = UserFactory()
        sender = UserFactory()
        movie_night_invitation = MovieNightInvitationFactory()

        # Create a notification with MovieNightInvitation as the content object
        notification = NotificationFactory(
            recipient=recipient,
            sender=sender,
            content_object=movie_night_invitation,
            notification_type="INV"
        )

        # Serialize the notification
        serializer = NotificationSerializer(notification)
        data = serializer.data

        # Assert that the content_object is serialized as a MovieNightInvitation
        assert data["content_object"]["id"] == movie_night_invitation.id
        assert data["content_object"]["invitee"] == movie_night_invitation.invitee.email

    def test_notification_serialization_without_sender(self):
        """
        Test that a notification can be serialized without a sender (e.g., system notifications).
        
        This test checks that the NotificationSerializer correctly handles cases where there is 
        no sender (i.e., `sender=None`), which could happen for system-generated notifications. 
        It ensures that the `sender_email` field is serialized as `None`.
        """
        recipient = UserFactory()
        movie_night = MovieNightFactory()

        # Create a notification without a sender (sender=None)
        notification = NotificationFactory(
            recipient=recipient, 
            sender=None, 
            content_object=movie_night, 
            notification_type="UPD"
        )

        # Serialize the notification
        serializer = NotificationSerializer(notification)
        data = serializer.data

        # Assert that the sender email is None
        assert data['sender_email'] is None
        assert data['recipient_email'] == recipient.email

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""