"""
Unit tests for movie-related API views.

This file contains test cases for the following functionalities:
1. `movie_search` view (POST):
   - Searching for movies by title with a valid search term.
   - Handling missing or invalid search terms.
   - Handling exceptions during the search process.
   - Returning an empty result set when no movies match the search term.
2. `movie_detail` view (GET):
   - Retrieving detailed information about a specific movie.
   - Handling exceptions that occur during the detail fetch process.
   - Handling authentication and authorization: Unauthenticated User cannot view movie detail.

Each test is designed to mock the necessary components (e.g., `search_and_save`, `fill_movie_details`, and `Movie.objects.filter`) to isolate the logic being tested and avoid actual database or API calls.
"""
import pytest
from tests.factories import MovieFactory, GenreFactory
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestMovieSearch:

    def test_movie_search_valid_term(self, any_client, mocker):
        """Returns movies for a valid search term."""
        # Mock the search_and_save function to prevent actual API calls
        mocker.patch('movies.views.search_and_save')

        # Mock the Movie.objects.filter method to return sample data
        sample_movies = [
            MovieFactory(title="Test Movie 1"),
            MovieFactory()
        ]
        mock_queryset = mocker.Mock()
        mock_queryset.only.return_value = sample_movies
        # Mock the filter() method to return the mock QuerySet
        mocker.patch('movies.views.Movie.objects.filter', return_value=mock_queryset)
       
        url = reverse('movie_search')
        data = {'term': 'Test'}
        response = any_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) == 2
        assert response.data['results'][0]['title'] == 'Test Movie 1'

    def test_movie_search_missing_term(self, any_client):
        """Returns 400 error when no search term is provided."""
        url = reverse('movie_search')
        data = {}  # No 'term' provided
        response = any_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error'] == 'Search term is required.'

    def test_movie_search_exception(self, any_client, mocker):
        """Returns 500 error on internal exception."""
        # Mock search_and_save to raise an exception
        mocker.patch('movies.views.search_and_save', side_effect=Exception('Test Exception'))

        url = reverse('movie_search')
        data = {'term': 'Test'}
        response = any_client.post(url, data, format='json')

        # Assert: Ensure that the exception is correctly caught and a 500 error is returned
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data['error'] == "An error occurred while processing your request."

    def test_movie_search_empty_results(self,any_client, mocker):
        """Returns empty list when no movies match the search term."""
        # Mock the search_and_save function
        mocker.patch('movies.views.search_and_save')

        # Mock Movie.objects.filter to return an empty list
        mock_queryset = mocker.Mock()
        mock_queryset.only.return_value = []
        mocker.patch('movies.views.Movie.objects.filter', return_value=mock_queryset)

        url = reverse('movie_search')
        data = {'term': 'NoResults'}
        response = any_client.post(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'] == []
        assert response.data['message'] == 'No movies found matching your search term.'

class TestMovieDetailView:
    def test_movie_detail_view_authenticated(self, authenticated_client, sample_movie, mocker):
        """Returns movie details successfully."""
        # Mock fill_movie_details to prevent actual API calls
        mocker.patch('movies.views.fill_movie_details')

        url = reverse('movie_detail', kwargs={'pk': sample_movie.pk})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['imdb_id'] == sample_movie.imdb_id
        assert response.data['title'] == sample_movie.title

    def test_movie_detail_view_exception(self, authenticated_client, sample_movie, mocker):
        """Returns 500 error on internal exception."""
        # Mock fill_movie_details to raise an exception
        mocker.patch('movies.views.fill_movie_details', side_effect=Exception('Test Exception'))

        url = reverse('movie_detail', kwargs={'pk': sample_movie.pk})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data['error'] == 'An unexpected error occurred.'

    def test_movie_detail_view_unauthenticated(self, any_client, sample_movie, mocker):
        """Returns 401 error - Unauthenticated""" 
        mocker.patch("movies.views.fill_movie_details")

        url = reverse('movie_detail', kwargs={'pk': sample_movie.pk})
        response = any_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED   

@pytest.mark.django_db
class TestMovieView:
    
    def test_movie_list_view(self, any_client):
        """
        Test that the movie list view returns all movies without filters.
        """
        # Create some sample movies
        MovieFactory(title="Movie 1", year=2020, runtime_minutes=120)
        MovieFactory(title="Movie 2", year=2019, runtime_minutes=90)

        # Access the list view
        url = reverse('movie_list')
        response = any_client.get(url)

        # Assert: response should be 200 OK and return the movies
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2  # Two movies created
        assert response.data['results'][0]['title'] == "Movie 1"
        assert response.data['results'][1]['title'] == "Movie 2"

    def test_movie_list_view_with_filters(self, any_client):
        """
        Test that the movie list view returns filtered results based on query parameters.
        """
        # Create genres
        genre1 = GenreFactory(name="Action")
        genre2 = GenreFactory(name="Drama")

        # Create some movies with genres
        MovieFactory(title="Action Movie", year=2021, genres=[genre1], runtime_minutes=150)
        MovieFactory(title="Drama Movie", year=2020, genres=[genre2], runtime_minutes=120)

        # Access the list view with filter (genre: Action)
        url = reverse('movie_list') + "?genres=action"
        response = any_client.get(url)

        # Assert: only movies with the Action genre are returned
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]['title'] == "Action Movie"

    def test_movie_list_view_with_ordering(self, any_client):
        """
        Test that the movie list view supports ordering by fields like 'year' and 'runtime_minutes'.
        """
        # Create some sample movies
        MovieFactory(title="Movie 1", year=2018, runtime_minutes=150)
        MovieFactory(title="Movie 2", year=2020, runtime_minutes=100)

        # Access the list view with ordering by 'year'
        url = reverse('movie_list') + "?ordering=-year"
        response = any_client.get(url)

        # Assert: movies should be ordered by year (descending)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"][0]['year'] == 2020  # The movie with the latest year should be first
        assert response.data["results"][1]['year'] == 2018  # The older movie should be second

    def test_movie_list_view_empty(self, any_client):
        """
        Test that the movie list view returns an empty list when there are no matching results.
        """
        # No movies in the database
        url = reverse('movie_list')
        response = any_client.get(url)

        # Assert: response should be 200 OK, but return an empty list
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 0
    
"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""