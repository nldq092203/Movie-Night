"""
Test cases for serialization and deserialization of MovieNightSerializer.
"""
import pytest
from movies.models import MovieNight, Movie, MovieNightInvitation
from movies.serializers import MovieNightSerializer, MovieNightDetailSerializer
from tests.factories import UserFactory, MovieFactory, MovieNightInvitationFactory, MovieNightFactory
from django.utils import timezone
from datetime import timedelta

@pytest.mark.django_db
class TestMovieNightSerializer:
    def test_movie_night_serializer_serialization(self):
        """
        Test that MovieNightSerializer correctly serializes a MovieNight instance,
        including the creator's email.
        """
        user = UserFactory(email="test@example.com")
        movie = MovieFactory(title="Inception")
        movie_night = MovieNightFactory(creator=user, start_time=timezone.now(), movie=movie)

        # Serialize the MovieNight instance
        serializer = MovieNightSerializer(instance=movie_night)
        data = serializer.data

        # Check that the data contains the correct fields and values
        assert data["id"] == movie_night.id
        assert data["creator"] == user.email  # Creator's email is serialized
        assert data["movie"] == movie_night.movie.id  # Movie's id is serialized

    def test_movie_night_serializer_deserialization_valid(self):
        """
        Test that MovieNightSerializer correctly deserializes valid input data
        and creates a MovieNight instance.
        """
        user = UserFactory(email="test@example.com")
        movie = MovieFactory(title="Inception")
        start_time = timezone.now() + timedelta(days=1)

        # Input data to be deserialized (creator is read-only and automatically set)
        input_data = {
            "start_time": start_time,
            "movie": movie.id,
        }

        # Deserialize the input data with the creator set automatically
        serializer = MovieNightSerializer(data=input_data, context={"request": {"user": user}})
        assert serializer.is_valid(), serializer.errors

        # Save the deserialized instance
        movie_night = serializer.save(creator=user)

        # Check that the deserialized instance has the correct data
        assert movie_night.start_time == start_time
        assert movie_night.creator == user
        assert movie_night.movie == movie

    def test_movie_night_serializer_deserialization_invalid(self):
        """
        Test that MovieNightSerializer raises validation error when the movie is missing.
        """
        user = UserFactory(email="test@example.com")
        start_time = timezone.now()

        # Input data without the required movie field
        input_data = {
            "start_time": start_time,
        }

        # Deserialize the input data and check for validation error
        serializer = MovieNightSerializer(data=input_data, context={"request": {"user": user}})
        assert not serializer.is_valid()
        assert "movie" in serializer.errors  # Check that the movie field is required

    def test_movie_night_serializer_validate_start_time_invalid(self):
        """
        Test that MovieNightSerializer raises validation error when start_time is in the past.
        """
        user = UserFactory(email="test@example.com")
        movie = MovieFactory(title="Inception")
        invalid_start_time = timezone.now() - timezone.timedelta(days=1)  # Past time

        # Input data with invalid start_time
        input_data = {
            "start_time": invalid_start_time,
            "movie": movie.id,
        }

        # Deserialize the input data and check for validation error
        serializer = MovieNightSerializer(data=input_data, context={"request": {"user": user}})
        assert not serializer.is_valid()
        assert "start_time" in serializer.errors  # Check that the start_time field is required
        assert "Start time must be in the future." in serializer.errors["start_time"]  # Customize this error message as per your implementation

@pytest.mark.django_db
class TestMovieNightDetailSerializer:
    def test_movie_night_detail_serializer_serialization(self):
        """
        Test that MovieNightSerializer correctly serializes a MovieNight instance,
        including the creator, participants, and pending invitees.
        """
        # Create user and movie
        user = UserFactory(email="test@example.com")
        movie = MovieFactory(title="Inception", runtime_minutes=148)

        # Create a MovieNight instance
        movie_night = MovieNight.objects.create(
            movie=movie,
            start_time=timezone.now(),
            creator=user,
            start_notification_sent=False
        )

        # Create invitations for participants and pending invitees
        confirmed_invitee = UserFactory(email="invitee1@example.com")
        pending_invitee = UserFactory(email="invitee2@example.com")
        
        MovieNightInvitationFactory(
            movie_night=movie_night, invitee=confirmed_invitee, attendance_confirmed=True, is_attending=True
        )
        MovieNightInvitationFactory(
            movie_night=movie_night, invitee=pending_invitee, attendance_confirmed=False
        )

        # Serialize the MovieNight instance
        serializer = MovieNightDetailSerializer(instance=movie_night, context={'request': None})
        data = serializer.data

        # Assert basic fields
        assert data["movie"] == movie.id
        assert data["creator"] == user.email
        assert data["start_notification_sent"] is False

        # Assert participants and pending invitees
        assert "participants" in data
        assert "pending_invitees" in data
        assert len(data["participants"]) == 1
        assert len(data["pending_invitees"]) == 0  # Since no request context is passed, pending invitees will be empty

    def test_movie_night_detail_serializer_deserialization(self, user):
        """
        Test that MovieNightSerializer correctly deserializes input data and creates a MovieNight instance.
        """
        movie = MovieFactory(title="Inception", runtime_minutes=148)

        input_data = {
            "movie": movie.id,
            "start_time": timezone.now() + timedelta(minutes=5),
            # "creator": user.email,
            "start_notification_sent": False
        }

        # Deserialize input data and validate
        serializer = MovieNightDetailSerializer(data=input_data)
        assert serializer.is_valid(), serializer.errors

        movie_night = serializer.save(creator=user)

        # Assertions
        assert movie_night.movie == movie
        assert movie_night.creator == user
        assert movie_night.start_notification_sent is False

    def test_movie_night_detail_serializer_with_pending_invitees(self, mocker):
        """
        Test that MovieNightSerializer correctly returns pending invitees only if the requester is the creator.
        """
        user = UserFactory(email="creator@example.com")
        movie = MovieFactory(title="Inception", runtime_minutes=148)
        movie_night = MovieNight.objects.create(
            movie=movie,
            start_time=timezone.now(),
            creator=user,
            start_notification_sent=False
        )
        
        pending_invitee = UserFactory(email="invitee2@example.com")
        MovieNightInvitationFactory(
            movie_night=movie_night, invitee=pending_invitee, attendance_confirmed=False
        )

        # Mock request context with the creator as the requesting user
        request = mocker.Mock(user=user)
        serializer = MovieNightDetailSerializer(instance=movie_night, context={'request': request})
        data = serializer.data

        # Assert that the pending invitees list is populated
        assert len(data["pending_invitees"]) == 1
        assert data["pending_invitees"][0] == "invitee2@example.com"

    def test_movie_night_detail_serializer_pending_invitees_non_creator(self, mocker):
        """
        Test that pending invitees are not returned when the user is not the creator.
        """
        user = UserFactory(email="creator@example.com")
        other_user = UserFactory(email="noncreator@example.com")
        movie = MovieFactory(title="Inception", runtime_minutes=148)
        movie_night = MovieNight.objects.create(
            movie=movie,
            start_time=timezone.now(),
            creator=user,
            start_notification_sent=False
        )
        
        pending_invitee = UserFactory(email="invitee2@example.com")
        MovieNightInvitationFactory(
            movie_night=movie_night, invitee=pending_invitee, attendance_confirmed=False
        )

        # Mock request context with a non-creator as the requesting user
        request = mocker.Mock(user=other_user)
        serializer = MovieNightDetailSerializer(instance=movie_night, context={'request': request})
        data = serializer.data

        # Assert that the pending invitees list is empty for non-creators
        assert len(data["pending_invitees"]) == 0
        

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""