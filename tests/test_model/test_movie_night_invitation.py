"""
Test cases for MoviNightInvitation model.
"""

import pytest
from tests.factories import MovieNightInvitationFactory
from movies.models import MovieNightInvitation
from tests.factories import UserFactory, MovieNightFactory
from django.db.utils import IntegrityError
from django.utils import timezone
from unittest.mock import patch

@pytest.mark.django_db
@patch('movies.tasks.send_invitation.delay')
class TestMovieNightInvitation:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.invitation = MovieNightInvitationFactory()
    def test_movienight_invitation_creation(self, mock_send_invitation):
        
        assert isinstance(self.invitation, MovieNightInvitation)
        assert self.invitation.movie_night is not None
        assert self.invitation.invitee is not None
        assert not self.invitation.attendance_confirmed

    def test_unique_together_constraint(self, mock_send_invitation):
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