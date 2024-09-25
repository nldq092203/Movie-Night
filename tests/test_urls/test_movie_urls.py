"""
Test URL patterns and their corresponding views for the Movie
"""
import pytest
from django.urls import reverse, resolve
from movies.views import MovieSearchView, MovieSearchResultsView, MovieSearchWaitView, MovieDetailView, MovieView

@pytest.mark.django_db
class TestMovieURLs:
    """Test URL patterns for the movies app."""

    def test_movie_search_url(self):
        """Test that the movie_search URL resolves to the correct view."""
        url = reverse('movie_search')
        assert resolve(url).func.view_class == MovieSearchView

    def test_movie_search_wait_url(self):
        """Test that the movie_search_wait URL resolves to the correct view."""
        import uuid
        valid_uuid = str(uuid.uuid4())
        url = reverse('movie_search_wait', kwargs={'result_uuid': valid_uuid})
        assert resolve(url).func.view_class == MovieSearchWaitView

    def test_movie_search_results_url(self):
        """Test that the movie_search URL resolves to the correct view."""
        url = reverse('movie_search_results')
        assert resolve(url).func.view_class == MovieSearchResultsView

    def test_movie_detail_url(self):
        """Test that the movie_detail URL resolves to the correct view."""
        url = reverse('movie_detail', kwargs={'pk': 'tt1375666'})
        assert resolve(url).func.view_class == MovieDetailView

    def test_movie_list_url(self):
        """Test that the movie_list URL resolves to the correct view."""
        url = reverse('movie_list')
        assert resolve(url).func.view_class == MovieView

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""