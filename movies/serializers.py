from rest_framework import serializers
from movies.models import Genre, Movie, SearchTerm, MovieNight, MovieNightInvitation
from movienight_auth.models import User

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

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ["imdb_id", "title", "year"]

class GenreField(serializers.StringRelatedField):
    def to_internal_value(self, data):
        try:
            # Fetch or create a genre object based on the provided genre name
            genre, created = Genre.objects.get_or_create(name=data.lower())
            return genre  # Return the Genre instance
        except (TypeError, ValueError):
            self.fail(f"Genre value '{data}' is invalid")


class MovieDetailSerializer(serializers.ModelSerializer):
    genres = GenreField(many=True)  # Handling multiple genres

    class Meta:
        model = Movie
        fields = "__all__"

    def update(self, instance, validated_data):
        instance = super(MovieDetailSerializer, self).update(instance, validated_data)
        instance.is_full_record = True
        instance.save()

        return instance

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
    creator = serializers.EmailField()  # Use the email field for both reading and writing

    class Meta:
        model = MovieNight
        fields = "__all__"

    def validate_creator(self, value):
        """
        Ensure the creator is a valid user identified by their email.
        """
        try:
            # Find the user by their email during deserialization
            return User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User with email {value} does not exist.")



class MovieNightInvitationSerializer(serializers.ModelSerializer):
    invitee = serializers.EmailField()  # Use email for both deserialization and serialization

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


    
