from django.contrib import admin
from film_recommender.models import Movie, Genre, FavouriteGenre, DailyRecommendedFilm, Image

admin.site.register(Movie)
admin.site.register(Genre)
admin.site.register(FavouriteGenre)
admin.site.register(DailyRecommendedFilm)
admin.site.register(Image)
