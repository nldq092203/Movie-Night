"""
Test cases for serialization and deserialization MovieNightSerializer.
"""
import pytest
from movies.models import MovieNight, Movie
from movies.serializers import MovieNightSerializer
from tests.factories import UserFactory, MovieFactory
from django.utils import timezone

@pytest.mark.django_db
class TestMovieNightSerializer:
    def test_movie_night_serializer_serialization(self):
        """
        Test that MovieNightSerializer correctly serializes a MovieNight instance.
        """
        user = UserFactory(email="test@example.com")
        movie = MovieFactory(title="Inception", runtime_minutes=148)

        movie_night = MovieNight.objects.create(
            movie=movie,
            start_time=timezone.now(),
            creator=user,
            start_notification_sent=False
        )

        serializer = MovieNightSerializer(instance=movie_night)
        data = serializer.data

        assert data["movie"] == movie.id
        assert data["creator"] == user.email
        assert data["start_notification_sent"] is False
        assert "end_time" not in data  # `end_time` is a property, so it won't be serialized



    def test_movie_night_serializer_deserialization(self):
        """
        Test that MovieNightSerializer correctly deserializes input data and creates a MovieNight instance.
        """
        user = UserFactory(email="test@example.com")
        movie = MovieFactory(title="Inception", runtime_minutes=148)

        input_data = {
            "movie": movie.id,
            "start_time": timezone.now(),
            "creator": user.email,
            "start_notification_sent": False
        }

        # Deserialize input data and validate
        serializer = MovieNightSerializer(data=input_data)
        assert serializer.is_valid(), serializer.errors

        movie_night = serializer.save()

        # Assertions
        assert movie_night.movie == movie
        assert movie_night.creator == user
        assert movie_night.start_notification_sent is False
        
"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""