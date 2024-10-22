import pytest
from rest_framework.serializers import ValidationError
from movienight_profile.serializers import UserProfileSerializer  # Adjust to the correct path
from tests.factories import UserFactory, UserProfileFactory  # Assuming you have a UserFactory and UserProfileFactory

@pytest.mark.django_db
class TestUserProfileSerializer:
    """Test suite for the UserProfileSerializer."""

    def test_valid_data(self):
        """Test the serializer with valid data where gender is not 'Custom'."""
        user = UserFactory(email='testuser@example.com')
        profile_data = {
            'user': user.email,
            'name': 'Test User',
            'bio': 'This is a bio',
            'gender': 'Male',
            'custom_gender': '',
        }

        serializer = UserProfileSerializer(data=profile_data)
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data['gender'] == 'Male'
        assert serializer.validated_data['custom_gender'] == ''

    def test_valid_custom_gender(self):
        """Test the serializer with valid data where gender is 'Custom'."""
        user = UserFactory(email='customuser@example.com')
        profile_data = {
            'user': user.email,
            'name': 'Custom User',
            'bio': 'This is a custom bio',
            'gender': 'Custom',
            'custom_gender': 'Non-binary',
        }

        serializer = UserProfileSerializer(data=profile_data)
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data['gender'] == 'Custom'
        assert serializer.validated_data['custom_gender'] == 'Non-binary'

    def test_invalid_custom_gender_missing(self):
        """Test validation error when gender is 'Custom' but custom_gender is not provided."""
        user = UserFactory(email='invaliduser@example.com')
        profile_data = {
            'user': user.email,
            'name': 'Invalid User',
            'bio': 'This is an invalid bio',
            'gender': 'Custom',
            'custom_gender': '',
        }

        serializer = UserProfileSerializer(data=profile_data)
        assert not serializer.is_valid()
        assert 'custom_gender' in serializer.errors
        assert serializer.errors['custom_gender'][0] == 'Please provide a custom gender when selecting "Custom".'

    def test_invalid_custom_gender_provided_for_non_custom_gender(self):
        """Test validation error when custom_gender is provided but gender is not 'Custom'."""
        user = UserFactory(email='invaliduser@example.com')
        profile_data = {
            'user': user.email,
            'name': 'Invalid User',
            'bio': 'This is an invalid bio',
            'gender': 'Male',
            'custom_gender': 'Non-binary',
        }

        serializer = UserProfileSerializer(data=profile_data)
        assert not serializer.is_valid()
        assert 'custom_gender' in serializer.errors
        assert serializer.errors['custom_gender'][0] == 'Custom gender should be empty unless you select "Custom" as gender.'