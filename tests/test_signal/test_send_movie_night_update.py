"""
Test for the MovieNight signal that triggers a notification when a movie night start time is updated.

- `test_send_movie_night_update_signal`: Ensures that the `send_movie_night_update.delay` 
  task is called when a `MovieNight` instance's start time is modified.

"""
import pytest
from movies.models import MovieNight
from unittest import mock
from django.utils import timezone
from tests.factories import MovieFactory


@pytest.mark.django_db
def test_send_movie_night_update_signal(mocker, user):
    """
    Test that `send_movie_night_update.delay` is called when the MovieNight start time is changed.
    """
    # Mock the task function
    mock_task = mocker.patch("movies.tasks.send_movie_night_update.delay")

    # Create a MovieNight
    movie_night = MovieNight.objects.create(
        movie = MovieFactory(),
        start_time=timezone.now(),
        creator=user
    )

    # Change the start time
    new_time = timezone.now() + timezone.timedelta(days=1)
    movie_night.start_time = new_time
    movie_night.save()

    # Assert that the task was triggered with the correct arguments
    mock_task.assert_called_once_with(movie_night.pk, new_time)

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""