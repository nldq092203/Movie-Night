
"""
Test Cases for serialization and deserialization SearchTermSerializer.
"""
import pytest
from rest_framework.exceptions import ValidationError
from movies.models import SearchTerm
from movies.serializers import SearchTermSerializer

@pytest.mark.django_db
class TestSearchTermSerializer:
    def test_search_term_serializer_serialization(self):
        """
        Test that the SearchTermSerializer correctly serializes the search term.
        """
        search_term = SearchTerm.objects.create(term="Inception")

        serializer = SearchTermSerializer(instance=search_term)
        data = serializer.data

        assert data['term'] == "inception"
        assert "last_search" in data  


    def test_search_term_serializer_deserialization(self):
        """
        Test that the SearchTermSerializer correctly deserializes input data and converts the term to lowercase.
        """
        data = {
            "term": "Inception"
        }

        # Deserialize the data
        serializer = SearchTermSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

        search_term = serializer.save()
        assert search_term.term == "inception"

    def test_search_term_serializer_invalid_data(self):
        """
        Test that the SearchTermSerializer handles invalid input data.
        """
        data = {}

        serializer = SearchTermSerializer(data=data)

        # Serializer should not be valid due to missing term
        assert not serializer.is_valid()
        assert "term" in serializer.errors

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""