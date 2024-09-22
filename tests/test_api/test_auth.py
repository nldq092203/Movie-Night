"""
Test cases for Login and Refresh AccessToken
    1. Test Successful Login and Obtain JWT Tokens
    2. Test Login with Incorrect Password
    3. Test Login with Inactive Account
    4. Test Refresh Access Token
"""
import pytest
from django.contrib.auth import get_user_model
from tests.factories import UserFactory
from rest_framework import status

User = get_user_model()

@pytest.mark.django_db
class TestLoginAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Automatically set up user for each test"""
        self.user = UserFactory(
            email="testuser@example.com",
            password="defaultpassword",
            is_active=True 
        )    

    def test_success_login_and_obtain_jwt_tokens(self, api_client):
        """ Test Successful Login and Obtain JWT Tokens """
        url = '/auth/token/'
        payload = {
            'email': self.user.email,
            'password': 'defaultpassword'
        }

        response = api_client.post(url, payload, format='json')

        assert response.status_code == status.HTTP_200_OK

        # Check that the response contains 'access' and 'refresh' tokens
        assert 'access' in response.data
        assert 'refresh' in response.data
    
    def test_incorrect_password_login(self, api_client):
        """ Test Login with Incorrect Password"""
        url = '/auth/token/'
        payload = {
            'email': self.user.email,
            'password': 'wrongppassword'
        }

        response = api_client.post(url, payload, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Check that the response does not contain 'access' and 'refresh' tokens
        assert 'access' not in response.data
        assert 'refresh' not in response.data

    def test_inactive_account_login(self, api_client):
        """Test Login with Inactive Account"""
        self.user.is_active = False
        self.user.save()

        url = '/auth/token/'
        payload = {
            'email': self.user.email,
            'password': 'defaultpassword'
        }

        response = api_client.post(url, payload, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Check that the response does not contain 'access' and 'refresh' tokens
        assert 'access' not in response.data
        assert 'refresh' not in response.data

    def test_refresh_access_token(self, api_client):
        """ Test Refresh Access Token """
        login_url = '/auth/token/'
        login_data = {
            'email': self.user.email,
            'password': 'defaultpassword'
        }
        login_response = api_client.post(login_url, login_data, format='json')

        assert login_response.status_code == status.HTTP_200_OK
        refresh_token = login_response.data['refresh']

        refresh_url = '/auth/token/refresh/'

        refresh_data = {
            'refresh': refresh_token
        }

        refresh_response = api_client.post(refresh_url, refresh_data, format='json')

        assert refresh_response.status_code == status.HTTP_200_OK
        assert 'access' in refresh_response.data
    

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""