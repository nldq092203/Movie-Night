from django.contrib import admin
from movies.models import (
    Genre,
    SearchTerm,
    Movie,
    MovieNight,
    MovieNightInvitation,
    Notification
)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'year')

admin.site.register(Genre)
admin.site.register(SearchTerm)
admin.site.register(Movie, MovieAdmin)
admin.site.register(MovieNight)
admin.site.register(Notification)
admin.site.register(MovieNightInvitation)

