from django.contrib import admin
from film_recommender.models import Movie, Genre, FavouriteGenres, DailyRecommendedFilm, DailyRecommendation, Image

admin.site.register(Movie)
admin.site.register(Genre)
admin.site.register(FavouriteGenres)
admin.site.register(DailyRecommendedFilm)
admin.site.register(DailyRecommendation)
admin.site.register(Image)
