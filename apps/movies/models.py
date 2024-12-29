"""
This module defines models related to a movie night application, which includes genres, search terms, movies, movie nights, and movie night invitations.
Each model includes methods to handle business logic, including saving data, and representing objects with human-readable formats.

"""

from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from datetime import timedelta
from apps.notifications.models import Notification
from django.contrib.contenttypes.models import ContentType
UserModel = get_user_model()


class Genre(models.Model):
    """
    Genre model represents movie genres. Each genre name is unique and lowercased.
    """
    class Meta:
        ordering = ["name"]
    
    name = models.TextField(unique=True)

    def __str__(self):
        """
        Returns the genre's name as a string.
        """
        return self.name
    
    def save(self, *args, **kwargs):
        """
        Override the save method to automatically lowercase genre names before saving.
        """
        if self.name:
            self.name = self.name.lower()
        super(Genre, self).save(*args, **kwargs)


class SearchTerm(models.Model):
    """
    SearchTerm model tracks search terms entered by users. Each search term is unique
    and lowercased, and the timestamp of the last search is updated automatically.
    """
    class Meta:
        ordering = ["term"]

    term = models.TextField(unique=True)
    last_search = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Returns the search term as a string.
        """
        return self.term
    
    def save(self, *args, **kwargs):
        """
        Override the save method to automatically lowercase search terms before saving.
        """
        if self.term:
            self.term = self.term.lower()
        super(SearchTerm, self).save(*args, **kwargs)


class Movie(models.Model):
    """
    Movie model represents a movie with its basic details such as title, year, IMDb rating, etc.
    Movies can be related to multiple genres.
    """
    class Meta:
        ordering = ["title", "year"]
    
    imdb_id = models.SlugField(unique=True)
    title = models.TextField()
    year = models.PositiveIntegerField()
    runtime_minutes = models.PositiveIntegerField(null=True)
    genres = models.ManyToManyField(Genre, related_name="movies")
    plot = models.TextField()
    country = models.TextField()
    imdb_rating = models.FloatField(default=0)
    url_poster = models.URLField()
    is_full_record = models.BooleanField(default=False)

    def __str__(self):
        """
        Returns the movie's title and release year as a string.
        """
        return f"{self.title} ({self.year})"


class MovieNight(models.Model):
    """
    MovieNight model represents a scheduled movie night event. It includes details about
    the movie being watched, the start time, and notifications that are sent to participants.
    """
    class Meta:
        ordering = ["creator", "start_time"]

    movie = models.ForeignKey(Movie, on_delete=models.PROTECT)  # Protects the movie from being deleted if associated with a movie night
    start_time = models.DateTimeField()
    creator = models.ForeignKey(UserModel, on_delete=models.CASCADE)  # The user who created the movie night
    start_notification_sent = models.BooleanField(default=False)  # Whether the notification for the event start was sent
    start_notification_before = models.DurationField(default=timedelta(minutes=0))  # Time before the event to send notifications
    notifications = GenericRelation(Notification)  # Links notifications related to the movie night

    @property
    def end_time(self):
        """
        Calculates and returns the end time of the movie night based on the runtime of the movie.
        If the movie runtime is not set, it returns None.
        """
        if not self.movie.runtime_minutes:
            return None
        return self.start_time + timedelta(minutes=self.movie.runtime_minutes)

    def __str__(self):
        """
        Returns a string representation of the movie night, including the movie and creator's email.
        """
        return f"{self.movie} by {self.creator.email}"
    def delete(self, *args, **kwargs):
        Notification.objects.filter(content_type=ContentType.objects.get_for_model(self), object_id=self.id).update(content_type=None, object_id=None)
        super().delete(*args, **kwargs)

class MovieNightInvitation(models.Model):
    """
    MovieNightInvitation model represents an invitation sent to a user for a specific movie night.
    Each invitation is unique for a user and a movie night, and notifications can be generated
    based on the invitation status.
    """
    class Meta:
        unique_together = [("invitee", "movie_night")]  # Ensures that the same invitee can't receive multiple invitations for the same movie night

    movie_night = models.ForeignKey(MovieNight, on_delete=models.CASCADE, related_name="invites", db_index=True)
    invitee = models.ForeignKey(UserModel, on_delete=models.CASCADE, db_index=True)  # The user invited to the movie night
    attendance_confirmed = models.BooleanField(default=False)  # Whether the invitee has confirmed attendance
    is_attending = models.BooleanField(default=False)  # Whether the invitee is attending
    notifications = GenericRelation(Notification)  # Links notifications related to the invitation

    def __str__(self):
        """
        Returns a string representation of the invitation, including the movie night and invitee's email.
        """
        return f"{self.movie_night} / {self.invitee.email}"
    

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""