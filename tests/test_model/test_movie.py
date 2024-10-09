"""
Test cases for Movie model. Verify movie creation with unique imdb_id
"""

import pytest
from movies.models import Movie, Genre
from django.db import IntegrityError
from tests.factories import MovieFactory

@pytest.mark.django_db
class TestMovie:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.movie = MovieFactory(imdb_id='tt1375666', title="Inception", year=2010)
    def test_movie_creation(self):

        assert self.movie.title == 'Inception'
        assert self.movie.genres.count() == 1
        assert str(self.movie) == 'Inception (2010)'

    
    def test_movie_unique_imdb_id(self):
        with pytest.raises(IntegrityError):
            MovieFactory( imdb_id='tt1375666')

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""