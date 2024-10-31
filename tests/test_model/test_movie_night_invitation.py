"""
Test cases for MoviNightInvitation model.
"""

import pytest
from tests.factories import MovieNightInvitationFactory
from movies.models import MovieNightInvitation
from tests.factories import UserFactory, MovieNightFactory
from django.db.utils import IntegrityError
from django.utils import timezone
from django.db.models.signals import post_save
from movies.signals import send_invitation

@pytest.mark.django_db
class TestMovieNightInvitation:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.invitation = MovieNightInvitationFactory()
        post_save.disconnect(send_invitation, sender=MovieNightInvitation)

    def tearDown(self):
        # Reconnect the signal after tests
        post_save.connect(send_invitation, sender=MovieNightInvitation)

    def test_movienight_invitation_creation(self):
        
        assert isinstance(self.invitation, MovieNightInvitation)
        assert self.invitation.movie_night is not None
        assert self.invitation.invitee is not None
        assert not self.invitation.attendance_confirmed

    def test_unique_together_constraint(self):
        """
        Test that the 'unique_together' constraint on ('invitee', 'movie_night') is enforced.
        """
        # Create a user and a movie night
        user = UserFactory()
        movie_night = MovieNightFactory()

        # Create a valid MovieNightInvitation
        MovieNightInvitationFactory(invitee=user, movie_night=movie_night)

        # Try to create a second invitation with the same invitee and movie_night
        with pytest.raises(IntegrityError):
            MovieNightInvitation.objects.create(invitee=user, movie_night=movie_night)

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""