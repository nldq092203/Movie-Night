from django.urls import path
from apps.movies.views import (
    MovieSearchView,
    MovieSearchWaitView,
    MovieSearchResultsView,
    MovieDetailView, 
    MovieView, 
    MyMovieNightView,
    ParticipatingMovieNightView,
    MovieNightDetailView,
    MyMovieNightInvitationView,
    MovieNightInvitationCreateView,
    InvitedMovieNightView,
    MovieNightInvitationDetailView,
    GenreView,
    GenreDetailView,
    MyMovieNightForAMovieView
)

from django.views.decorators.cache import cache_page

urlpatterns = [
    path("movies/search/", MovieSearchView.as_view(), name="movie_search"),
    path("movies/search-wait/<uuid:result_uuid>/", MovieSearchWaitView.as_view(), name="movie_search_wait"),
    path("movies/search-results/", MovieSearchResultsView.as_view(), name="movie_search_results"),
    path("movies/<str:pk>/my-movie-nights/", MyMovieNightForAMovieView.as_view(), name="my_movienight"),
    path("movies/<str:pk>/", MovieDetailView.as_view(), name="movie_detail"),
    path("movies/", cache_page(60*5)(MovieView.as_view()), name="movie_list"),
    path("my-movie-nights/", MyMovieNightView.as_view(), name="my_movienight_list"),
    path("participating-movie-nights/", ParticipatingMovieNightView.as_view(), name="movienight_list"),
    path("movie-nights/invited/", InvitedMovieNightView.as_view(), name="invited_movienight_list"),
    path('movie-nights/<str:pk>/', MovieNightDetailView.as_view(), name="movienight_detail"),
    path('movie-nights/<str:pk>/invite/', MovieNightInvitationCreateView.as_view(), name="movienight_invitation_create"),
    path('movienight-invitations/', MyMovieNightInvitationView.as_view(), name="movienight_invitation_list"),
    path('movienight-invitations/<str:pk>/', MovieNightInvitationDetailView.as_view(), name="movienight_invitation_detail"),
    path('genres/', GenreView.as_view(), name="genre_list"),
    path('genres/<str:pk>/', GenreDetailView.as_view(), name="genre_detail"),
]

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""