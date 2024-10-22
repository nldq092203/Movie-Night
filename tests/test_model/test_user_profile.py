"""
Test cases for UseProfile model
"""

# test_user_profile.py

import pytest
from tests.factories import UserProfileFactory, UserFactory
from movienight_profile.models import UserProfile 

@pytest.mark.django_db
class TestUserProfile:
    """Test suite for the UserProfile model."""

    def test_user_profile_creation(self):
        """Test that a UserProfile can be created and is associated with a user."""
        user_profile = UserProfileFactory()

        assert user_profile.id is not None
        assert user_profile.user is not None
        assert isinstance(user_profile.user, UserFactory._meta.model)
        assert isinstance(user_profile, UserProfile)
        assert user_profile.name is not None
        assert user_profile.bio is not None

    # def test_custom_gender_field(self):
    #     """Test that custom gender field is only set if gender is 'Custom'."""
    #     # Create a UserProfile with gender 'Custom'
    #     user_profile = UserProfileFactory(gender='Custom')
    #     assert user_profile.custom_gender is not None

    #     # Create a UserProfile with gender 'Male'
    #     user_profile_male = UserProfileFactory(gender='Male')
        
    #     # Assert that custom_gender is empty for non-Custom genders
    #     assert user_profile_male.custom_gender == '' or user_profile_male.custom_gender is None
        
    def test_user_profile_related_to_user(self, user):
        """Test that a user has a related UserProfile."""
        user_profile = UserProfileFactory(user=user)

        assert user_profile.user == user
        assert hasattr(user, 'profile')  # Checks the reverse relationship
        assert user.profile == user_profile
"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""