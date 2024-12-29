"""
This module defines the views (logic business)

It includes:
- A POST-based movie search function using search terms to query the OMDB API and local database.
- A detail view to retrieve and update complete movie information.
- A generic list view for filtering movies based on various criteria like year, runtime, title, and genres.

"""
from rest_framework.response import Response
from rest_framework.generics import (
    RetrieveAPIView, 
    ListAPIView, 
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    CreateAPIView,
    )                     
from apps.movies.serializers import (
    MovieSerializer, 
    MovieDetailSerializer, 
    MovieNightSerializer, 
    MovieNightInvitationSerializer,
    MovieNightDetailSerializer,
    GenreSerializer, 
    MovieSearchSerializer,
    )
from apps.movies.models import Movie, MovieNight, MovieNightInvitation, Genre
from django.contrib.auth import get_user_model
from apps.movies.tasks import search_and_save
from apps.movies.omdb_integration import fill_movie_details
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator
from rest_framework import status

from apps.movies.filters import (
    MovieFilterSet, 
    ParticipatingMovieNightFilterSet, 
    MyMovieNightFilterSet, 
    MovieNightInvitationFilterSet
    )
from apps.movies.permissions import MovieNightDetailPermission, IsInvitee
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied
from celery.exceptions import TimeoutError
from django.shortcuts import redirect
import urllib.parse
from django.urls import reverse
from movienight.celery import app
from rest_framework.views import APIView
from celery.result import AsyncResult

from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

User = get_user_model()

############### Movie ###################
@extend_schema(
    request=MovieSearchSerializer,
    responses={
        302: OpenApiResponse(
            description="Redirected to either the 'wait' page or the results page depending on task completion.",
            response=OpenApiTypes.STR
        ),
        400: OpenApiResponse(
            description="Invalid input data. The request failed validation. The response contains error details.",
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    'Invalid Input',
                    value={
                        "term": ["This field is required."]
                    },
                    response_only=True  # Set this as response-only example
                )
            ]
        ),
        500: OpenApiResponse(
            description="Internal Server Error. An error occurred while processing the request. This typically happens due to Celery issues or other server problems.",
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    'Server Error',
                    value={
                        "error": "An error occurred while processing your request."
                    },
                    response_only=True 
                )
            ]
        ),
    },
    description="Search for movies based on a search term. This view initiates a background task using Celery to fetch results, and returns a 302 redirect based on task completion.",
)
class MovieSearchView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [] 

    def post(self, request):
        """
        Search for movies based on a search term.
        - Initiates a background task using Celery.
        - Returns a 302 (Found) and redirects to a "wait" page while the task is processed.
        - On completion, redirects to the results page.
        """

        # Use the serializer to validate the input data
        serializer = MovieSearchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        term = serializer.validated_data['term']

        try:
            # Dispatch the Celery task asynchronously
            res = search_and_save.delay(term)
        except Exception as e:
            return Response(
                {"error": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            # Check if the task completes in 120 seconds, else redirect to "wait"
            res.get(timeout=120)
        except TimeoutError:
            # Redirect to a wait page if the task is still running
            return redirect(
                reverse("movie_search_wait", args=(res.id,))
                + "?search_term="
                + urllib.parse.quote_plus(term)
            )

        # Redirect to the search results page if the task is completed quickly
        return redirect(
            reverse("movie_search_results")
            + "?search_term="
            + urllib.parse.quote_plus(term),
            permanent=False,
        )

@extend_schema(
    parameters=[
        OpenApiParameter(name='search_term', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
    ],
    responses={
        200: OpenApiTypes.OBJECT,
        302: OpenApiTypes.STR,
        500: OpenApiTypes.OBJECT,
    },
    description="Handle pending search results from a Celery task.",
)
class MovieSearchWaitView(APIView):
    """
    API view to handle pending search results from a Celery task.
    """
    permission_classes = [AllowAny]
    authentication_classes = [] 
    
    def get(self, request, result_uuid):
        term = request.query_params.get("search_term", "").strip()
        res = AsyncResult(result_uuid)

        try:
            res.get(timeout=-1)
        except TimeoutError:
            return Response(
                {"message": "Task pending, please refresh."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return redirect(
            reverse("movie_search_results")
            + "?search_term="
            + urllib.parse.quote_plus(term)
        )
    
class MovieSearchResultsView(APIView):
    """
    API view to return paginated search results based on the search term.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        parameters=[
            OpenApiParameter(name='search_term', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
        ],
        responses={200: MovieSerializer(many=True)},
        description="Return paginated search results based on the search term.",
    )
    def get(self, request, *args, **kwargs):
        # Retrieve and validate the search term
        term = request.query_params.get("search_term", "").strip()
        page = request.query_params.get("page", 1)

        if not term:
            return Response(
                {"error": "Search term is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate a cache key for the search term and page
        cache_key = f"search_results:{term}:page:{page}"
        cached_results = cache.get(cache_key)
        if cached_results:
            return Response(cached_results)

        # Fetch results from the database
        results = Movie.objects.filter(title__icontains=term)
        paginator = PageNumberPagination()
        paginated_results = paginator.paginate_queryset(results, request, view=self)

        # Serialize and cache paginated results for the specific page
        serialized_results = MovieSerializer(paginated_results, many=True).data
        paginated_response = paginator.get_paginated_response(serialized_results).data

        cache.set(cache_key, paginated_response, timeout=3600)
        return Response(paginated_response)
        
class MovieDetailView(RetrieveAPIView):
    """
    Retrieve and update detailed information for a single movie.

    This view:
    - Fetches a movie by its primary key (IMDB ID).
    - Calls the OMDB API to update movie details if not already fully recorded.
    - Returns the detailed movie data.

    Returns:
    - A response containing the movie details or an error if the movie is not found or another issue occurs.
    """
    queryset = Movie.objects.all()
    serializer_class = MovieDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Movie.objects.none()  # Return empty queryset for schema generation
        return Movie.objects.all()

    def retrieve(self, request, *args, **kwargs):
        movie_detail = self.get_object()
        try:
            fill_movie_details(movie_detail)

        except Exception as e:
            logger.error(f"Error fetching movie details: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        serializer = self.get_serializer(movie_detail)
        return Response(serializer.data)
    



class CustomPaginator(Paginator):
    @property
    def count(self):
        """
        Override the count property to cache the result of COUNT(*).
        If no cached value exists, it falls back to the default behavior and caches the result.
        """
        cache_key = "movies_total_count"
        total_count = cache.get(cache_key)
        
        if total_count is None:
            # Call the original count logic from the default paginator
            total_count = super().count  # This triggers the COUNT(*) query

            cache.set(cache_key, total_count,timeout=60*20)  
        
        return total_count

class CustomPageNumberPagination(PageNumberPagination):
    django_paginator_class = CustomPaginator

class MovieView(ListAPIView):
    """
    A list view to filter movies based on criteria such as genres, country, year, and runtime.

    This view:
    - Applies filters provided via query parameters.
    - Supports ordering by year, runtime, and title.

    Returns: a list of filtered movies.
    """
    filterset_class = MovieFilterSet
    ordering_fields = ['year','runtime_minutes', 'title']
    queryset = Movie.objects.all()
    permission_classes = [AllowAny]
    authentication_classes = [] 
    serializer_class = MovieSerializer
    pagination_class = CustomPageNumberPagination


############ MovieNight ##############
class MyMovieNightForAMovieView(ListCreateAPIView):

    """
    View for listing and creating MovieNight instances that are created by the currently authenticated user for a specific movie.

    - GET: Lists movie nights created by the current user for a movie pk.
    - POST: Allows the current user to create a new movie night for a movie.
    """
    serializer_class = MovieNightSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = MyMovieNightFilterSet
    ordering_fields = ["start_time", "movie"]

    def get_queryset(self):
        # Get the movie ID from the URL parameters
        movie_id = self.kwargs.get("pk")
        # Return movie nights for the current user filtered by the specified movie
        return MovieNight.objects.filter(movie=movie_id, creator=self.request.user)

    def get_serializer(self, *args, **kwargs):
        # Get the serializer class
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()

        if self.request.method in ['POST', 'PUT', 'PATCH']:
            # For POST, PUT, PATCH methods, add 'movie' to the data before validation
            data = kwargs.get('data', {})
            if isinstance(data, list):
                # Handle list input for bulk operations
                for item in data:
                    item['movie'] = self.kwargs.get('pk')
            else:
                data['movie'] = self.kwargs.get('pk')
            kwargs['data'] = data

        return serializer_class(*args, **kwargs)

    def perform_create(self, serializer):
        """
        Automatically set the creator of the movie night to the current authenticated user.
        """
        # Save with the creator
        serializer.save(creator=self.request.user)

class MyMovieNightView(ListCreateAPIView):
    """
    View for listing and creating MovieNight instances that are created by the currently authenticated user.

    - GET: Lists movie nights created by the current user.
    - POST: Allows the current user to create a new movie night.
    """
    serializer_class = MovieNightSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = MyMovieNightFilterSet
    ordering_fields = ["start_time", "movie"]

    def get_queryset(self):
        """
        Return movie nights created by the currently authenticated user.
        """
        if getattr(self, 'swagger_fake_view', False):
            return MovieNight.objects.none()
        return MovieNight.objects.filter(creator=self.request.user)


    def perform_create(self, serializer):
        """
        Automatically set the creator of the movie night to the current authenticated user during creation.
        """
        # Ensure start_notification_before is set to a default value (e.g., 0) if not provided
        if 'start_notification_before' not in serializer.validated_data:
            serializer.validated_data['start_notification_before'] = 0
            
        serializer.save(creator=self.request.user)

class ParticipatingMovieNightView(ListAPIView):
    """
    View for listing all MovieNight instances where the authenticated user
    is either the creator or a confirmed attendance invitee, with detailed info.
    """
    serializer_class = MovieNightDetailSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ParticipatingMovieNightFilterSet
    ordering_fields = ["start_time", "creator"]

    def get_queryset(self):
        """
        Return movie nights where the user is either the creator or a confirmed attendance invitee.
        """
        if getattr(self, 'swagger_fake_view', False):
            return MovieNight.objects.none()

        user = self.request.user

        # Filter for the user being either the creator or a confirmed invitee
        queryset = MovieNight.objects.filter(
            Q(creator=user) | 
            Q(invites__invitee=user, invites__attendance_confirmed=True, invites__is_attending=True)
        ).distinct()  # Use distinct to avoid duplicates

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Serialize all movie night instances using MovieNightDetailSerializer
        movie_nights_data = MovieNightDetailSerializer(queryset, many=True).data

        # Loop through each movie night and add invitation status and movie details
        for movie_night_data in movie_nights_data:
            movie_night_instance = MovieNight.objects.get(id=movie_night_data['id'])

            # Fetch the movie details
            movie = movie_night_instance.movie
            movie_data = {
                "title": movie.title if movie else None,
                "runtime_minutes": movie.runtime_minutes if movie else None,
            }

            # Add invitation status and movie data to each movie night entry
            movie_night_data.update({

                "movie": movie_data
            })

        return Response(movie_nights_data, status=status.HTTP_200_OK)
    
class InvitedMovieNightView(ListAPIView):
    """
    View for listing all MovieNight instances where the authenticated user has been invited.
    """
    serializer_class = MovieNightSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ParticipatingMovieNightFilterSet
    ordering_fields = ["start_time", "creator"]

    def get_queryset(self):
        """
        Return movie nights where the user has been invited.
        """
        if getattr(self, 'swagger_fake_view', False):
            return MovieNight.objects.none()
        user = self.request.user

        return MovieNight.objects.filter(invites__invitee=user)


class MovieNightDetailView(RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, or deleting a specific movie night.

    This view supports:
    - **Retrieve**: Get the details of a movie night by its ID.
    - **Update**: Modify the details of a movie night (only allowed for certain users).
    - **Delete**: Remove a movie night (only allowed for certain users).
    
    Additionally, when retrieving a movie night, the API returns the current user's invitation status 
    if the user was invited to the movie night.

    Permission:
    - The user must be authenticated.
    - Only users with appropriate permissions can update or delete the movie night.

    Invitation Status Fields:
    - **invitation_id**: The ID of the invitation (if the user is invited).
    - **is_invited**: Whether the user is invited to the movie night.
    - **attendance_confirmed**: Whether the user has confirmed their attendance.
    - **is_attending**: Whether the user is attending the movie night.

    Raises:
    - `PermissionDenied`: If the user does not have permission to perform the requested operation.
    """
    serializer_class = MovieNightDetailSerializer
    permission_classes = [IsAuthenticated, MovieNightDetailPermission]
    queryset = MovieNight.objects.all()

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve the details of a movie night, along with the current user's invitation status.

        The invitation status includes:
        - `invitation_id`: The ID of the invitation (if the user is invited).
        - `is_invited`: Whether the user is invited.
        - `attendance_confirmed`: Whether the user has confirmed their attendance.
        - `is_attending`: Whether the user is attending the movie night.

        If no invitation exists for the current user, default values are returned for the invitation status.
        
        Returns:
            Response: A JSON response containing the movie night details and the user's invitation status.
        """
        # Retrieve the movie night instance
        movie_night = self.get_object()

        # Initialize invitation status response
        invitation_status = {
            "invitation_id": None,
            "is_invited": False,
            "attendance_confirmed": False,
            "is_attending": False
        }

        # Use filter().first() to efficiently check if an invitation exists
        invitation = MovieNightInvitation.objects.filter(
            movie_night=movie_night,
            invitee=request.user
        ).first()

        if invitation:
            invitation_status = {
                "invitation_id": invitation.id,
                "is_invited": True,
                "attendance_confirmed": invitation.attendance_confirmed,
                "is_attending": invitation.is_attending
            }   

        # Serialize the movie night details
        serializer = self.get_serializer(movie_night)
        movie_night_data = serializer.data

        # Add invitation status to the response data
        movie_night_data.update({
            "invitation_status": invitation_status,
        })

        return Response(movie_night_data)
########## MovieNightInvitation ############
class MyMovieNightInvitationView(ListAPIView):
    """
    View for listing all MovieNight invitation sent for an authenticated user
    """
    serializer_class = MovieNightInvitationSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = MovieNightInvitationFilterSet
    ordering_fields = ["movie_night__start_time"]

    def get_queryset(self):
        """
        Return invitations for the currently authenticated user, excluding those they have explicitly refused.
        """
        if getattr(self, 'swagger_fake_view', False):
            return MovieNightInvitation.objects.none()
        return MovieNightInvitation.objects.filter(invitee=self.request.user).exclude(is_attending=False, attendance_confirmed=True)

class MovieNightInvitationCreateView(CreateAPIView):
    """
    API view for creating MovieNight invitations.
    This view allows the creator of a MovieNight to send invitations to other users.
    """
    serializer_class = MovieNightInvitationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Get the movie_night object
        movie_night = MovieNight.objects.get(id=self.kwargs['pk'])
        
        # Check if the request user is the creator of the movie night
        if movie_night.creator != self.request.user:
            raise PermissionDenied("Only the creator can invite others.")
        
        # Save the invitation
        serializer.save(movie_night=movie_night)

class MovieNightInvitationDetailView(RetrieveUpdateDestroyAPIView):
    """
    View for retrieving, updating, or deleting a MovieNightInvitation instance.

    - GET: Retrieve details of a specific movie night invitation.
    - PUT/PATCH: Update details of a movie night invitation if the user is the invitee.
    - DELETE: Remove a movie night invitation if the user is the invitee.
    """
    serializer_class = MovieNightInvitationSerializer
    permission_classes = [IsAuthenticated, IsInvitee]  
    queryset = MovieNightInvitation.objects.all() 

################# Genre ###################
class GenreView(ListAPIView):
    """
    View for listing all genres ordered by "name'

    - GET: Lists all genres available in the system.
    """
    serializer_class = GenreSerializer
    permission_classes = [AllowAny]  
    authentication_classes = [] 
    queryset = Genre.objects.all().order_by("name") 


class GenreDetailView(RetrieveAPIView):
    """
    View for retrieving the details of a specific genre.

    - GET: Retrieve details of a specific genre by its ID.
    """
    serializer_class = GenreSerializer
    permission_classes = [AllowAny]  
    authentication_classes = [] 
    queryset = Genre.objects.all()  


"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""