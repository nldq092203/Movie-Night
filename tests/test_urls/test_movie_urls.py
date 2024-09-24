"""
Test URL patterns and their corresponding views for the Movie
"""
import pytest
from django.urls import reverse, resolve
from movies.views import movie_search, MovieDetailView, MovieView

@pytest.mark.django_db
class TestMovieURLs:
    """Test URL patterns for the movies app."""

    def test_movie_search_url(self):
        """Test that the movie_search URL resolves to the correct view."""
        url = reverse('movie_search')
        assert resolve(url).func == movie_search

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