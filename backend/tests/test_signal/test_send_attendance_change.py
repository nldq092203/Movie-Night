"""
Tests for the MovieNightInvitation signals that handle sending notifications when the 
attendance status of an invitation is changed. 

- `test_send_attendance_change_signal_create`: Ensures that the `send_attendance_change.delay` 
  task is **not** triggered when a new `MovieNightInvitation` is created.
  
- `test_send_attendance_change_signal_update`: Ensures that the `send_attendance_change.delay` 
  task **is** triggered when an existing `MovieNightInvitation` is updated and the 
  `is_attending` field is changed.
"""
import pytest
from movies.models import MovieNightInvitation
from unittest import mock
from tests.factories import MovieNightFactory

@pytest.mark.django_db
class TestSendAttendanceChange:

    def test_send_attendance_change_signal_create(self, mocker, user):
        """
        Test that `send_attendance_change.delay` is not called when MovieNightInvitation creates.
        """
        # Mock the task function
        mock_task = mocker.patch("movies.tasks.send_attendance_change.delay")
        movie_night = MovieNightFactory()

        # Create a MovieNightInvitation (the signal shouldn't be triggered on creation)
        invitation = MovieNightInvitation.objects.create(
            invitee=user, movie_night=movie_night, is_attending=False
        )
        # Assert that the task was NOT called on creation
        mock_task.assert_not_called()

    def test_send_attendance_change_signal_update(self, mocker, user):
        """
        Test that `send_attendance_change.delay` is called when MovieNightInvitation update attendance.
        """
        # Mock the task function
        mock_task = mocker.patch("movies.tasks.send_attendance_change.delay")

        # Create a MovieNightInvitation (the signal shouldn't be triggered on creation)
        invitation = MovieNightInvitation.objects.create(
            invitee=user, movie_night=MovieNightFactory(), is_attending=False
        )
        # Update the invitation's attendance
        invitation.is_attending = True
        invitation.save()

        # Assert that the task was triggered with the correct arguments
        mock_task.assert_called_once_with(invitation.pk, True)            

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""