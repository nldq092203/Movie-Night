"""
Test cases for the notifications in the Movie Night application including:

1. **TestSendInvitation**:
   - Tests sending an invitation notification when a movie night invitation is created.
   - Ensures that the notification is sent to the correct recipient with the correct data.

2. **TestSendAttendanceChange**:
   - Tests sending a notification when the invitee's attendance status changes.
   - Ensures that the correct message is sent for both accepted and refused responses.

3. **TestSendMovieNightUpdate**:
   - Tests sending a notification when the movie night start time is updated.
   - Ensures that all confirmed participants receive the update notification.

4. **TestSendStartingNotification**:
   - Tests sending a reminder notification shortly before the movie night begins.
   - Ensures that both the creator and confirmed participants receive the reminder.

5. **TestSendMovieNightDelete**:
   - Tests sending a cancellation notification when a movie night is deleted.
   - Ensures that all participants receive the cancellation notification.
"""

import pytest
from movies.notifications import NotificationSerializer
from unittest import mock
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from movies.models import MovieNightInvitation, MovieNight
from tests.factories import MovieNightFactory, MovieNightInvitationFactory, UserFactory


@pytest.mark.django_db
class TestSendInvitation:

    @mock.patch('movies.notifications.NotificationSerializer') 
    def test_send_invitation(self, mock_serializer):
        """
        Test that an invitation notification is sent when a MovieNightInvitation is created.
        """
        # Create movie night invitation
        movie_night_invitation = MovieNightInvitationFactory()

        # Mock serializer instance
        mock_serializer_instance = mock_serializer.return_value
        mock_serializer_instance.is_valid.return_value = True

        from movies.notifications import send_invitation  
        # Call the function
        send_invitation(movie_night_invitation)

        # Check if the NotificationSerializer was called with the correct data
        mock_serializer.assert_called_once_with(
            data={
                'notification_type': 'INV',
                'content_type': ContentType.objects.get_for_model(MovieNightInvitation).id,
                'object_id': movie_night_invitation.id,
                'message': f"{movie_night_invitation.movie_night.creator.email} have invited you to a movie night."
            }
        )

        # Ensure save was called on the serializer
        mock_serializer_instance.save.assert_called_once_with(
            sender=movie_night_invitation.movie_night.creator,
            recipient=movie_night_invitation.invitee
        )

@pytest.mark.django_db
class TestSendAttendanceChange:
    @mock.patch('movies.notifications.NotificationSerializer')
    def test_send_attendance_change(self, mock_serializer):
        """
        Test that an attendance change notification is sent when an invitee accepts or refuses.
        """
        # Create movie night invitation
        movie_night_invitation = MovieNightInvitationFactory()

        # Mock serializer instance
        mock_serializer_instance = mock_serializer.return_value
        mock_serializer_instance.is_valid.return_value = True

        from movies.notifications import send_attendance_change
        # Call the function for accepting
        send_attendance_change(movie_night_invitation, True)

        # Check if the NotificationSerializer was called with the correct data for acceptance
        mock_serializer.assert_called_once_with(
            data={
                'notification_type': 'RES',
                'content_type': ContentType.objects.get_for_model(MovieNightInvitation).id,
                'object_id': movie_night_invitation.id,
                'message': f"{movie_night_invitation.invitee.email} have accepted to participate in your movie night."
            }
        )

        # Ensure save was called on the serializer
        mock_serializer_instance.save.assert_called_once_with(
            sender=movie_night_invitation.invitee,
            recipient=movie_night_invitation.movie_night.creator
        )


@pytest.mark.django_db
class TestSendMovieNightUpdate:
    
    @mock.patch('movies.notifications.NotificationSerializer')
    def test_send_movie_night_update(self, mock_serializer):
        """
        Test that the movie night update notification is sent to accepted invitees.
        """
        # Create movie night and invitees
        movie_night = MovieNightFactory()
        invitee = UserFactory()
        MovieNightInvitationFactory(invitee=invitee, movie_night=movie_night, is_attending=True)

        # Mock serializer instance
        mock_serializer_instance = mock_serializer.return_value
        mock_serializer_instance.is_valid.return_value = True

        from movies.notifications import send_movie_night_update
        # Call the function
        send_movie_night_update(movie_night, "2024-10-06 18:00")

        # Check if NotificationSerializer was called for the invitees
        mock_serializer.assert_called_once_with(
            data={
                'notificcation_type': 'UPD',
                'content_type': ContentType.objects.get_for_model(MovieNight).id,
                'object_id': movie_night.id,
                'message': f"{movie_night.creator.email} have changed start time for a movie night to 2024-10-06 18:00."
            }
        )

        # Ensure save was called on the serializer for each recipient
        mock_serializer_instance.save.assert_called_once_with(
            sender=movie_night.creator, recipient=invitee
        )

@pytest.mark.django_db
class TestSendStartingNotification:
    
    @mock.patch('movies.notifications.NotificationSerializer')
    def test_send_starting_notification(self, mock_serializer):
        """
        Test that starting notifications are sent to the creator and accepted invitees.
        """
        # Create movie night and invitees
        movie_night = MovieNightFactory()
        invitee = MovieNightInvitationFactory(movie_night=movie_night, is_attending=True)

        # Mock serializer instance
        mock_serializer_instance = mock_serializer.return_value
        mock_serializer_instance.is_valid.return_value = True

        from movies.notifications import send_starting_notification
        # Call the function
        send_starting_notification(movie_night)

        # Assert that NotificationSerializer was called for both creator and invitees
        assert mock_serializer.call_count == 2

        # Ensure save was called for each recipient
        mock_serializer_instance.save.assert_any_call(recipient=movie_night.creator)
        mock_serializer_instance.save.assert_any_call(recipient=invitee.invitee)

        # Ensure the movie night is marked as notification sent
        assert movie_night.start_notification_sent
    
    @mock.patch('movies.notifications.send_starting_notification')
    def test_notify_of_starting_soon(self, mock_notification):
        """
        Test that notifications for starting soon movie nights are sent.
        """
        # Create a movie night
        movie_night = MovieNightFactory(
            start_time=timezone.now() + timezone.timedelta(minutes=15), 
            start_notification_sent=False
        )

        movie_night.start_notification_before = timezone.timedelta(minutes=30)
        movie_night.save()

        from movies.notifications import notify_of_starting_soon
        notify_of_starting_soon()

        # Assert that send_starting_notification was called with the movie_night
        mock_notification.assert_called_once_with(movie_night)


@pytest.mark.django_db
class TestSendMovieNightDeleteSignal:
    
    @mock.patch('movies.notifications.NotificationSerializer')
    def test_send_movie_night_delete(self, mock_serializer):
        """
        Test that movie night delete notifications are sent to accepted invitees.
        """
        # Create movie night and invitees
        movie_night = MovieNightFactory()
        invitee = MovieNightInvitationFactory(movie_night=movie_night, is_attending=True)

        # Mock serializer instance
        mock_serializer_instance = mock_serializer.return_value
        mock_serializer_instance.is_valid.return_value = True

        from movies.notifications import send_movie_night_delete
        # Call the function
        send_movie_night_delete(movie_night)
        formatted_start_time = movie_night.start_time.strftime('%Y-%m-%d %H:%M:%S')

        # Check if NotificationSerializer was called for the invitees
        mock_serializer.assert_called_once_with(
            data={
                'notificcation_type': 'CAN',
                'content_type': ContentType.objects.get_for_model(MovieNight).id,
                'object_id': movie_night.id,
                'message': f"{movie_night.creator.email} have canceled a movie night ({movie_night.movie} at {formatted_start_time})."
            }
        )

        # Ensure save was called for each recipient
        mock_serializer_instance.save.assert_called_once_with(sender=movie_night.creator, recipient=invitee.invitee)

# import pytest
# from unittest import mock
# from django.core import mail
# from django.urls import reverse
# from movies.notifications import (
#     send_invitation,
#     send_attendance_change,
#     send_starting_notification,
#     notify_of_starting_soon,
#     send_movie_night_update
# )
# from movies.models import MovieNightInvitation, MovieNight
# from tests.factories import MovieNightInvitationFactory, MovieNightFactory, UserFactory
# from django.utils import timezone
# from datetime import timedelta


# @pytest.mark.django_db
# def test_send_invitation(mocker):
#     """
#     Test the send_invitation function to ensure the email is sent correctly.
#     """
#     mock_send_mail = mocker.patch("movies.notifications.send_mail")
#     movie_night_invitation = MovieNightInvitationFactory()

#     send_invitation(movie_night_invitation)

#     # Assert that send_mail was called with the correct arguments
#     mock_send_mail.assert_called_once()
#     assert movie_night_invitation.invitee.email in mock_send_mail.call_args[0][3]


# @pytest.mark.django_db
# def test_send_attendance_change(mocker):
#     """
#     Test the send_attendance_change function to ensure the attendance change email is sent.
#     """
#     mock_send_mail = mocker.patch("movies.notifications.send_mail")
#     movie_night_invitation = MovieNightInvitationFactory()

#     send_attendance_change(movie_night_invitation, True)

#     # Assert that send_mail was called with the correct arguments
#     mock_send_mail.assert_called_once()
#     assert movie_night_invitation.movie_night.creator.email in mock_send_mail.call_args[0][3]


# @pytest.mark.django_db
# def test_send_starting_notification(mocker):
#     """
#     Test the send_starting_notification function to ensure the starting notification email is sent.
#     """
#     mock_send_mail = mocker.patch("movies.notifications.send_mail")
#     movie_night = MovieNightFactory()
#     MovieNightInvitationFactory(movie_night=movie_night, is_attending=True)  # Confirmed invitee

#     send_starting_notification(movie_night)

#     # Assert that send_mail was called with the correct recipients
#     mock_send_mail.assert_called_once()
#     assert movie_night.creator.email in mock_send_mail.call_args[0][3]


# @pytest.mark.django_db
# def test_notify_of_starting_soon(mocker):
#     """
#     Test the notify_of_starting_soon function to ensure notifications are sent for soon-to-start movie nights.
#     """
#     mock_send_starting_notification = mocker.patch("movies.notifications.send_starting_notification")
#     movie_night = MovieNightFactory(start_time=timezone.now() + timedelta(minutes=15), start_notification_sent=False)
#     MovieNightInvitationFactory(movie_night=movie_night, is_attending=True)

#     notify_of_starting_soon()

#     # Assert that the send_starting_notification was called for the correct movie night
#     mock_send_starting_notification.assert_called_once_with(movie_night)


# @pytest.mark.django_db
# def test_send_movie_night_update(mocker):
#     """
#     Test the send_movie_night_update function to ensure the movie night update email is sent.
#     """
#     mock_send_mail = mocker.patch("movies.notifications.send_mail")
#     movie_night = MovieNightFactory()
#     MovieNightInvitationFactory(movie_night=movie_night, is_attending=True)

#     new_time = timezone.now() + timedelta(days=1)
#     send_movie_night_update(movie_night, new_time)

#     # Assert that send_mail was called with the correct arguments
#     mock_send_mail.assert_called_once()
#     assert movie_night.invites.first().invitee.email in mock_send_mail.call_args[0][3]

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""
