import pytest
from django.urls import reverse
from rest_framework import status
from tests.factories import UserProfileFactory  


@pytest.mark.django_db
class TestProfileView:
    """Test suite for the ProfileView."""

    def test_profile_view_authenticated(self, authenticated_client, user):
        """Test retrieving a profile for an authenticated user."""
        # Create a user profile for the authenticated user
        profile = UserProfileFactory(user=user)

        # Define the URL for the profile view (assuming the ID is used in the URL)
        url = reverse('profile_detail', kwargs={'email': user.email})

        # Perform the GET request
        response = authenticated_client.get(url)

        # Assert the response is successful and data is returned correctly
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user'] == user.email
        assert response.data['name'] == profile.name
        assert response.data['bio'] == profile.bio
        assert response.data['gender'] == profile.gender

    def test_profile_view_unauthenticated(self, api_client, user):
        """Test retrieving a profile for an unauthenticated user."""
        # Create a user profile
        UserProfileFactory(user=user)

        # Define the URL for the profile view
        url = reverse('profile_detail', kwargs={'email': user.email})

        # Perform the GET request without authentication
        response = api_client.get(url)

        # Assert the response is unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_profile_not_found(self, authenticated_client):
        """Test retrieving a profile that does not exist."""
        non_existing_user_id = 9999  # Assuming this ID does not exist

        # Define the URL for the profile view with a non-existing user ID
        url = reverse('profile_detail', kwargs={'email': non_existing_user_id})

        # Perform the GET request
        response = authenticated_client.get(url)

        # Assert the response is 404 Not Found
        assert response.status_code == status.HTTP_404_NOT_FOUND