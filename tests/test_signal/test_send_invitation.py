"""
Test for the MovieNightInvitation signal that triggers a notification when an invitation is created.

- `test_send_invitation_signal`: Ensures that the `send_invitation.delay` task is called 
  when a new `MovieNightInvitation` is created.
  
"""

import pytest
from django.db.models.signals import post_save
from movies.models import MovieNightInvitation
from unittest import mock
from tests.factories import MovieNightFactory, UserFactory

@pytest.mark.django_db
def test_send_invitation_signal(mocker):
    """
    Test that `send_invitation.delay` is called when a new MovieNightInvitation is created.
    """
    # Mock the task function
    mock_task = mocker.patch("movies.tasks.send_invitation.delay")
    movie_night = MovieNightFactory()
    invitee = UserFactory()

    # Create a new MovieNightInvitation
    invitation = MovieNightInvitation.objects.create(
        invitee=invitee, movie_night=movie_night
    )

    # Assert that the task was triggered
    mock_task.assert_called_once_with(invitation.pk)

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""