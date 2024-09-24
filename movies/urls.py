from django.urls import path
from movies.views import (
    movie_search, 
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
    ProfileView
)

urlpatterns = [
    path("movies/search/", movie_search, name="movie_search"),
    path("movies/<str:pk>/", MovieDetailView.as_view(), name="movie_detail"),
    path("movies/", MovieView.as_view(), name="movie_list"),
    path("my-movie-nights/", MyMovieNightView.as_view(), name="my_movienight_list"),
    path("movie-nights/", ParticipatingMovieNightView.as_view(), name="movienight_list"),
    path("movie-nights/invited/", InvitedMovieNightView.as_view(), name="invited_movienight_list"),
    path('movie-nights/<str:pk>/', MovieNightDetailView.as_view(), name="movienight_detail"),
    path('movie-nights/<str:pk>/invite/', MovieNightInvitationCreateView.as_view(), name="movienight_invitation_create"),
    path('movienight-invitations/', MyMovieNightInvitationView.as_view(), name="movienight_invitation_list"),
    path('movienight-invitations/<str:pk>/', MovieNightInvitationDetailView.as_view(), name="movienight_invitation_detail"),
    path('genres/', GenreView.as_view(), name="genre_list"),
    path('genres/<str:pk>/', GenreDetailView.as_view(), name="genre_detail"),
    path('profiles/<str:email>/', ProfileView.as_view(), name='profile_by_email'),

]

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""