"""
Test cases for UseProfile model
"""

import pytest
from django.contrib.auth import get_user_model
from movies.models import UserProfile
from tests.factories import UserProfileFactory, UserFactory

UserModel = get_user_model()

@pytest.mark.django_db
def test_userprofile_creation():
    user = UserFactory()
    profile = UserProfileFactory.create(user=user, bio='This is a test bio.')

    assert profile.user == user
    assert profile.bio == 'This is a test bio.'
    assert str(profile) == f"UserProfile object for {user}"


"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""