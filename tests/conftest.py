"""
Define fixtures to use in tests.
"""
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from tests.factories import MovieFactory
User = get_user_model()

@pytest.fixture(scope="class")
def api_client():
    """Fixture to provide an API client"""
    yield APIClient()

@pytest.fixture
def user(db):
    user = User.objects.create_user(email='testuser@gmail.com', password='testpass')
    return user

@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def sample_movie(db):
    """Creates a sample movie for testing"""
    return MovieFactory(imdb_id='tt1234567', title='Test Movie', year=2000)

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""