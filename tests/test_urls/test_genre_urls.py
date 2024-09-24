import pytest
from django.urls import reverse, resolve
from movies.views import (
    GenreView,
    GenreDetailView
)
@pytest.mark.django_db
class TestGenreURLs:
    """Test URL patterns for the genre-related views."""

    def test_genre_list_url(self):
        """Test that the genre list URL resolves to the correct view."""
        url = reverse('genre_list')
        assert resolve(url).func.view_class == GenreView

    def test_genre_detail_url(self):
        """Test that the genre detail URL resolves to the correct view."""
        url = reverse('genre_detail', kwargs={'pk': '1'})
        assert resolve(url).func.view_class == GenreDetailView