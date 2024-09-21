from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView
from rest_framework.decorators import api_view, permission_classes
from movies.serializers import MovieSerializer, MovieDetailSerializer
from movies.models import Movie
from movies.omdb_integration import search_and_save, fill_movie_details
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def movie_search(request):
    if request.method == "POST":
        term = request.data["term"]
        search_and_save(term)
        movie_list = Movie.objects.filter(title__icontains=term)

        # Set up pagination
        paginator = PageNumberPagination()
        paginator.page_size = 50
        result_page = paginator.paginate_queryset(movie_list, request)

        serializer = MovieSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)



class MovieDetailView(RetrieveAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        movie_detail = self.get_object()
        fill_movie_details(movie_detail)
        serializer = self.get_serializer(movie_detail)
        return Response(serializer.data)