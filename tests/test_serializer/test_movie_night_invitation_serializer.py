"""
Test cases for serialization and deserialization MovieNightInvitationSerializer.
"""
import pytest
from movies.models import MovieNight, MovieNightInvitation
from movies.serializers import MovieNightInvitationSerializer
from tests.factories import UserFactory, MovieFactory, MovieNightFactory, MovieNightInvitationFactory
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from unittest.mock import patch
@pytest.mark.django_db
@patch('movies.tasks.send_invitation.delay')
class TestMovieNightInvitation:
    def test_movie_night_invitation_serializer_serialization(self, mock_send_invitation):
        """
        Test that MovieNightInvitationSerializer correctly serializes a MovieNightInvitation instance.
        """
        user = UserFactory(email="invitee@example.com")
        movie_night = MovieNightFactory()

        invitation = MovieNightInvitationFactory(
            movie_night=movie_night,
            invitee=user,
            attendance_confirmed=False,
            is_attending=False
        )

        # Serialize the MovieNightInvitation instance
        serializer = MovieNightInvitationSerializer(instance=invitation)
        data = serializer.data

        assert data["movie_night"] == movie_night.id
        assert data["invitee"] == user.email
        assert data["attendance_confirmed"] is False
        assert data["is_attending"] is False



    def test_movie_night_invitation_serializer_deserialization(self, mock_send_invitation):
        """
        Test that MovieNightInvitationSerializer correctly deserializes input data and creates a MovieNightInvitation instance.
        """
        user = UserFactory(email="invitee@example.com")
        movie_night = MovieNightFactory()

        input_data = {
            "movie_night": movie_night.id,
            "invitee": user.email,
            "attendance_confirmed": False,
            "is_attending": False
        }

        # Deserialize input data and validate
        serializer = MovieNightInvitationSerializer(data=input_data)
        assert serializer.is_valid(), serializer.errors

        invitation = serializer.save()

        assert invitation.movie_night == movie_night
        assert invitation.invitee == user
        assert invitation.attendance_confirmed is False
        assert invitation.is_attending is False

    def test_invitation_serializer_duplicate(self, mock_send_invitation):
        """
        Test that the serializer enforces the unique_together constraint on ('invitee', 'movie_night').
        """
        user = UserFactory(email="invitee@example.com")
        movie_night = MovieNightFactory()

        # Create the first invitation
        MovieNightInvitationFactory(invitee=user, movie_night=movie_night)

        # Attempt to create a duplicate invitation
        data = {
            "invitee": user.email,
            "movie_night": movie_night.id,
            "attendance_confirmed": False,
            "is_attending": False
        }

        serializer = MovieNightInvitationSerializer(data=data)

        # Ensure that the serializer raises a validation error for the duplicate invite
        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)

        # Assert the correct error message for the unique constraint violation
        assert "The fields invitee, movie_night must make a unique set." in str(excinfo.value)
    
    def test_invitation_serializer_invalid_invitee(self, mock_send_invitation):
        """
        Test that the serializer raises a validation error for an invalid invitee email.
        """
        movie_night = MovieNightFactory()

        # Provide an invalid email address for invitee
        data = {
            "invitee": "nonexistent@example.com",
            "movie_night": movie_night.id,
            "attendance_confirmed": False,
            "is_attending": False
        }

        serializer = MovieNightInvitationSerializer(data=data)
        
        # Ensure that the serializer raises a validation error for the invalid invitee
        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)

        # Assert the error message indicates that the user does not exist
        assert "User with email nonexistent@example.com does not exist." in str(excinfo.value)


    def test_defaults_to_false(self, mock_send_invitation):
        """
        Test that when `attendance_confirmed` and `is_attending` are not provided,
        they default to False in the serializer.
        """
        invitee = UserFactory(email="invitee@example.com")
        movie_night = MovieNightFactory()

        data = {
            "invitee": invitee.email,
            "movie_night": movie_night.id
        }

        serializer = MovieNightInvitationSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

        # Save the serializer and fetch the created object
        invitation = serializer.save()

        # Assert that attendance_confirmed and is_attending defaulted to False
        assert invitation.attendance_confirmed is False
        assert invitation.is_attending is False

    def test_provided_values(self, mock_send_invitation):
        """
        Test that when `attendance_confirmed` and `is_attending` are provided,
        they are correctly set in the serializer.
        """
        invitee = UserFactory(email="invitee@example.com")
        movie_night = MovieNightFactory()

        data = {
            "invitee": invitee.email,
            "movie_night": movie_night.id,
            "attendance_confirmed": True,
            "is_attending": True
        }

        serializer = MovieNightInvitationSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

        # Save the serializer and fetch the created object
        invitation = serializer.save()

        # Assert that attendance_confirmed and is_attending are set correctly
        assert invitation.attendance_confirmed is True
        assert invitation.is_attending is True

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""