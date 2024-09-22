"""
Test Case for serialization and deserialization GenreSerializer.
"""
import pytest
from movies.models import Genre
from movies.serializers import GenreSerializer

@pytest.mark.django_db
class TestGenreSerializer:
    def test_genre_serializer_serialization(self):
        """
        Test that the GenreSerializer correctly serializes the genre data.
        """
        genre = Genre.objects.create(name="Comedy")

        serializer = GenreSerializer(instance=genre)
        data = serializer.data

        # Assert that the genre name is serialized correctly
        assert data['name'] == "comedy"


    def test_genre_serializer_deserialization(self):
        """
        Test that the GenreSerializer correctly deserializes input data and converts the genre name to lowercase.
        """
        data = {
            "name": "Action"
        }

        serializer = GenreSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        genre = serializer.save()

        # Assert that the genre name is saved in lowercase
        assert genre.name == "action"

    def test_genre_serializer_invalid_data(self):
        """
        Test that the GenreSerializer handles invalid input data.
        """
        data = {}

        serializer = GenreSerializer(data=data)

        # Serializer should not be valid due to missing 'name' field
        assert not serializer.is_valid()
        assert "name" in serializer.errors 



    def test_genre_serializer_existing_genre(self):
        """
        Test that the GenreSerializer does not allow duplicate genres due to unique constraint.
        """
        Genre.objects.create(name="Drama")

        data = {
            "name": "DRAMA"
        }

        serializer = GenreSerializer(data=data)

        # Serializer should not be valid because the genre name should already exist (after conversion to lowercase)
        assert not serializer.is_valid()
        assert "name" in serializer.errors

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""