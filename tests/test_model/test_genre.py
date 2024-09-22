"""
Test cases for Genre model. Verify genre creation with unique name.
"""
import pytest
from movies.models import Genre
from django.db import IntegrityError
from tests.factories import GenreFactory

@pytest.mark.django_db
class TestGenre: 

    @pytest.fixture(autouse=True)
    def setup(self):
        self.genre = GenreFactory(name="Comedy")
    
    def test_genre_creation(self):
        assert self.genre.name == 'comedy'
        assert str(self.genre) == 'comedy'

    def test_genre_unique_name(self):
        with pytest.raises(IntegrityError):
            GenreFactory(name='Comedy')


"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""