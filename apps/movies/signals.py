"""
This module contains Django signal handlers for the Movie Night application. These handlers 
are responsible for sending notifications to users when key events occur, such as the creation 
of movie night invitations, changes in attendance, updates to movie night start times, and 
movie night cancellations. These notifications are processed asynchronously using Celery tasks.

Signal Handlers:
- send_invitation: Triggered when a new movie night invitation is created.
- send_attendance_change: Triggered when an invitee changes their attendance status.
- send_movie_night_update: Triggered when the start time of a movie night is updated.
- send_movie_night_delete: Triggered when a movie night is deleted.

"""

from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, pre_delete
from apps.movies.models import MovieNightInvitation, MovieNight
from apps.movies import tasks
from django.db import transaction
import logging
logger = logging.getLogger(__name__)

@receiver(post_save, sender=MovieNightInvitation, dispatch_uid="invitation_created")
def send_invitation(sender, instance, created, **kwargs):
    """
    Signal to send an invitation notification when a new MovieNightInvitation is created.
    
    This signal triggers after the MovieNightInvitation object is saved (post_save).
    It ensures that a Celery task is called to send the invitation asynchronously only after 
    the database transaction is fully committed, ensuring data integrity.
    
    Args:
        sender: The model class (MovieNightInvitation).
        instance: The actual instance being saved.
        created: Boolean that indicates if a new record was created (True) or an existing one was updated (False).
        **kwargs: Additional keyword arguments.
    """
    if created:
        logger.warning("In send_invitation")
        # Ensure the task runs only after the transaction is committed.
        # transaction.on_commit(lambda: tasks.send_invitation.delay(instance.pk))
        tasks.send_invitation.delay(instance.pk)
        logger.warning("In send_invitation")


@receiver(pre_save, sender=MovieNightInvitation, dispatch_uid="invitation_updated")
def send_attendance_change(sender, instance, **kwargs):
    """
    Signal to handle notifications when the attendance status of an invitee changes.
    
    This signal triggers before the MovieNightInvitation object is saved (pre_save). 
    It checks whether the attendance status has changed and, if so, sends a notification 
    using a Celery task. It only applies to existing invitations (not new ones).
    
    Args:
        sender: The model class (MovieNightInvitation).
        instance: The actual instance being saved (updated).
        **kwargs: Additional keyword arguments.
    """
    if not instance.pk:
        # This is a new invitation, no need to handle attendance change.
        return
    
    # Retrieve the previous state of the invitation.
    previous_invitation = MovieNightInvitation.objects.get(pk=instance.pk)
    instance.attendance_confirmed = True  # Automatically confirm attendance upon change.

    # Only notify if the attendance status has changed.
    if previous_invitation.is_attending != instance.is_attending:
        # Use Celery to send the notification asynchronously.
        tasks.send_attendance_change.delay(instance.pk, instance.is_attending)


@receiver(pre_save, sender=MovieNight, dispatch_uid="movie_night_update")
def send_movie_night_update(sender, instance, **kwargs):
    """
    Signal to send a notification when the start time of a MovieNight is updated.
    
    This signal triggers before the MovieNight object is saved (pre_save). 
    It compares the current start time with the previous start time and sends an update 
    notification if there is a change.
    
    Args:
        sender: The model class (MovieNight).
        instance: The actual instance being saved (updated).
        **kwargs: Additional keyword arguments.
    """
    if not instance.pk:
        # This is a new MovieNight, no need to handle updates.
        return
    
    # Retrieve the previous state of the MovieNight.
    previous_movie_night = MovieNight.objects.get(pk=instance.pk)
    
    # Check if the start time has changed, and if so, send an update notification.
    if previous_movie_night.start_time != instance.start_time:
        # Use Celery to send the notification asynchronously.
        tasks.send_movie_night_update.delay(instance.pk, instance.start_time)


@receiver(pre_delete, sender=MovieNight, dispatch_uid="movie_night_update")
def send_movie_night_delete(sender, instance, **kwargs):
    """
    Signal to send a cancellation notification when a MovieNight is deleted.
    
    This signal triggers before the MovieNight object is deleted (pre_delete). 
    It sends a cancellation notification using a Celery task, notifying all participants 
    that the MovieNight has been canceled.
    
    Args:
        sender: The model class (MovieNight).
        instance: The actual instance being deleted.
        **kwargs: Additional keyword arguments.
    """
    # Use Celery to send the deletion notification asynchronously.
    tasks.send_movie_night_delete.delay(instance.pk)

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""