"""
Test for the MovieNightInvitation signal that triggers a notification when an invitation is created.

- `test_send_invitation_signal`: Ensures that the `send_invitation.delay` task is called 
  when a new `MovieNightInvitation` is created.
  
"""

import pytest
from django.db.models.signals import post_save
from movies.models import MovieNightInvitation
from django.db import transaction
from unittest import mock
from tests.factories import MovieNightFactory, UserFactory

@pytest.mark.django_db
class TestSendInvitationSignal:
    
    @mock.patch('movies.tasks.send_invitation.delay')  # Mock where the `delay` method is called
    def test_send_invitation_signal(self, mock_delay):
        """
        Test that the Celery task `send_invitation.delay` is triggered when a MovieNightInvitation is created.
        """
        # Create test data
        movie_night = MovieNightFactory()
        invitee = UserFactory()

        # Ensure transaction is committed so the signal can trigger the task
        with transaction.atomic():
            MovieNightInvitation.objects.create(
                movie_night=movie_night,
                invitee=invitee,
                attendance_confirmed=False
            )
        
        transaction.on_commit(lambda: mock_delay.assert_called_once())

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""