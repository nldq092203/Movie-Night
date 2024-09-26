from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from movies.models import MovieNightInvitation, MovieNight
from movies import tasks

@receiver(post_save, sender=MovieNightInvitation, dispatch_uid="invitation_created")
def send_invitation(sender, instance, created, **kwargs):
    if created:
        tasks.send_invitation.delay(instance.pk)

@receiver(pre_save, sender=MovieNightInvitation, dispatch_uid="invitation_updated")
def send_attendance_change(sender, instance, **kwargs):
    if not instance.pk:
        # Is a new one
        return
    
    previous_invitation = MovieNightInvitation.objects.get(pk=instance.pk)
    instance.attendance_confirmed = True

    # Only notify if there is a change in attendance
    if previous_invitation.is_attending != instance.is_attending:
        tasks.send_attendance_change.delay(instance.pk, instance.is_attending)

@receiver(pre_save, sender=MovieNight, dispatch_uid="movie_night_update")
def send_movie_night_update(sender, instance, **kwargs):
    if not instance.pk:
        return
    previous_movie_night = MovieNight.objects.get(pk=instance.pk)
    
    if previous_movie_night.start_time != instance.start_time:
        tasks.send_movie_night_update.delay(instance.pk, instance.start_time)
 