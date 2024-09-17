from rest_framework.response import Response
from rest_framework.decorators import api_view
from movies.serializers import MovieSerializer
from movies.models import Movie
from movies.omdb_integration import search_and_save

@api_view(["POST"])
def movie_search(request):
    if request.method == "POST":
        term = request.data["term"]
        search_and_save(term)
        movie_list = Movie.objects.filter(title__icontains=term)
        serializer = MovieSerializer(movie_list, many=True)
        return Response(serializer.data)

