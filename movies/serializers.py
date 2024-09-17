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
        fields = "__all__"

class MovieDetailSerializer(MovieSerializer):
    def update(self, instance, validated_data):
        instance.title = validated_data.get("title", instance.title)
        instance.year = validated_data.get("year", instance.year)
        instance.runtime_minutes = validated_data.get("runtime_minutes", instance.runtime_minutes)
        instance.genres.clear()
        for genre_name in validated_data.get("genres", []):
            genre, created = Genre.objects.get_or_create(name=genre_name)
            instance.genre.add(genre)
        instance.plot = validated_data("plot", instance.plot)
        instance.country = validated_data("country", instance.country)
        instance.imbd_rating = validated_data("imdb_rating", instance.imdb_rating)
        instance.url_poster = validated_data("url_poster", instance.url_poster)
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
        queryset=User.onjects.all(), view_name="api_user_detail", lookup_field="email"
    )

    movie_night = serializers.HyperlinkedRelatedField(
        queryset=MovieNight.objects.all(), view_name="api_movienight_detail", lookup_field="email"
    )
    class Meta:
        model = MovieNightInvitation
        fields = "__all__"

    
    
