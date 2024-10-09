"""
Test cases for serialization and deserialization MovieDetailSerializer.
"""
import pytest
from movies.models import Movie, Genre
from movies.serializers import MovieDetailSerializer


@pytest.mark.django_db
class TestMovieDetailSerializer:
    def test_movie_detail_serializer_serialization(self):
        """
        Test that MovieDetailSerializer correctly serializes a movie instance.
        """
        genre1 = Genre.objects.create(name="Sci-Fi")
        genre2 = Genre.objects.create(name="Action")
        
        movie = Movie.objects.create(
            imdb_id="tt1375666",
            title="Inception",
            year=2010,
            runtime_minutes=148,
            plot="A thief who steals corporate secrets through the use of dream-sharing technology.",
            country="USA",
            imdb_rating=8.8,
            url_poster="http://example.com/inception.jpg",
            is_full_record=False
        )
        
        movie.genres.add(genre1, genre2)

        serializer = MovieDetailSerializer(instance=movie)
        data = serializer.data

        # Assertions to check serialized output
        assert data["title"] == "Inception"
        assert data["year"] == 2010
        assert data["imdb_id"] == "tt1375666"
        assert data["runtime_minutes"] == 148
        assert data["plot"] == "A thief who steals corporate secrets through the use of dream-sharing technology."
        assert data["country"] == "USA"
        assert data["imdb_rating"] == 8.8
        assert data["is_full_record"] == False
        assert data["url_poster"] == "http://example.com/inception.jpg"
        assert all(genre in data["genres"] for genre in ["sci-fi", "action"])


    def test_movie_detail_serializer_deserialization(self):
        """
        Test that MovieDetailSerializer correctly deserializes input data and updates the movie instance.
        """
        genre1 = Genre.objects.create(name="Sci-Fi")
        genre2 = Genre.objects.create(name="Action")
        
        movie = Movie.objects.create(
            imdb_id="tt1375666",
            title="Inception",
            year=2010,
            runtime_minutes=148,
            plot="A thief who steals corporate secrets through the use of dream-sharing technology.",
            country="USA",
            imdb_rating=8.8,
            url_poster="http://example.com/inception.jpg",
            is_full_record=False
        )
        
        movie.genres.add(genre1, genre2)

        input_data = {
            "imdb_id": "tt0133093",
            "title": "The Matrix",
            "year": 1999,
            "runtime_minutes": 136,
            "plot": "A computer hacker learns from mysterious rebels about the true nature of his reality.",
            "country": "USA",
            "imdb_rating": 8.7,
            "url_poster": "http://example.com/matrix.jpg",
            "genres": ["Sci-Fi", "Action"]
        }

        # Deserialize and validate input data
        serializer = MovieDetailSerializer(instance=movie, data=input_data)
        assert serializer.is_valid(), serializer.errors
        updated_movie = serializer.save()

        # Assertions to check updated instance
        assert updated_movie.title == "The Matrix"
        assert updated_movie.year == 1999
        assert updated_movie.imdb_id == "tt0133093"
        assert updated_movie.runtime_minutes == 136
        assert updated_movie.plot == "A computer hacker learns from mysterious rebels about the true nature of his reality."
        assert updated_movie.country == "USA"
        assert updated_movie.imdb_rating == 8.7
        assert updated_movie.url_poster == "http://example.com/matrix.jpg"
        assert updated_movie.genres.count() == 2

        # Ensure the genres were updated/created correctly
        assert Genre.objects.filter(name="sci-fi").exists()  
        assert Genre.objects.filter(name="action").exists()

    def test_movie_detail_serializer_genre_case_insensitivity(self):
        """
        Test that genres are case-insensitive and stored in lowercase.
        """
        input_data = {
            "imdb_id": "tt0133093",
            "title": "The Matrix",
            "year": 1999,
            "runtime_minutes": 136,
            "plot": "A computer hacker learns from mysterious rebels about the true nature of his reality.",
            "country": "USA",
            "imdb_rating": 8.7,
            "url_poster": "http://example.com/matrix.jpg",
            "genres": ["Sci-Fi", "Action", "sCi-Fi"]  # Duplicated genre with different case
        }

        serializer = MovieDetailSerializer(data=input_data)
        assert serializer.is_valid(), serializer.errors
        movie = serializer.save()

        # Ensure that there are only 2 unique genres and they are stored in lowercase
        assert movie.genres.count() == 2
        assert Genre.objects.filter(name="sci-fi").count() == 1
        assert Genre.objects.filter(name="action").count() == 1

    def test_movie_detail_serializer_invalid_data(self):
        """
        Test that invalid data is correctly handled by the serializer.
        """
        # Input data with invalid year and missing fields
        invalid_data = {
            "imdb_id": "tt0133093",
            "title": "The Matrix",
            "year": -1999,  # Invalid year
            "runtime_minutes": 136,
            "plot": "A computer hacker learns from mysterious rebels about the true nature of his reality.",
            "country": "USA",
            "imdb_rating": 8.7,
            "url_poster": "http://example.com/matrix.jpg",
            "genres": []
        }

        serializer = MovieDetailSerializer(data=invalid_data)

        # Ensure the serializer is invalid and returns errors
        assert not serializer.is_valid()
        assert "year" in serializer.errors  # Invalid year

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""