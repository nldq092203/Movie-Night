"""
Functions to interact with the OMDb API and manage movie-related data in the local database.
"""

import logging 
import re
from apps.movies.models import Genre, SearchTerm, Movie
from apps.omdb.django_client import get_client_from_settings
from apps.movies.serializers import MovieDetailSerializer

from datetime import timedelta

from django.utils.timezone import now

logger = logging.getLogger(__name__)

def get_or_create_genres(genre_names):
    for genre_name in genre_names:
        genre, created = Genre.get_or_create(name=genre_name)
        yield genre

def fill_movie_details(movie):
    """
    Fetch a movie's full details from OMDb. Then, save it to the DB. If the movie already has a `full_record` this does
    nothing, so it's safe to call with any `Movie`.
    """
    if movie.is_full_record:
        logger.warning(
            "'%s' is already a full record.",
            movie.title,
        )
        return
    omdb_client = get_client_from_settings()
    try:
        movie_details = omdb_client.get_by_imdb_id(movie.imdb_id)
    except Exception as e:
        logger.error(str(e))

    serializer = MovieDetailSerializer(instance=movie, data=movie_details.to_dict())

    if serializer.is_valid():
        serializer.is_full_record = True
        serializer.id = movie.id
        serializer.save()
    else:
        logger.error("Failed to update movie details: %s", serializer.errors)
    

def search_and_save(search):
    """
    Perform a search for search_term against the API, but only if it hasn't been searched in the past 30 days. Save
    each result to the local DB as a partial record.
    """
    # Replace multiple spaces with single spaces, and lowercase the search
    normalized_search_term = re.sub(r"\s+", " ", search.lower())

    search_term, created = SearchTerm.objects.get_or_create(term=normalized_search_term)

    if not created and (search_term.last_search > now() - timedelta(days=30)):
        # Don't search as it has been searched in 30 days
        logger.warning(
            "Search for '%s' was performed in the past 30 days so not searching from omdb_api again.",
            normalized_search_term,
        )
        return

    omdb_client = get_client_from_settings()

    for omdb_movie in omdb_client.search(search):
        logger.info("Saving movie: '%s' / '%s'", omdb_movie.title, omdb_movie.imdb_id)
        movie, created = Movie.objects.get_or_create(
            imdb_id=omdb_movie.imdb_id,
            defaults={
                "title": omdb_movie.title,  # Set attributes in defaults if a new Movie is created
                "year": omdb_movie.year,
                "url_poster": omdb_movie.url_poster,           
            },
        )

        if created:
            logger.info("Movie created: '%s'", movie.title)
            # fill_movie_details(movie)

    search_term.save()

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""