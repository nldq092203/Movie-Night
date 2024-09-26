"""
Notification functions for MovieNight application.

This module provides functions to send various email notifications for movie night events,
such as invitations, attendance changes, movie night updates, and notifications for when 
a movie night is starting soon. The emails are templated using Django's template system 
and sent via the configured email backend.

Functions:
- `send_invitation`: Sends an invitation email to an invitee for a specific movie night.
- `send_attendance_change`: Notifies the creator when an invitee's attendance status changes.
- `send_starting_notification`: Notifies the invitees and creator that the movie night is starting soon.
- `notify_of_starting_soon`: Finds movie nights starting within 30 minutes and sends notifications.
- `send_movie_night_update`: Notifies invitees when a movie night start time has been updated.

"""

from datetime import timedelta
from urllib.parse import urljoin
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from movies.models import MovieNight

def send_invitation(movie_night_invitation):
    """
    Send an invitation email to the invitee for a movie night.

    Args:
    - movie_night_invitation: The MovieNightInvitation object containing the movie night 
      and the invitee information.

    The email contains a link to view the movie night details and is sent to the invitee.
    """
    subject = render_to_string(
        "movies/notifications/invitation_subject.txt",
        {"movie_night": movie_night_invitation.movie_night},
    )

    movie_night_path = reverse(
        "movienight_detail", args=(movie_night_invitation.movie_night.pk,)
    )

    body = render_to_string(
        "movies/notifications/invitation_body.txt",
        {
            "creator": movie_night_invitation.movie_night.creator,
            "movie_night": movie_night_invitation.movie_night,
            "movie_night_url": urljoin(settings.BASE_URL, movie_night_path),
        },
    )

    send_mail(
        subject,
        body,
        None,
        [movie_night_invitation.invitee.email],
    )


def send_attendance_change(movie_night_invitation, is_attending):
    """
    Notify the creator when an invitee updates their attendance status for a movie night.

    Args:
    - movie_night_invitation: The MovieNightInvitation object.
    - is_attending: Boolean indicating if the invitee will attend.

    The creator receives an email notification about the invitee's attendance status update.
    """
    subject = render_to_string(
        "movies/notifications/attendance_update_subject.txt",
        {
            "movie_night": movie_night_invitation.movie_night,
            "movie_night_invitation": movie_night_invitation,
        },
    )

    movie_night_path = reverse(
        "movienight_detail", args=(movie_night_invitation.movie_night.pk,)
    )

    body = render_to_string(
        "movies/notifications/attendance_update_body.txt",
        {
            "is_attending": is_attending,
            "movie_night_invitation": movie_night_invitation,
            "movie_night": movie_night_invitation.movie_night,
            "movie_night_url": urljoin(settings.BASE_URL, movie_night_path),
        },
    )

    send_mail(
        subject,
        body,
        None,
        [movie_night_invitation.movie_night.creator.email],
    )


def send_starting_notification(movie_night):
    """
    Notify invitees and the creator that the movie night is starting soon.

    Args:
    - movie_night: The MovieNight object.

    This function sends an email to all confirmed invitees and the creator when a movie
    night is starting soon (typically 30 minutes before the event).
    """

    subject = render_to_string(
        "movies/notifications/starting_subject.txt",
        {"movie_night": movie_night},
    )

    movie_night_path = reverse("movienight_detail", args=(movie_night.pk,))

    body = render_to_string(
        "movies/notifications/starting_body.txt",
        {
            "movie_night": movie_night,
            "movie_night_url": urljoin(settings.BASE_URL, movie_night_path),
        },
    )

    to_emails = [
        invite.invitee.email for invite in movie_night.invites.filter(is_attending=True)
    ]
    to_emails.append(movie_night.creator.email)

    send_mail(
        subject,
        body,
        None,
        to_emails,
    )
    movie_night.start_notification_sent = True
    movie_night.save()


def notify_of_starting_soon():
    """
    Send notifications for movie nights starting within the next 30 minutes.

    This function finds all movie nights that are about to start but have not yet
    sent a notification, and sends a starting notification to the invitees and the creator.
    """
    start_before = timezone.now() + timedelta(minutes=30)

    movie_nights = MovieNight.objects.filter(
        start_time__lte=start_before, start_notification_sent=False
    )

    for movie_night in movie_nights:
        send_starting_notification(movie_night)


def send_movie_night_update(movie_night, start_time):
    """
    Notify invitees when the movie night start time is updated.

    Args:
    - movie_night: The MovieNight object.
    - start_time: The updated start time of the movie night.

    This function sends an email to all confirmed invitees to inform them about
    the new start time of the movie night.
    """
    subject = render_to_string(
        "movies/notifications/movie_night_update_subject.txt",
        {
            "movie_night": movie_night,
        },
    )

    movie_night_path = reverse(
        "movienight_detail", args=(movie_night.pk,)
    )

    body = render_to_string(
        "movies/notifications/attendance_update_body.txt",
        {
            "start_time": start_time,
            "movie_night": movie_night,
            "movie_night_url": urljoin(settings.BASE_URL, movie_night_path),
        },
    )

    to_emails = [
        invite.invitee.email for invite in movie_night.invites.filter(is_attending=True)
    ]

    send_mail(
        subject,
        body,
        None,
        to_emails,
    )

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""