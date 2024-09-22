"""
Test cases for MoviNightInvitation model.
"""

import pytest
from tests.factories import MovieNightInvitationFactory
from movies.models import MovieNightInvitation

@pytest.mark.django_db
class TestMovieNightInvitation:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.invitation = MovieNightInvitationFactory()

    def test_movienight_invitation_creation(self):
        
        assert isinstance(self.invitation, MovieNightInvitation)
        assert self.invitation.movie_night is not None
        assert self.invitation.invitee is not None
        assert not self.invitation.attendance_confirmed

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""