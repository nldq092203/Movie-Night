import pytest
from django.urls import reverse
from rest_framework import status
from tests.factories import UserFactory, UserProfileFactory

@pytest.mark.django_db
class TestProfileView:

    def test_retrieve_profile_by_email(self, authenticated_client):
        """
        Test retrieving a profile by email.
        """
        user = UserFactory(email="testuser@example.com")
        UserProfileFactory(user=user, bio="This is a test bio.")
        
        url = reverse('profile_by_email', kwargs={'email': user.email})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['bio'] == "This is a test bio."
        assert response.data['user'] == user.id