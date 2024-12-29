
"""
This module handles notifications for various movie night events such as invitations, attendance changes, 
movie night updates, reminders, and cancellations. It uses Django's content types framework and Celery tasks 
to send asynchronous notifications to users.
"""

from apps.notifications.serializers import NotificationSerializer
from django.contrib.contenttypes.models import ContentType
from apps.movies.models import MovieNightInvitation, MovieNight
from django.contrib.auth import get_user_model
import logging
from django.utils import timezone
from django.db.models import F

logger = logging.getLogger(__name__)

User = get_user_model()


def send_invitation(movie_night_invitation):
    """
    Sends an invitation notification to the invitee of the movie night.
    
    Args:
        movie_night_invitation (MovieNightInvitation): The movie night invitation instance.
    
    The function retrieves the sender (movie night creator) and recipient (invitee), and then 
    sends a notification indicating that the recipient has been invited to the movie night.
    """
    try:
        sender = User.objects.get(email=movie_night_invitation.movie_night.creator.email)
    except User.DoesNotExist:
        logger.error("Sender does not exist") 
        return
    try:
        recipient = User.objects.get(email=movie_night_invitation.invitee.email)
    except User.DoesNotExist:
        logger.error("Recipient does not exist")
        return
    serializer = NotificationSerializer(
        data={
            'notification_type': 'INV',
            'content_type': ContentType.objects.get_for_model(MovieNightInvitation).id,
            'object_id': movie_night_invitation.id,
            'message': f"{sender.email} have invited you to a movie night."
        }
    )
    if serializer.is_valid():
        serializer.save(sender=sender, recipient=recipient)
    else:
        logger.error(f"Notification serialization error: {serializer.errors}")    


def send_attendance_change(movie_night_invitation, is_attending):
    """
    Sends a notification when an invitee accepts or refuses a movie night invitation.
    
    Args:
        movie_night_invitation (MovieNightInvitation): The movie night invitation instance.
        is_attending (bool): A boolean indicating whether the invitee is attending the movie night.
    
    The function notifies the movie night creator about the invitee's response (accepted or refused).
    """
    try:
        sender = User.objects.get(email=movie_night_invitation.invitee.email)
    except User.DoesNotExist:
        logger.error("Sender does not exist")
        return
    try:
        recipient = User.objects.get(email=movie_night_invitation.movie_night.creator.email)
    except User.DoesNotExist:
        logger.error("Recipient does not exist")
        return
    response = "accepted" if is_attending else "refused"
    serializer = NotificationSerializer(
        data={
            'notification_type': 'RES',
            'content_type': ContentType.objects.get_for_model(MovieNightInvitation).id,
            'object_id': movie_night_invitation.id,
            'message': f"{sender.email} have {response} to participate in your movie night."
        }
    )
    if serializer.is_valid():
        serializer.save(sender=sender, recipient=recipient)
    else:
        logger.error(f"Notification serialization error: {serializer.errors}")    


def send_movie_night_update(movie_night, start_time):
    """
    Sends a notification to all invitees who accepted the invitation, informing them about 
    the updated start time for the movie night.
    
    Args:
        movie_night (MovieNight): The movie night instance.
        start_time (datetime): The new start time for the movie night.
    
    The function notifies the invitees of the updated start time for the event.
    """
    try:
        sender = User.objects.get(email=movie_night.creator.email)
    except User.DoesNotExist:
        logger.error("Sender does not exist")
        return

    recipients = [
        invite.invitee for invite in movie_night.invites.filter(is_attending=True)
    ]
    
    for recipient in recipients:
        serializer = NotificationSerializer(
            data={
                'notification_type': 'UPD',
                'content_type': ContentType.objects.get_for_model(MovieNight).id,
                'object_id': movie_night.id,
                'message': f"{sender.email} have changed start time for a movie night to {start_time}."
            }
        )
        if serializer.is_valid():
            
            serializer.save(sender=sender, recipient=recipient)
        else:
            logger.error(f"Notification serialization error: {serializer.errors}")   


def send_starting_notification(movie_night):
    """
    Sends a notification reminding the creator and invitees that the movie night is starting soon.
    
    Args:
        movie_night (MovieNight): The movie night instance.
    
    The function sends notifications to the creator and all accepted invitees, reminding them 
    that the movie night is starting soon.
    """
    recipients = [
        invite.invitee for invite in movie_night.invites.filter(is_attending=True)
    ]
    recipients.append(movie_night.creator)
    
    for recipient in recipients:
        serializer = NotificationSerializer(
            data={
                'notification_type': 'REM',
                'content_type': ContentType.objects.get_for_model(MovieNight).id,
                'object_id': movie_night.id,
                'message': f"The movie night that you have participated will start soon."
            }
        )
        if serializer.is_valid():
            serializer.save(recipient=recipient)
        else:
            logger.error(f"Notification serialization error: {serializer.errors}")       
    movie_night.start_notification_sent = True
    movie_night.save()


def notify_of_starting_soon():
    """
    Sends notifications for movie nights that are starting soon.
    
    The function finds all movie nights that have not sent a starting notification yet
    and are within the 'start_notification_before' window. It then sends a reminder
    notification to the creator and accepted invitees.
    """
    movie_nights = MovieNight.objects.filter(
        start_notification_sent=False,
        start_time__lt=timezone.now() + F('start_notification_before')
    )

    for movie_night in movie_nights:
        send_starting_notification(movie_night)


def send_movie_night_delete(movie_night):
    """
    Sends a cancellation notification to all invitees when a movie night is canceled.
    
    Args:
        movie_night (MovieNight): The movie night instance.
    
    The function notifies all accepted invitees that the movie night has been canceled.
    """
    try:
        sender = User.objects.get(email=movie_night.creator.email)
    except User.DoesNotExist:
        logger.error("Sender does not exist")
        return

    recipients = [
        invite.invitee for invite in movie_night.invites.filter(is_attending=True)
    ]

    formatted_start_time = movie_night.start_time.strftime('%Y-%m-%d %H:%M:%S')
    for recipient in recipients:
        serializer = NotificationSerializer(
            data={
                'notificcation_type': 'CAN',
                'content_type': ContentType.objects.get_for_model(MovieNight).id,
                'object_id': movie_night.id,
                'message': f"{sender.email} have canceled a movie night ({movie_night.movie} at {formatted_start_time})."
            }
        )
        if serializer.is_valid():
            serializer.save(sender=sender, recipient=recipient)
        else:
            logger.error(f"Notification serialization error: {serializer.errors}")

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""

### Another version for send notifications by email ###
# """
# Notification functions for MovieNight application.

# This module provides functions to send various email notifications for movie night events,
# such as invitations, attendance changes, movie night updates, and notifications for when 
# a movie night is starting soon. The emails are templated using Django's template system 
# and sent via the configured email backend.

# Functions:
# - `send_invitation`: Sends an invitation email to an invitee for a specific movie night.
# - `send_attendance_change`: Notifies the creator when an invitee's attendance status changes.
# - `send_starting_notification`: Notifies the invitees and creator that the movie night is starting soon.
# - `notify_of_starting_soon`: Finds movie nights starting within 30 minutes and sends notifications.
# - `send_movie_night_update`: Notifies invitees when a movie night start time has been updated.

# """

# from datetime import timedelta
# from urllib.parse import urljoin
# from django.conf import settings
# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from django.urls import reverse
# from django.utils import timezone
# from movies.models import MovieNight
# import logging

# logger = logging.getLogger(__name__)

# def send_invitation(movie_night_invitation):
#     """
#     Send an invitation email to the invitee for a movie night.

#     Args:
#     - movie_night_invitation: The MovieNightInvitation object containing the movie night 
#       and the invitee information.

#     The email contains a link to view the movie night details and is sent to the invitee.
#     """
#     subject = render_to_string(
#         "movies/notifications/invitation_subject.txt",
#         {"movie_night": movie_night_invitation.movie_night},
#     )

#     movie_night_path = reverse(
#         "movienight_detail", args=(movie_night_invitation.movie_night.pk,)
#     )

#     body = render_to_string(
#         "movies/notifications/invitation_body.txt",
#         {
#             "creator": movie_night_invitation.movie_night.creator,
#             "movie_night": movie_night_invitation.movie_night,
#             "movie_night_url": urljoin(settings.BASE_URL, movie_night_path),
#         },
#     )

#     send_mail(
#         subject,
#         body,
#         None,
#         [movie_night_invitation.invitee.email],
#     )


# def send_attendance_change(movie_night_invitation, is_attending):
#     """
#     Notify the creator when an invitee updates their attendance status for a movie night.

#     Args:
#     - movie_night_invitation: The MovieNightInvitation object.
#     - is_attending: Boolean indicating if the invitee will attend.

#     The creator receives an email notification about the invitee's attendance status update.
#     """
#     subject = render_to_string(
#         "movies/notifications/attendance_update_subject.txt",
#         {
#             "movie_night": movie_night_invitation.movie_night,
#             "movie_night_invitation": movie_night_invitation,
#         },
#     )

#     movie_night_path = reverse(
#         "movienight_detail", args=(movie_night_invitation.movie_night.pk,)
#     )

#     body = render_to_string(
#         "movies/notifications/attendance_update_body.txt",
#         {
#             "is_attending": is_attending,
#             "movie_night_invitation": movie_night_invitation,
#             "movie_night": movie_night_invitation.movie_night,
#             "movie_night_url": urljoin(settings.BASE_URL, movie_night_path),
#         },
#     )

#     send_mail(
#         subject,
#         body,
#         None,
#         [movie_night_invitation.movie_night.creator.email],
#     )


# def send_starting_notification(movie_night):
#     """
#     Notify invitees and the creator that the movie night is starting soon.

#     Args:
#     - movie_night: The MovieNight object.

#     This function sends an email to all confirmed invitees and the creator when a movie
#     night is starting soon (typically 30 minutes before the event).
#     """

#     subject = render_to_string(
#         "movies/notifications/starting_subject.txt",
#         {"movie_night": movie_night},
#     )

#     movie_night_path = reverse("movienight_detail", args=(movie_night.pk,))

#     body = render_to_string(
#         "movies/notifications/starting_body.txt",
#         {
#             "movie_night": movie_night,
#             "movie_night_url": urljoin(settings.BASE_URL, movie_night_path),
#         },
#     )

#     to_emails = [
#         invite.invitee.email for invite in movie_night.invites.filter(is_attending=True)
#     ]
#     to_emails.append(movie_night.creator.email)

#     send_mail(
#         subject,
#         body,
#         None,
#         to_emails,
#     )
#     movie_night.start_notification_sent = True
#     movie_night.save()


# def notify_of_starting_soon():
#     """
#     Send notifications for movie nights starting within the next 30 minutes.

#     This function finds all movie nights that are about to start but have not yet
#     sent a notification, and sends a starting notification to the invitees and the creator.
#     """
#     start_before = timezone.now() + timedelta(minutes=60)

#     movie_nights = MovieNight.objects.filter(
#         start_time__lte=start_before, start_notification_sent=False
#     )

#     for movie_night in movie_nights:
#         send_starting_notification(movie_night)



# def send_movie_night_update(movie_night, start_time):
#     """
#     Notify invitees when the movie night start time is updated.

#     Args:
#     - movie_night: The MovieNight object.
#     - start_time: The updated start time of the movie night.

#     This function sends an email to all confirmed invitees to inform them about
#     the new start time of the movie night.
#     """
#     subject = render_to_string(
#         "movies/notifications/movie_night_update_subject.txt",
#         {
#             "movie_night": movie_night,
#         },
#     )

#     movie_night_path = reverse(
#         "movienight_detail", args=(movie_night.pk,)
#     )

#     body = render_to_string(
#         "movies/notifications/movie_night_update_body.txt",
#         {
#             "start_time": start_time,
#             "movie_night": movie_night,
#             "movie_night_url": urljoin(settings.BASE_URL, movie_night_path),
#         },
#     )

#     to_emails = [
#         invite.invitee.email for invite in movie_night.invites.filter(is_attending=True)
#     ]

#     send_mail(
#         subject,
#         body,
#         None,
#         to_emails,
#     )