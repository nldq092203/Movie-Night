"""
Celery tasks for the movies app, handling background operations like OMDB integration and notifications.

Tasks:
- `search_and_save`: Initiates a search through OMDB's API and saves the results.
- `send_invitation`: Sends a movie night invitation notification to a user based on the invitation's primary key.
- `send_attendance_change`: Sends a notification when an invitee's attendance status changes.
- `notify_of_starting_soon`: Sends notifications when a movie night is starting soon.
- `send_movie_night_update`: Sends notifications when a movie night start time is updated.

Each task utilizes background processing to offload these operations and improve the overall responsiveness of the app.
"""

from celery import shared_task
from movies import omdb_integration
from movies import notifications
from movies.models import MovieNightInvitation, MovieNight
import logging 
logger = logging.getLogger(__name__)

@shared_task
def search_and_save(search):
    return omdb_integration.search_and_save(search)



@shared_task
def send_invitation(mni_pk):
    logger.info(f"Attempting to fetch MovieNightInvitation with pk={mni_pk}")
    try:
        movie_night_invitation = MovieNightInvitation.objects.get(pk=mni_pk)
        notifications.send_invitation(movie_night_invitation)
    except MovieNightInvitation.DoesNotExist:
        logger.error(f"MovieNightInvitation with pk={mni_pk} does not exist")

@shared_task
def send_attendance_change(mni_pk, is_attending):
    notifications.send_attendance_change(
        MovieNightInvitation.objects.get(pk=mni_pk), is_attending
    )

@shared_task
def notify_of_starting_soon():
    notifications.notify_of_starting_soon()

@shared_task
def send_movie_night_update(mn_pk, start_time):
    notifications.send_movie_night_update(
        MovieNight.objects.get(pk=mn_pk), start_time
    )

@shared_task
def send_movie_night_delete(mn_pk):
    notifications.send_movie_night_delete(
        MovieNight.objects.get(pk=mn_pk)
    )

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""