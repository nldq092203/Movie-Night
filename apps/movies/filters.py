"""
Defines filtering logic for the Movie model
"""
from django_filters import rest_framework as filters

from apps.movies.models import Movie, Genre, MovieNight, MovieNightInvitation

class MovieFilterSet(filters.FilterSet):
    """
    A filter set for the Movie model to allow users to filter movies based on various criteria, 
    including publication year range, runtime, IMDb rating, genres, and title.

    Filters:
    - published_from: Filters movies published after or during the given year.
    - published_to: Filters movies published before or during the given year.
    - runtime_minutes_from: Filters movies with a runtime greater than or equal to the given value.
    - runtime_minutes_to: Filters movies with a runtime less than or equal to the given value.
    - imdb_rating_from: Filters movies with an IMDb rating greater than or equal to the given value.
    - genres: Filters movies that belong to the specified genres. Uses AND logic (conjoined=True).
    - title: Filters movies whose titles contain the given substring (case-insensitive).
    """
    published_from = filters.NumberFilter(
        field_name="year", lookup_expr="gte", label="Published Date From"
    )
    published_to = filters.NumberFilter(
        field_name="year", lookup_expr="lte", label="Published Date To"
    )
    runtime_minutes_to = filters.NumberFilter(
        field_name="runtime_minutes", lookup_expr="lte", label="Maximum Runtime (minutes)"
    )
    runtime_minutes_from = filters.NumberFilter(
        field_name="runtime_minutes", lookup_expr="gte", label="Minimum Runtime (minutes)"
    )
    imdb_rating_from = filters.NumberFilter(
        field_name="imdb_rating", lookup_expr="gte", label="Minimum IMDb Rating"
    )
    genres = filters.ModelMultipleChoiceFilter(
        queryset=Genre.objects.all(),
        field_name="genres__name",
        to_field_name="name",
        label="Genres",
        conjoined=True 
    )
    title = filters.CharFilter(
        field_name="title", lookup_expr="icontains", label="Title Contains"
    )
    class Meta:
        model = Movie
        fields = [
            'genres', 'country', 'published_from', 'published_to', 
            'runtime_minutes_from', 'runtime_minutes_to', 
            'imdb_rating_from', 'title', 'is_full_record'
        ]

class MyMovieNightFilterSet(filters.FilterSet):
    start_from = filters.DateTimeFilter(
        field_name="start_time", lookup_expr="gte", label="Start Time From"
    )
    start_to = filters.DateTimeFilter(
        field_name="start_time", lookup_expr="lte", label="Start Time To"
    )
    class Meta:
        model = MovieNight
        fields = ["start_time"]    
        
class ParticipatingMovieNightFilterSet(filters.FilterSet):
    """
    FilterSet for filtering MovieNight instances based on:
    - start time (from and to)
    - creator
    - invitee (based on invitations)
    """
    creator_email = filters.CharFilter(field_name="creator__email", lookup_expr="icontains")

    start_from = filters.DateTimeFilter(
        field_name="start_time", lookup_expr="gte", label="Start Time From"
    )
    start_to = filters.DateTimeFilter(
        field_name="start_time", lookup_expr="lte", label="Start Time To"
    )
    
    class Meta:
        model = MovieNight
        fields = [
            'creator_email', 'invites__invitee', 'start_time'
        ]

class MovieNightInvitationFilterSet(filters.FilterSet):
    """
    Filters for MovieNight invitations:
    - `attendance_confirmed`: Whether the invitee has responded to the invitation.
    - `is_attending`: Whether the invitee accepts the invitation.
    """

    attendance_confirmed = filters.BooleanFilter(
        field_name="attendance_confirmed",
        label="Response Received (Confirmed)",
        help_text="Filter invitations where invitees have responded to the invitation."
    )
    
    is_attending = filters.BooleanFilter(
        field_name="is_attending",
        label="Confirmed Attendance (Will Attend)",
        help_text="Filter invitations where invitees have accepted the invitation."
    )

    class Meta:
        model = MovieNightInvitation
        fields = ["is_attending", "attendance_confirmed"]

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""