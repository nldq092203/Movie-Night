"""
Defines factories for generating test data corresponding to models.
"""
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from movies.models import UserProfile, Genre, SearchTerm, Movie, MovieNight, MovieNightInvitation
from django.utils import timezone 
UserModel = get_user_model()

class UserFactory(DjangoModelFactory):
    class Meta:
        model = UserModel

    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', 'defaultpassword')


class UserProfileFactory(DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = factory.SubFactory(UserFactory)
    bio = factory.Faker('text')


class GenreFactory(DjangoModelFactory):
    class Meta:
        model = Genre

    name = factory.Faker('word')


class SearchTermFactory(DjangoModelFactory):
    class Meta:
        model = SearchTerm

    term = factory.Faker('word')
    last_search = factory.LazyFunction(timezone.now)


class MovieFactory(DjangoModelFactory):
    class Meta:
        model = Movie

    imdb_id = factory.Faker('slug')
    title = factory.Faker('sentence')
    year = factory.Faker('year')
    runtime_minutes = factory.Faker('random_int')
    plot = factory.Faker('paragraph')
    country = factory.Faker('country')
    imdb_rating = factory.Faker('pyfloat', left_digits=1, right_digits=1, positive=True, max_value=10)
    url_poster = factory.Faker('url')
    is_full_record = False

    @factory.post_generation
    def genres(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            # A list of genres was passed in, use them
            for genre in extracted:
                self.genres.add(genre)
        else:
            # Create a default genre if none is provided
            genre = GenreFactory()
            self.genres.add(genre)


class MovieNightFactory(DjangoModelFactory):
    class Meta:
        model = MovieNight

    movie = factory.SubFactory(MovieFactory)
    start_time = factory.Faker('future_datetime')
    creator = factory.SubFactory(UserFactory)


class MovieNightInvitationFactory(DjangoModelFactory):
    class Meta:
        model = MovieNightInvitation

    movie_night = factory.SubFactory(MovieNightFactory)
    invitee = factory.SubFactory(UserFactory)
    attendance_confirmed = False
    is_attending = False


"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""