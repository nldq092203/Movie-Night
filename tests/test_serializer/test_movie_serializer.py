"""
Test Case for serialization and deserialization MovieSerializer.
"""

import pytest
from movies.models import Movie
from movies.serializers import MovieSerializer

@pytest.mark.django_db
class TestMovieSerializer:
    def test_movie_serializer_serialization(self):
        """
        Test that the MovieSerializer correctly serializes the movie data.
        """
        movie = Movie.objects.create(
            imdb_id="tt1375666",
            title="Inception",
            year=2010
        )

        serializer = MovieSerializer(instance=movie)
        data = serializer.data

        # Assert that the movie data is serialized correctly
        assert data["imdb_id"] == "tt1375666"
        assert data["title"] == "Inception"
        assert data["year"] == 2010

    def test_movie_serializer_deserialization(self):
        """
        Test that the MovieSerializer correctly deserializes input data and creates a movie instance.
        """
        data = {
            "imdb_id": "tt0133093",
            "title": "The Matrix",
            "year": 1999
        }

        serializer = MovieSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

        movie = serializer.save()

        # Assert that the movie instance is created correctly
        assert movie.imdb_id == "tt0133093"
        assert movie.title == "The Matrix"
        assert movie.year == 1999

    def test_movie_serializer_invalid_data(self):
        """
        Test that the MovieSerializer handles invalid input data.
        """
        data = {
            "title": "Interstellar"  # Missing 'imdb_id' and 'year'
        }

        # Deserialize the data
        serializer = MovieSerializer(data=data)

        # Serializer should not be valid due to missing fields
        assert not serializer.is_valid()
        assert "imdb_id" in serializer.errors 
        assert "year" in serializer.errors 

    def test_movie_serializer_update(self):
        """
        Test that the MovieSerializer correctly updates an existing movie instance.
        """
        movie = Movie.objects.create(
            imdb_id="tt0133093",
            title="The Matrix",
            year=1999
        )

        data = {
            "imdb_id": "tt0133093",  # Same IMDb ID (immutable)
            "title": "The Matrix Reloaded",
            "year": 2003
        }

        serializer = MovieSerializer(instance=movie, data=data)
        assert serializer.is_valid(), serializer.errors
        updated_movie = serializer.save()

        # Assert that the movie instance is updated correctly
        assert updated_movie.imdb_id == "tt0133093"
        assert updated_movie.title == "The Matrix Reloaded"
        assert updated_movie.year == 2003

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""