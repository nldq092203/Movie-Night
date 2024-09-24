"""
Test URL patterns and their corresponding views for the MovieNightInvitation
"""
import pytest
from django.urls import reverse, resolve
from movies.views import (
    MyMovieNightInvitationView, MovieNightInvitationDetailView
)

@pytest.mark.django_db
class TestMovieNightInvitationURLs:

    def test_my_movie_night_invitation_list_url(self):
        """Test that the movienight_invitation_list URL resolves to the correct view."""
        url = reverse('movienight_invitation_list')
        assert resolve(url).func.view_class == MyMovieNightInvitationView

    def test_movie_night_invitation_detail_url(self):
        """Test that the movienight_invitation_detail URL resolves to the correct view."""
        url = reverse('movienight_invitation_detail', kwargs={'pk': '1'})
        assert resolve(url).func.view_class == MovieNightInvitationDetailView
        
"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""