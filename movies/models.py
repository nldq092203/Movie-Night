from django.contrib.auth import get_user_model
from django.db import models


from datetime import timedelta

UserModel = get_user_model()

class UserProfile(models.Model):
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField()

    def __str__(self):
        return f"{self.__class__.__name__} object for {self.user}"

class Genre(models.Model):
    class Meta:
        ordering = ["name"]
    
    name = models.TextField(unique=True)

    def __str__(self):
        return self.name
    
class SearchTerm(models.Model):
    class Meta:
        ordering = ["term"]

    term = models.TextField(unique=True)
    last_search = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.term
    
class Movie(models.Model):
    class Meta:
        ordering = ["title", "year"]
    
    imdb_id = models.SlugField(unique=True)
    title = models.TextField()
    year = models.PositiveIntegerField()
    runtime_minutes = models.PositiveIntegerField(null=True)
    genres = models.ManyToManyField(Genre, related_name="movies")
    plot = models.TextField()
    country = models.TextField()
    imdb_rating = models.FloatField()
    url_poster = models.URLField()
    is_full_record = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({self.year})"

class MovieNight(models.Model):
    class Meta:
        ordering = ["creator", "start_time"]

    movie = models.ForeignKey(Movie, on_delete=models.PROTECT)
    start_time = models.DateTimeField()
    creator = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    start_notification_sent = models.BooleanField(default=False)

    @property
    def end_time(self):
        if not self.movie.runtime_minutes:
            return None

        return self.start_time + timedelta(minutes=self.movie.runtime_minutes)

    def __str__(self):
        return f"{self.movie} by {self.creator.email}"
    

class MovieNightInvitation(models.Model):
    class Meta:
        unique_together = [("invitee", "movie_night")]

    movie_night = models.ForeignKey(
        MovieNight, on_delete=models.CASCADE, related_name="invites"
    )
    invitee = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    attendance_confirmed = models.BooleanField(default=False)
    is_attending = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.movie_night} / {self.invitee.email}"

