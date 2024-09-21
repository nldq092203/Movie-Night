from rest_framework import serializers
from movies.models import Genre, Movie, SearchTerm, MovieNight, MovieNightInvitation
from movienight_auth.models import User

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = "__all__"


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

class SearchTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchTerm
        fields = "__all__"

class MovieNightSerializer(serializers.ModelSerializer):
    author = serializers.HyperlinkedRelatedField(
        queryset=User.objects.all(), view_name="api_user_detail", lookup_field="email"
    )

    class Meta:
        model = MovieNight
        fields = "__all__"

class MovieNightInvitationSerializer(serializers.ModelSerializer):
    invitee = serializers.HyperlinkedRelatedField(
        queryset=User.objects.all(), view_name="api_user_detail", lookup_field="email"
    )

    movie_night = serializers.HyperlinkedRelatedField(
        queryset=MovieNight.objects.all(), view_name="api_movienight_detail", lookup_field="email"
    )
    class Meta:
        model = MovieNightInvitation
        fields = "__all__"

    
    
