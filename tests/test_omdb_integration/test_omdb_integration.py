"""
Unit tests for the `fill_movie_details` and `search_and_save` functions in `omdb_integration`.

Tests include:
1. Handling movies already marked as fully recorded.
2. Fetching and updating movie details from OMDb, including validation.
3. Skipping recent searches and creating new movies from OMDb results.
4. Correct logging behavior in various scenarios.

Mocks are used for the OMDb client, database operations, and logging to isolate function behavior.
"""
import pytest
from tests.factories import MovieFactory, SearchTermFactory
from movies.omdb_integration import fill_movie_details, search_and_save
from django.utils.timezone import now

@pytest.mark.django_db
class TestFillMovieDetails:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.movie = MovieFactory(is_full_record=False, title="Inception", imdb_id="tt1375666")

    def test_fill_movie_details_already_full_record(self, mocker):
        """
        Test the logger in fill_movie_details function to verify whether the logger displayed the
        correct message when movie has been fully recorded
        """

        self.movie.is_full_record = True
        self.movie.save()

        mock_logger = mocker.patch('movies.omdb_integration.logger')

        mock_omdb_client = mocker.Mock()
        mocker.patch('movies.omdb_integration.get_client_from_settings', return_value=mock_omdb_client)
        fill_movie_details(self.movie)

        # Assert: Ensure the logger was called with the expected message
        mock_logger.warning.assert_called_once_with(
            "'%s' is already a full record.",
            self.movie.title,  
        )
        # Ensure that the OMDb client was never called
        mock_omdb_client.assert_not_called()

        # Ensure is_full_record is still True
        assert self.movie.is_full_record is True
    
    def test_fill_movie_details_success(self, mocker):
        """
        1. Test the OMDB client to that the get_by_imdb_id method of the OMDb client 
        was called exactly once with the correct IMDb ID.
        2. Test the Serializer to verify that the function attempted to
        validate the fetched movie data before saving it 
        and confirm that the function proceeded to save the validated data to update the Movie instance
        """
        
        # Mock the OMDb client
        mock_omdb_client = mocker.Mock()
        mocker.patch('movies.omdb_integration.get_client_from_settings', return_value=mock_omdb_client)

        # Mock the serializer
        mock_serializer = mocker.Mock()
        mock_serializer.is_valid.return_value = True
        mocker.patch('movies.omdb_integration.MovieDetailSerializer', return_value=mock_serializer)

        fill_movie_details(self.movie)

        # Assert: Verify the expected behavior
        mock_omdb_client.get_by_imdb_id.assert_called_once_with("tt1375666")
        mock_serializer.is_valid.assert_called_once()
        mock_serializer.save.assert_called_once()
    
    def test_fill_movie_details_serializer_invalid(self, mocker):
        """
        Test the Serializer to verify that if data is invalid, save method will not be called
        and the logger displayed error.
        """
        mock_omdb_client = mocker.Mock()
        mocker.patch('movies.omdb_integration.get_client_from_settings', return_value=mock_omdb_client)

        # Mock the serializer with invalid data
        mock_serializer = mocker.Mock()
        mock_serializer.is_valid.return_value = False
        mock_serializer.errors = {'title': ['This field is required.']}
        mocker.patch('movies.omdb_integration.MovieDetailSerializer', return_value=mock_serializer)

        mock_logger = mocker.patch('movies.omdb_integration.logger')

        fill_movie_details(self.movie)

        # Assert: Verify that the error is logged
        assert self.movie.is_full_record is False
        mock_serializer.is_valid.assert_called_once()
        mock_serializer.save.assert_not_called()
        mock_logger.error.assert_called_once_with(
            "Failed to update movie details: %s", mock_serializer.errors
        )

class TestSearchAndSave:
    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        self.search_term = "Test  term"

        self.mock_search_get_or_create = mocker.patch(
            "movies.models.SearchTerm.objects.get_or_create"
        )

        self.mock_omdb_client = mocker.patch(
            "movies.omdb_integration.get_client_from_settings"
        )

        self.mock_logger = mocker.patch("movies.omdb_integration.logger")
        
        self.mock_movie_get_or_create = mocker.patch("movies.omdb_integration.Movie.objects.get_or_create")

    def test_search_recently_performed(self, mocker):
        """
        Test that if a search term has been searched in the past 30 days, no new search is performed.
        """

        self.mock_search_get_or_create.return_value = (mocker.Mock(term=self.search_term, last_search=now()), False)

        search_and_save(self.search_term)
        # Asserts
        # Logger warning displayed
        self.mock_logger.warning.assert_any_call(
            "Search for '%s' was performed in the past 30 days so not searching from omdb_api again.",
            "test term",
        )
        # No omdb_client was called
        self.mock_omdb_client.assert_not_called() 

    def test_new_search_term(self, mocker):
        """
        Test that a new search is performed when the term hasn't been searched recently.
        New movies listed in search are created
        """

        self.mock_search_get_or_create.return_value = (mocker.Mock(term=self.search_term, last_search=now()), True)

        self.mock_omdb_client.return_value.search.return_value = [
            mocker.Mock(imdb_id="tt1375666", title="Inception", year=2010, url_poster="http://example.com/inception.jpg"),
        ]
        # Mock a new movie created
        self.mock_movie_get_or_create.return_value = (mocker.Mock(imdb_id="tt1375666", title="Inception", year=2010, url_poster="http://example.com/inception.jpg"), True)

        search_and_save(self.search_term)

        # Assert that Omdb_client was called
        self.mock_omdb_client.assert_called_once()
        # Assert that search was called once
        self.mock_omdb_client.return_value.search.assert_called_once_with(self.search_term)
        # Assert that logger info displayed
        self.mock_logger.info.assert_any_call("Saving movie: '%s' / '%s'", "Inception", "tt1375666")


        # Assert that the movie was created
        self.mock_movie_get_or_create.assert_called_once_with(
            imdb_id="tt1375666",
            defaults={
                "title": "Inception",
                "year": 2010,
                "url_poster": "http://example.com/inception.jpg"
            },
        )
        # Assert the logger logged the creation of the movie
        self.mock_logger.info.assert_any_call("Movie created: '%s'", "Inception")

    def test_existing_movie(self, mocker):
            """
            Test that if a movie already exists, it is not created again.
            """

            self.mock_search_get_or_create.return_value = (mocker.Mock(term=self.search_term, last_search=now()), True)

            self.mock_omdb_client.return_value.search.return_value = [
                mocker.Mock(imdb_id="tt1375666", title="Inception", year=2010, url_poster="http://example.com/inception.jpg"),
            ]
            # Mock a new movie created
            self.mock_movie_get_or_create.return_value = (mocker.Mock(imdb_id="tt1375666", title="Inception", year=2010, url_poster="http://example.com/inception.jpg"), False)

            search_and_save(self.search_term)

            # Assert no log for movie creation (since movie was not created)
            for call in self.mock_logger.info.call_args_list:
                assert call != mocker.call("Movie created: '%s'", "Inception")
    

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""