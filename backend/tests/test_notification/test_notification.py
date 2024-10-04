import pytest
from unittest import mock
from django.core import mail
from django.urls import reverse
from movies.notifications import (
    send_invitation,
    send_attendance_change,
    send_starting_notification,
    notify_of_starting_soon,
    send_movie_night_update
)
from movies.models import MovieNightInvitation, MovieNight
from tests.factories import MovieNightInvitationFactory, MovieNightFactory, UserFactory
from django.utils import timezone
from datetime import timedelta


@pytest.mark.django_db
def test_send_invitation(mocker):
    """
    Test the send_invitation function to ensure the email is sent correctly.
    """
    mock_send_mail = mocker.patch("movies.notifications.send_mail")
    movie_night_invitation = MovieNightInvitationFactory()

    send_invitation(movie_night_invitation)

    # Assert that send_mail was called with the correct arguments
    mock_send_mail.assert_called_once()
    assert movie_night_invitation.invitee.email in mock_send_mail.call_args[0][3]


@pytest.mark.django_db
def test_send_attendance_change(mocker):
    """
    Test the send_attendance_change function to ensure the attendance change email is sent.
    """
    mock_send_mail = mocker.patch("movies.notifications.send_mail")
    movie_night_invitation = MovieNightInvitationFactory()

    send_attendance_change(movie_night_invitation, True)

    # Assert that send_mail was called with the correct arguments
    mock_send_mail.assert_called_once()
    assert movie_night_invitation.movie_night.creator.email in mock_send_mail.call_args[0][3]


@pytest.mark.django_db
def test_send_starting_notification(mocker):
    """
    Test the send_starting_notification function to ensure the starting notification email is sent.
    """
    mock_send_mail = mocker.patch("movies.notifications.send_mail")
    movie_night = MovieNightFactory()
    MovieNightInvitationFactory(movie_night=movie_night, is_attending=True)  # Confirmed invitee

    send_starting_notification(movie_night)

    # Assert that send_mail was called with the correct recipients
    mock_send_mail.assert_called_once()
    assert movie_night.creator.email in mock_send_mail.call_args[0][3]


@pytest.mark.django_db
def test_notify_of_starting_soon(mocker):
    """
    Test the notify_of_starting_soon function to ensure notifications are sent for soon-to-start movie nights.
    """
    mock_send_starting_notification = mocker.patch("movies.notifications.send_starting_notification")
    movie_night = MovieNightFactory(start_time=timezone.now() + timedelta(minutes=15), start_notification_sent=False)
    MovieNightInvitationFactory(movie_night=movie_night, is_attending=True)

    notify_of_starting_soon()

    # Assert that the send_starting_notification was called for the correct movie night
    mock_send_starting_notification.assert_called_once_with(movie_night)


@pytest.mark.django_db
def test_send_movie_night_update(mocker):
    """
    Test the send_movie_night_update function to ensure the movie night update email is sent.
    """
    mock_send_mail = mocker.patch("movies.notifications.send_mail")
    movie_night = MovieNightFactory()
    MovieNightInvitationFactory(movie_night=movie_night, is_attending=True)

    new_time = timezone.now() + timedelta(days=1)
    send_movie_night_update(movie_night, new_time)

    # Assert that send_mail was called with the correct arguments
    mock_send_mail.assert_called_once()
    assert movie_night.invites.first().invitee.email in mock_send_mail.call_args[0][3]

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""