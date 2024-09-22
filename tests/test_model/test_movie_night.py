import pytest
from tests.factories import MovieNightFactory
from movies.models import MovieNight


@pytest.mark.django_db
class TestMovieNight:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.movienight = MovieNightFactory()

    def test_movienight_creation(self):
        assert isinstance(self.movienight, MovieNight)
        assert self.movienight.movie is not None
        assert self.movienight.creator is not None

