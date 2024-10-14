"""
Defines factories for generating test data corresponding to models.
"""
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from movies.models import UserProfile, Genre, SearchTerm, Movie, MovieNight, MovieNightInvitation
from notifications.models import Notification
from django.utils import timezone 
from chat.models import ChatGroup, Membership, GroupMessage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.contenttypes.models import ContentType
import shortuuid


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

from django.contrib.contenttypes.models import ContentType

class NotificationFactory(DjangoModelFactory):
    """
    Factory for the Notification model. This factory helps create Notification instances
    for testing purposes, linking notifications to users, content objects, and ensuring
    valid notification types.
    """
    class Meta:
        model = Notification

    recipient = factory.SubFactory(UserFactory)
    sender = factory.SubFactory(UserFactory)
    notification_type = "INV"
    content_object = factory.SubFactory(MovieNightFactory)

    @factory.lazy_attribute
    def content_type(self):
        return ContentType.objects.get_for_model(self.content_object)


class ChatGroupFactory(DjangoModelFactory):
    """
    Factory for the ChatGroup model. This factory helps create ChatGroup instances
    for testing purposes. It generates unique group names, assigns a sequence-based
    chat group name, and allows flexibility in setting group privacy.
    """
    class Meta:
        model = ChatGroup

    group_name = factory.LazyFunction(lambda: f"group-{shortuuid.uuid()}")
    groupchat_name = factory.Sequence(lambda n: f'Chat Group {n}')
    is_private = factory.Faker('boolean')

    @factory.post_generation
    def admin(self, create, extracted, **kwargs):
        """
        Post-generation hook for adding admin users to the ChatGroup. If an admin is not provided,
        it defaults to adding a single user from UserFactory.
        
        Args:
            create: Boolean flag indicating if the instance was actually created.
            extracted: List of admin users, if provided.
        """
        if not create:
            return
        if extracted:
            for admin_user in extracted:
                self.admin.add(admin_user)  # Add each provided admin to the group
        else:
            self.admin.add(UserFactory())  # Add a default admin if none were provided

class MembershipFactory(DjangoModelFactory):
    """
    Factory for the Membership model. This factory creates instances representing the
    relationship between a user and a chat group, with fields for nickname and the timestamp
    of when the user last read messages in the group.
    """
    class Meta:
        model = Membership

    user = factory.SubFactory(UserFactory)  # Link to a User instance from UserFactory
    chat_group = factory.SubFactory(ChatGroupFactory)  # Link to a ChatGroup instance
    nickname = factory.Faker('first_name')  # Generate a random first name as nickname
    last_read_at = factory.LazyFunction(timezone.now)  # Set current time as last read timestamp

class GroupMessageFactory(DjangoModelFactory):
    """
    Factory for the GroupMessage model. This factory facilitates the creation of
    messages within chat groups, including optional file attachments and random message bodies.
    """
    class Meta:
        model = GroupMessage

    group = factory.SubFactory(ChatGroupFactory)  # Associate with a ChatGroup
    author = factory.SubFactory(UserFactory)  # Associate with a User (message author)
    body = factory.Faker('sentence')  # Generate a random sentence for message content

    @factory.post_generation
    def file(self, create, extracted, **kwargs):
        """
        Post-generation hook for adding an optional file attachment to the message.
        If no file is provided, a default image file is created.
        
        Args:
            create: Boolean flag indicating if the instance was actually created.
            extracted: Custom file, if provided.
        """
        if not create:
            return
        if extracted:
            self.file = extracted  # Use the provided file

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""