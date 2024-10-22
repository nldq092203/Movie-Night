"""
Test URL patterns and their corresponding views for the Profile
"""
import pytest
from django.urls import reverse, resolve
from movienight_profile.views import ProfileView


@pytest.mark.django_db
class TestProfileView:
    """Test ProfileView that retrieves user profile by email."""

    def test_profile_url_resolves(self):
        """Test that the profile URL resolves to the correct view."""
        url = reverse('profile_detail', kwargs={'email': 'test@gmail.com'})
        assert resolve(url).func.view_class == ProfileView

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""