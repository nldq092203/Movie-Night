import pytest
from django.urls import reverse
from rest_framework import status
from movies.models import Genre
from tests.factories import GenreFactory

@pytest.mark.django_db
class TestGenreView:
    
    def test_genre_list(self, any_client):
        """
        Test that the genre list is retrieved successfully.
        """
        # Create sample genres
        GenreFactory(name="Action")
        GenreFactory(name="Comedy")
        
        # Make a GET request to the genre list view
        url = reverse('genre_list')  # Ensure this is the correct URL name for the genre list
        response = any_client.get(url)
        
        # Assert that the response is 200 OK and that the correct genres are returned
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2
        assert response.data["results"][0]['name'] == "action"
        assert response.data["results"][1]['name'] == "comedy"

    def test_genre_list_empty(self, any_client):
        """
        Test that an empty genre list is handled properly.
        """
        # No genres in the database
        
        # Make a GET request to the genre list view
        url = reverse('genre_list')
        response = any_client.get(url)
        
        # Assert that the response is 200 OK and the list is empty
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 0


@pytest.mark.django_db
class TestGenreDetailView:
    
    def test_genre_detail(self, any_client):
        """
        Test that a genre detail is retrieved successfully.
        """
        # Create a sample genre
        genre = GenreFactory(name="Action")
        
        # Make a GET request to the genre detail view
        url = reverse('genre_detail', kwargs={'pk': genre.pk})
        response = any_client.get(url)
        
       # Assert that the response is 200 OK and that the correct genre is returned
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == "action"

    def test_genre_detail_nonexistent(self, any_client):
        """
        Test that a non-existent genre detail returns 404.
        """
        # Make a GET request to a non-existent genre
        url = reverse('genre_detail', kwargs={'pk': 9999})  # Assuming 9999 doesn't exist
        response = any_client.get(url)
        
        # Assert that the response is 404 Not Found
        assert response.status_code == status.HTTP_404_NOT_FOUND