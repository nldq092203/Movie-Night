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
    # Create or get the periodic task linked to this schedule
    task, created = PeriodicTask.objects.get_or_create(
        name="Test movie start time each minute",
        interval=minute_schedule,
        task='movies.tasks.notify_of_starting_soon',
        enabled=True
    )
    

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""