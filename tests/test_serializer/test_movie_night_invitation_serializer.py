"""
Test cases for serialization and deserialization MovieNightInvitationSerializer.
"""
import pytest
from movies.models import MovieNight, MovieNightInvitation
from movies.serializers import MovieNightInvitationSerializer
from tests.factories import UserFactory, MovieFactory, MovieNightFactory
from django.utils import timezone

@pytest.mark.django_db
class   TestMovieNightInvitation:
    def test_movie_night_invitation_serializer_serialization(self):
        """
        Test that MovieNightInvitationSerializer correctly serializes a MovieNightInvitation instance.
        """
        user = UserFactory(email="invitee@example.com")
        movie_night = MovieNightFactory()

        invitation = MovieNightInvitation.objects.create(
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



    def test_movie_night_invitation_serializer_deserialization(self):
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

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""