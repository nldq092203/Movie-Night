"""
Test cases for User Registration and User Management
    Registration
    1. Test user successful registration
    2. Test with email existed
    3. Test with mismatching passwords 
    4. Test that passwords that are too short are rejected
    5. Test that passwords that are too common are rejected
    6. Test that passwords too similar to the email are rejected
    7. Test that numeric-only passwords are rejected

    Management
    1. Test for resending activation email
    2. Test for successfully activating account by email sent after registration
    4. Test for reset password when user forgot. An email will be sent
    5. Test for creating new password and confirming

"""


import pytest
from tests.factories import UserFactory
import logging
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from djoser.utils import encode_uid
from django.contrib.auth.tokens import default_token_generator
from django.core import mail

logger = logging.getLogger(__name__)
User = get_user_model()

@pytest.mark.django_db
class TestUserRegistrationAPI:
    url = "/auth/users/"

    def test_register_user(self, api_client):
        """ Test success user registration """

        user = UserFactory.build(password="defaultpassword")

        payload = {
            "email": user.email,
            "password": user.password,
            "re_password": user.password
        }

        response = api_client.post(self.url, payload, format='json')

        # Check that register was successfull
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email=payload["email"]).exists()


        try:
            # Try to fetch the user from the database
            registered_user = User.objects.get(email=payload["email"])
            
            # Log and check the user's status
            logger.warning(f"User is now {registered_user.is_active}")
            
            # Assert that the user is not active yet (if activation is required)
            # assert registered_user.is_active is False

            # Check activation email sent
            # assert len(mail.outbox) == 1 

        except ObjectDoesNotExist:
            pytest.fail(f"User with email {payload['email']} was not found in the database.")
    
    def test_register_user_existed(self, api_client):
        """ Test with email existed"""
        user = UserFactory()

        payload = {
            "email": user.email,
            "password": user.password,
            "re_password": user.password
        }

        response = api_client.post(self.url, payload, format='json')  
        assert response.status_code == status.HTTP_400_BAD_REQUEST 
        assert 'email' in response.data
        assert "user with this email address already exists." in response.data["email"]

    
    def test_register_user_password_mismatch(self, api_client):
        """ Test with mismatching passwords """

        user = UserFactory.build()

        payload = {
            "email": user.email,
            "password": "defaultpassword",
            "re_password": "differentpassword"
        }

        response = api_client.post(self.url, payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST 

        assert 'non_field_errors' in response.data
        assert "The two password fields didn't match." in response.data['non_field_errors']

    def test_password_too_short(self, api_client):
        """Test that passwords that are too short are rejected"""
        
        user = UserFactory.build()

        payload = {
            "email": user.email,
            "password": "a",
            "re_password": "a"
        }

        response = api_client.post(self.url, payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST 
        assert 'password' in response.data
        assert "This password is too short. It must contain at least 8 characters." in response.data["password"]


    def test_password_too_comnmon(self, api_client):
        """Test that passwords that are too common are rejected"""
        
        user = UserFactory.build()
    
        payload = {
            "email": user.email,
            "password": "password",
            "re_password": "password"
        }

        response = api_client.post(self.url, payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST 
        assert 'password' in response.data
        assert "This password is too common." in response.data["password"]
       
    def test_password_too_similar(self, api_client):
        """Test that passwords too similar to the email are rejected"""
        user = UserFactory.build(email="user@gmail.com")
    
        payload = {
            "email": user.email,
            "password": "user",
            "re_password": "user"
        }

        response = api_client.post(self.url, payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST 
        assert 'password' in response.data
        assert "The password is too similar to the email address." in response.data['password']

    def test_numeric_password(self, api_client):
        """Test that numeric-only passwords are rejected"""
        user = UserFactory.build()
    
        payload = {
            "email": user.email,
            "password": "123",
            "re_password": "123"
        }

        response = api_client.post(self.url, payload, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST 
        assert 'password' in response.data
        assert "This password is entirely numeric." in response.data['password']


@pytest.mark.django_db
class TestUserManagementAPI:

    @pytest.fixture(autouse=True)
    def setup(self):
        """Automatically set up user for each test"""
        self.user = UserFactory(
            email="testuser@example.com",
            password="defaultpassword",
            is_active=False 
        )    

    # def test_resend_activation_email(self, api_client):
    #     """ Test for resending activation email"""
    #     url = "/auth/users/resend_activation/"
    #     payload = {
    #         "email": self.user.email
    #     }
    #     response = api_client.post(url, payload, format="json")

    #     assert response.status_code == status.HTTP_204_NO_CONTENT

    #     # Verify that an email was sent
    #     assert len(mail.outbox) == 1 # One mail sent
        
    #     # Check email content
    #     assert "activate account" in mail.outbox[0].body.lower()

    # def test_user_activation(self, api_client):
    #     """ Test for activating account by email sent after registration"""
    #     # Generate activation token and uid
    #     uid = encode_uid(self.user.id)
    #     token = default_token_generator.make_token(self.user)
    #     payload = {
    #         "uid": uid,
    #         "token": token
    #     }

    #     url = "/auth/users/activation/"

    #     response = api_client.post(url, payload, format="json")

    #     assert response.status_code == status.HTTP_204_NO_CONTENT or response.status_code == status.HTTP_200_OK

    #     self.user.refresh_from_db()
    #     assert self.user.is_active is True

    def test_reset_password(self, api_client):
        """Test for reset password when user forgot. An email will be sent"""
        # Account is activated
        self.user.is_active = True
        self.user.save()

        url = "/auth/users/reset_password/"
        payload = {
            "email": self.user.email
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert len(mail.outbox) == 1
        assert "password reset" in mail.outbox[0].body.lower()
    
    def test_reset_password_confirm(self, api_client):
        """Test for creating new password and confirming"""

        # Account is activated
        self.user.is_active = True
        self.user.save()

        url = "/auth/users/reset_password_confirm/"
        
        
        uid = encode_uid(self.user.id)
        token = default_token_generator.make_token(self.user)

        payload = {
            "uid": uid,
            "token": token,
            "new_password": "newpassword123",
            "re_new_password": "newpassword123"
        }

        response = api_client.post(url, payload, format="json")

        #Verify that the old password no longer works
        old_password_login_response = api_client.post('/auth/token/', {
            'email': self.user.email,
            'password': 'defaultpassword'
        }, format='json')

        assert old_password_login_response.status_code == status.HTTP_401_UNAUTHORIZED

        #Verify that the new password works
        new_password_login_response = api_client.post('/auth/token/', {
            'email': self.user.email,
            'password': "newpassword123"
        }, format='json')

        assert new_password_login_response.status_code == status.HTTP_200_OK      

    def test_success_change_password(self, api_client):
        # Account is activated
        self.user.is_active = True
        self.user.save()

        #  Log in the user to obtain JWT tokens
        login_url = '/auth/token/'
        login_data = {
            'email': self.user.email,
            'password': 'defaultpassword'
        }
        login_response = api_client.post(login_url, login_data, format='json')

        assert login_response.status_code == status.HTTP_200_OK
        assert 'access' in login_response.data
        access_token = login_response.data['access']

        # Set the Authorization header with the access token
        api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

        # Send a request to change the password
        change_password_url = '/auth/users/set_password/'
        change_password_data = {
            'current_password': 'defaultpassword',
            'new_password': 'newpassword456',
            're_new_password': 'newpassword456'
        }
        change_password_response = api_client.post(change_password_url, change_password_data, format='json')

        assert change_password_response.status_code == status.HTTP_204_NO_CONTENT

        # Attempt to log in with the old password (fail)
        api_client.credentials()  # Remove existing credentials

        old_password_login_response = api_client.post(login_url, login_data, format='json')
        assert old_password_login_response.status_code == status.HTTP_401_UNAUTHORIZED

        # Attempt to log in with the new password (succeed)
        new_password_login_data = {
            'email': self.user.email,
            'password': 'newpassword456'
        }
        new_password_login_response = api_client.post(login_url, new_password_login_data, format='json')
        assert new_password_login_response.status_code == status.HTTP_200_OK
        assert 'access' in new_password_login_response.data           


"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""