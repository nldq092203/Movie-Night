from rest_framework import serializers
from movies.models import Genre, Movie, SearchTerm, MovieNight, MovieNightInvitation, UserProfile
from movienight_auth.models import User
from django.utils import timezone
from typing import List
import logging
logger = logging.getLogger(__name__)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = "__all__"

    def validate_name(self, value):
        """
        Ensure the genre name is always in lowercase and is unique (case-insensitive).
        """
        value_lower = value.lower()
        if Genre.objects.filter(name__iexact=value_lower).exists():
            raise serializers.ValidationError(f"The genre '{value}' already exists.")
        return value_lower

class MovieSearchSerializer(serializers.Serializer):
    term = serializers.CharField(max_length=255)
    
class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ["id", "imdb_id", "title", "year", "url_poster"]

class GenreField(serializers.StringRelatedField):
    def to_internal_value(self, data):
        try:
            # Fetch or create a genre object based on the provided genre name
            genre, created = Genre.objects.get_or_create(name=data.lower())
            return genre  # Return the Genre instance
        except (TypeError, ValueError):
            self.fail(f"Genre value '{data}' is invalid")


class MovieDetailSerializer(serializers.ModelSerializer):
    genres = GenreField(many=True)

    class Meta:
        model = Movie
        fields = "__all__"

    def validate_year(self, value):
        """
        Ensure the year is a positive integer.
        """
        if value <= 0:
            raise serializers.ValidationError("Year must be a positive integer.")
        return value

class SearchTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchTerm
        fields = "__all__"

    def validate_name(self, value):
        """
        Ensure the search term is always in lowercase.
        """
        return value.lower()

class MovieNightSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source='creator.email') 
    is_creator = serializers.SerializerMethodField()
    class Meta:
        model = MovieNight
        fields = ['id', 'start_time', 'creator', 'movie', 'is_creator']
        read_only = ['is_creator']
        
    def validate_start_time(self, value):
        """
        Check that the start_time is in the future.
        """
        if value <= timezone.now():
            raise serializers.ValidationError("Start time must be in the future.")
        return value
    
    def get_is_creator(self, obj):
        request = self.context.get('request', None)
        return request and obj.creator == request.user

class MovieNightDetailSerializer(MovieNightSerializer):
    creator = serializers.ReadOnlyField(source='creator.email') 
    pending_invitees = serializers.SerializerMethodField()
    participants = serializers.SerializerMethodField()

    class Meta:
        model = MovieNight
        fields = "__all__"


    def validate_creator(self, value):
        """
        Ensure the creator is a valid user identified by their email.
        If the email doesn't correspond to an existing user, raise an error.
        """
        try:
            return User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User with email {value} does not exist.")

    def get_participants(self, obj) -> List[str]:
        """ 
        Get all invitees who have confirmed attendance.
        This method returns a list of emails for users who have confirmed their attendance.
        """
        confirmed_invitees = MovieNightInvitation.objects.filter(
            movie_night=obj, attendance_confirmed=True, is_attending=True
        ).select_related('invitee')  # Optimized to load related users with one query

        # Extract the emails of confirmed invitees
        return [invitee.invitee.email for invitee in confirmed_invitees]

    def get_pending_invitees(self, obj) -> List[str]:
        """
        Get all invitees who haven't confirmed yet. Only return the pending invitees if 
        the requesting user is the creator.
        """
        request = self.context.get('request')

        # Ensure the user is the creator of the movie night
        if request and obj.creator == request.user:
            pending_invitees = MovieNightInvitation.objects.filter(
                movie_night=obj, attendance_confirmed=False
            ).select_related('invitee')

            return [invitee.invitee.email for invitee in pending_invitees]

        # If the user is not the creator, return an empty list or None
        return []

class MovieNightInvitationSerializer(serializers.ModelSerializer):
    invitee = serializers.EmailField()
    invited_time = serializers.ReadOnlyField()
    class Meta:
        model = MovieNightInvitation
        fields = "__all__"

    def validate_invitee(self, value):
        """
        Ensure the invitee is a valid user identified by their email.
        """
        try:
            # Look up the User object by email
            return User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User with email {value} does not exist.")

    def validate(self, data):
        """
        Check that the invitee and movie_night combination is unique.
        """
        invitee = data.get('invitee')
        movie_night = data.get('movie_night')

        # Ensure the combination of invitee and movie_night is unique
        if MovieNightInvitation.objects.filter(invitee=invitee, movie_night=movie_night).exists():
            raise serializers.ValidationError("This user has already been invited to this movie night.")
        
        return data

    def create(self, validated_data):
        """
        Automatically set attendance_confirmed and is_attending to False if they are not provided in the request.
        """
        validated_data.setdefault('attendance_confirmed', False)
        validated_data.setdefault('is_attending', False)
        return super().create(validated_data)
    
"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""