from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView
from rest_framework.decorators import api_view, permission_classes
from movies.serializers import MovieSerializer, MovieDetailSerializer
from movies.models import Movie
from movies.omdb_integration import search_and_save, fill_movie_details
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework import status

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def movie_search(request):
    # Extract the search term and ensure it exists
    term = request.data.get("term", "").strip()  # Remove leading and trailing whitespace

    # Check if term is present
    if not term:
        return Response(
            {"error": "Search term is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        search_and_save(term)
    except Exception as e:
        return Response(
            {"error": "An error occurred while processing your request."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    
    movie_list = Movie.objects.filter(title__icontains=term).only('imdb_id', 'title', 'year')

    # Set up pagination
    paginator = PageNumberPagination()
    paginator.page_size = 50
    result_page = paginator.paginate_queryset(movie_list, request)

    # Serialize the paginated data
    serializer = MovieSerializer(result_page, many=True)

    # Check if the result page is empty
    if not result_page:
        return Response(
            {
                "results": [],
                "message": "No movies found matching your search term."
            },
            status=status.HTTP_200_OK,
        )
    return paginator.get_paginated_response(serializer.data)

class MovieDetailView(RetrieveAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        movie_detail = self.get_object()
        try:
            fill_movie_details(movie_detail)
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        serializer = self.get_serializer(movie_detail)
        return Response(serializer.data)