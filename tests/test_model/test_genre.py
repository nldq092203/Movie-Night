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
        assert self.genre.name == 'Comedy'
        assert str(self.genre) == 'Comedy'

    def test_genre_unique_name(self):
        with pytest.raises(IntegrityError):
            GenreFactory(name='Comedy')
