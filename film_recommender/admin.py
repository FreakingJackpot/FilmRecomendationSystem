from django.contrib import admin
from parler.admin import TranslatableAdmin

from film_recommender.models import Movie, Genre, FavouriteGenre, DailyRecommendedFilm, Tag

admin.site.register(Genre, TranslatableAdmin)
admin.site.register(Tag, TranslatableAdmin)
admin.site.register(FavouriteGenre)
admin.site.register(DailyRecommendedFilm)
