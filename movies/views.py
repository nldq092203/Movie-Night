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
from movies.serializers import (
    MovieSerializer, 
    MovieDetailSerializer, 
    MovieNightSerializer, 
    MovieNightInvitationSerializer,
    MovieNightDetailSerializer,
    GenreSerializer, 
    MovieSearchSerializer,
    )
from movies.models import Movie, MovieNight, MovieNightInvitation, Genre
from django.contrib.auth import get_user_model
from movies.tasks import search_and_save
from movies.omdb_integration import fill_movie_details
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework import status

from movies.filters import (
    MovieFilterSet, 
    ParticipatingMovieNightFilterSet, 
    MyMovieNightFilterSet, 
    MovieNightInvitationFilterSet
    )
from movies.permissions import MovieNightDetailPermission, MovieNightInvitationPermission, IsInvitee
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
    
class MovieSearchResultsView(ListAPIView):
    """
    API view to return paginated search results based on the search term.
    """
    serializer_class = MovieSerializer
    pagination_class = PageNumberPagination
    permission_classes = [AllowAny]
    queryset = Movie.objects.all()  # Define a default queryset

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Movie.objects.none()
        term = self.request.query_params.get("search_term", "").strip()
        return Movie.objects.filter(title__icontains=term).only('imdb_id', 'title', 'year', 'url_poster')

    @extend_schema(
        parameters=[
            OpenApiParameter(name='search_term', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
        ],
        responses={200: MovieSerializer(many=True)},
        description="Return paginated search results based on the search term.",
    )
    def get(self, request, *args, **kwargs):
        term = request.query_params.get("search_term", "").strip()
        if not term:
            return Response(
                {"error": "Search term is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        movie_list = Movie.objects.filter(title__icontains=term).only('id', 'imdb_id', 'title', 'year', 'url_poster').order_by('-year')

        # Check if there are any results
        if not movie_list:
            return Response(
                {
                    "results": [],
                    "message": "No movies found matching your search term."
                },
                status=status.HTTP_200_OK,
            )

        # Use the default pagination
        page = self.paginate_queryset(movie_list)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(movie_list, many=True)
        return Response(serializer.data)
    
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
    serializer_class = MovieSerializer


############ MovieNight ##############

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
    permission_classes = [IsAuthenticated, MovieNightInvitationPermission]

    def perform_create(self, serializer):
        # Get the movie_night object
        movie_night = MovieNight.objects.get(pk=self.kwargs['pk'])
        
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
    queryset = Genre.objects.all().order_by("name") 


class GenreDetailView(RetrieveAPIView):
    """
    View for retrieving the details of a specific genre.

    - GET: Retrieve details of a specific genre by its ID.
    """
    serializer_class = GenreSerializer
    permission_classes = [AllowAny]  
    queryset = Genre.objects.all()  


"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""