"""
Test URL patterns and their corresponding views for the MovieNight
"""

import pytest
from django.urls import reverse, resolve
from movies.views import (
    MyMovieNightView,
    ParticipatingMovieNightView,
    InvitedMovieNightView,
    MovieNightDetailView,
    MovieNightInvitationCreateView,
)

@pytest.mark.django_db
class TestMovieNightURLs:
    """Test URL patterns for the movie night-related views."""

    def test_my_movie_night_list_url(self):
        """Test that the my_movienight_list URL resolves to the correct view."""
        url = reverse('my_movienight_list')
        assert resolve(url).func.view_class == MyMovieNightView

    def test_movie_night_list_url(self):
        """Test that the movienight_list URL resolves to the correct view."""
        url = reverse('movienight_list')
        assert resolve(url).func.view_class == ParticipatingMovieNightView

    def test_invited_movie_night_list_url(self):
        """Test that the invited_movienight_list URL resolves to the correct view."""
        url = reverse('invited_movienight_list')
        assert resolve(url).func.view_class == InvitedMovieNightView

    def test_movie_night_detail_url(self):
        """Test that the movienight_detail URL resolves to the correct view."""
        url = reverse('movienight_detail', kwargs={'pk': '1'})
        assert resolve(url).func.view_class == MovieNightDetailView

    def test_movie_night_invitation_create_url(self):
        """Test that the movienight_invitation_create URL resolves to the correct view."""
        url = reverse('movienight_invitation_create', kwargs={'pk': '1'})
        assert resolve(url).func.view_class == MovieNightInvitationCreateView

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""