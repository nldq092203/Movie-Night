from django_celery_beat.models import IntervalSchedule, PeriodicTask

def schedule_setup():
    """
    Sets up a periodic task that runs every minute to check for movies that 
    are starting soon.

    - The function creates or retrieves an interval schedule that triggers every minute.
    - A periodic task is then created or linked to this schedule to execute the 
      `notify_of_starting_soon` task from the `movie.tasks` module.

    This ensures that the system regularly checks if any movie nights are starting 
    within a specific timeframe and sends appropriate notifications.
    """
    minute_schedule, created = IntervalSchedule.objects.get_or_create(period=IntervalSchedule.MINUTES, every=1)
    check_movie_time = PeriodicTask(
        name="Check movie start time each minute",
        interval=minute_schedule,
        task='movie.tasks.notify_of_starting_soon'
    )

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""