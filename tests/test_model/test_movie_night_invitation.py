"""
Test cases for MoviNightInvitation model.
"""

import pytest
from tests.factories import MovieNightInvitationFactory
from movies.models import MovieNightInvitation
from tests.factories import UserFactory, MovieNightFactory
from django.db.utils import IntegrityError
from django.utils import timezone

@pytest.mark.django_db
class TestMovieNightInvitation:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.invitation = MovieNightInvitationFactory()

    def test_movienight_invitation_creation(self):
        
        assert isinstance(self.invitation, MovieNightInvitation)
        assert self.invitation.movie_night is not None
        assert self.invitation.invitee is not None
        assert UserFactory not in self.invitation.attendance_confirmed

    def test_unique_together_constraint(self):
        """
        Test that the 'unique_together' constraint on ('invitee', 'movie_night') is enforced.
        """
        # Create a user and a movie night
        user = ()
        movie_night = MovieNightFactory()

        # Create a valid MovieNightInvitation
        MovieNightInvitationFactory(invitee=user, movie_night=movie_night)

        # Try to create a second invitation with the same invitee and movie_night
        with pytest.raises(IntegrityError):
            MovieNightInvitation.objects.create(invitee=user, movie_night=movie_night)

    def test_movie_night_invitation_invited_time(self):
        """
        Test that the invited_time is set to the current time when the invitation is created.
        """
        user = UserFactory()
        movie_night = MovieNightFactory()

        # Create an invitation
        invitation = MovieNightInvitationFactory(movie_night=movie_night, invitee=user)

        # Assert that invited_time is close to the current time
        now = timezone.now()
        assert invitation.invited_time <= now
        assert (now - invitation.invited_time).total_seconds() < 1  # Time difference should be very small
"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""