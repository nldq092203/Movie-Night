"""
This module contains Django REST Framework serializers for handling serialization and validation of 
various models in a movie night application. These models include User, Genre, Movie, 
MovieNight, MovieNightInvitation, and SearchTerm. Each serializer handles data 
validation, serialization to and from JSON, and custom logic for specific fields.
"""

from rest_framework import serializers
from movies.models import Genre, Movie, SearchTerm, MovieNight, MovieNightInvitation
from movienight_auth.models import User
from django.utils import timezone
from datetime import timedelta
from typing import List
import logging
logger = logging.getLogger(__name__)




class GenreSerializer(serializers.ModelSerializer):
    """
    Serializer for the Genre model. Validates and serializes genre data.
    """
    class Meta:
        model = Genre
        fields = "__all__"

    def validate_name(self, value):
        """
        Ensure the genre name is unique (case-insensitive) and is stored in lowercase.
        """
        value_lower = value.lower()
        if Genre.objects.filter(name__iexact=value_lower).exists():
            raise serializers.ValidationError(f"The genre '{value}' already exists.")
        return value_lower


class MovieSearchSerializer(serializers.Serializer):
    """
    Serializer for a search term input for searching movies.
    This serializer only handles a single field: 'term'.
    """
    term = serializers.CharField(max_length=255)


class MovieSerializer(serializers.ModelSerializer):
    """
    Serializer for the Movie model. Serializes basic movie information.
    """
    class Meta:
        model = Movie
        fields = ["id", "imdb_id", "title", "year", "url_poster", "imdb_rating"]

    def validate_url_poster(self, value):
        # Accept all values for url_poster
        return value

class GenreField(serializers.StringRelatedField):
    """
    Custom field for handling genres. Converts genre names into Genre objects.
    """

    def to_internal_value(self, data):
        """
        Converts the input genre name into a Genre object.
        """
        try:
            # Fetch or create a genre object based on the provided genre name
            genre, created = Genre.objects.get_or_create(name=data.lower())
            return genre
        except (TypeError, ValueError):
            self.fail(f"Genre value '{data}' is invalid")


class MovieDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed Movie information, including genres.
    """
    genres = GenreField(many=True)

    class Meta:
        model = Movie
        fields = "__all__"

    def validate_year(self, value):
        """
        Validate that the year of the movie is a positive integer.
        """
        if value <= 0:
            raise serializers.ValidationError("Year must be a positive integer.")
        return value


class SearchTermSerializer(serializers.ModelSerializer):
    """
    Serializer for the SearchTerm model. Tracks search terms used by users.
    """
    class Meta:
        model = SearchTerm
        fields = "__all__"

    def validate_name(self, value):
        """
        Ensure the search term is in lowercase.
        """
        return value.lower()


class MovieNightSerializer(serializers.ModelSerializer):
    """
    Serializer for MovieNight model. Includes fields for the creator, movie, and start time.
    """
    creator = serializers.ReadOnlyField(source='creator.email')
    is_creator = serializers.SerializerMethodField()

    class Meta:
        model = MovieNight
        fields = ['id', 'start_time', 'start_notification_before', 'creator', 'movie', 'is_creator']
        read_only = ['is_creator']

    def validate_start_time(self, value):
        """
        Ensure the start time of the movie night is in the future.
        """
        if value <= timezone.now():
            raise serializers.ValidationError("Start time must be in the future.")
        return value

    def get_is_creator(self, obj):
        """
        Determine if the requesting user is the creator of the movie night.
        """
        request = self.context.get('request', None)
        return request and obj.creator == request.user


class MovieNightDetailSerializer(MovieNightSerializer):
    """
    Detailed serializer for MovieNight, adding pending invitees and participants information.
    """
    pending_invitees = serializers.SerializerMethodField()
    participants = serializers.SerializerMethodField()

    class Meta:
        model = MovieNight
        fields = [
            "id",
            "movie",
            "start_time",
            "creator",
            "start_notification_sent",
            "start_notification_before",
            "pending_invitees",
            "participants",
            "is_creator"
        ]
        read_only = ["creator"]

    def get_participants(self, obj) -> List[str]:
        """ 
        Retrieve emails of invitees who have confirmed their attendance.
        """
        confirmed_invitees = MovieNightInvitation.objects.filter(
            movie_night=obj, attendance_confirmed=True, is_attending=True
        ).select_related('invitee')

        return [invitee.invitee.email for invitee in confirmed_invitees]

    def get_pending_invitees(self, obj) -> List[str]:
        """
        Retrieve emails of invitees who haven't confirmed yet, 
        but only return this data if the requesting user is the creator.
        """
        request = self.context.get('request')

        if request and obj.creator == request.user:
            pending_invitees = MovieNightInvitation.objects.filter(
                movie_night=obj, attendance_confirmed=False
            ).select_related('invitee')

            return [invitee.invitee.email for invitee in pending_invitees]

        return []


class MovieNightInvitationSerializer(serializers.ModelSerializer):
    """
    Serializer for MovieNightInvitation model. Handles the invitee and invitation data.
    """
    invitee = serializers.EmailField()

    class Meta:
        model = MovieNightInvitation
        fields = [
            "id",
            "invitee",
            "movie_night",
            "attendance_confirmed",
            "is_attending"
        ]

    def validate_invitee(self, value):
        """
        Ensure the invitee is a valid user identified by their email.
        """
        try:
            return User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User with email {value} does not exist.")

    def validate(self, data):
        """
        Check that the combination of invitee and movie night is unique.
        """
        invitee = data.get('invitee')
        movie_night = data.get('movie_night')

        if MovieNightInvitation.objects.filter(invitee=invitee, movie_night=movie_night).exists():
            raise serializers.ValidationError("This user has already been invited to this movie night.")
        
        return data

    def create(self, validated_data):
        """
        Set default values for attendance_confirmed and is_attending if not provided.
        """
        validated_data.setdefault('attendance_confirmed', False)
        validated_data.setdefault('is_attending', False)
        return super().create(validated_data)


    
"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""