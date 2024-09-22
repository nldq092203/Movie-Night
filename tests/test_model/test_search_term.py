"""
Test cases for SearchTerm model. Verify searchterm creation with unique term.
"""
import pytest
from django.db import IntegrityError
from tests.factories import SearchTermFactory

@pytest.mark.django_db
class TestSearchTerm: 

    @pytest.fixture(autouse=True)
    def setup(self):
        self.term = SearchTermFactory(term="Comedy")
    
    def test_search_term_creation(self):
        assert self.term.term == 'comedy'
        assert str(self.term) == 'comedy'

    def test_search_term_unique_name(self):
        with pytest.raises(IntegrityError):
            SearchTermFactory(term='Comedy')


"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""