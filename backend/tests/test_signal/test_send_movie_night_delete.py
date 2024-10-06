import pytest
from django.db.models.signals import pre_delete
from tests.factories import MovieNightFactory
from unittest import mock

@pytest.mark.django_db
class TestSendMovieNightDeleteSignal:
    @mock.patch('movies.tasks.send_movie_night_delete.delay') 
    def test_send_movie_night_delete_signal(self, mock_task):
        """
        Test that `send_movie_night_delete.delay` is called when a MovieNight is deleted.
        """
        # Create a MovieNight
        movie_night = MovieNightFactory()
        movie_night_pk = movie_night.pk

        # Delete the MovieNight, which should trigger the signal
        movie_night.delete()

        # Assert that the task was triggered with the correct argument
        mock_task.assert_called_once_with(movie_night_pk)

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""