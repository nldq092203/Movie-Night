from django.urls import path
from movies.views import movie_search, MovieDetailView

urlpatterns = [
    path("movie-search/", movie_search, name="movie_search"),
    path("movies/<str:pk>", MovieDetailView.as_view(), name="movie_detail")
]