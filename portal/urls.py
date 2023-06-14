from django.urls import path
from django.views.decorators.vary import vary_on_cookie
from django.views.decorators.cache import cache_page

from portal.views import HomeView, DetailMovieView, review, GenresView, GenreView, DailyRecommendView, SearchMovieView, \
    ReviewedMoviesView

urlpatterns = [
    path('', cache_page(5 * 60)(vary_on_cookie(HomeView.as_view())), name='home'),
    path('movie/<pk>/review/', review, name='review'),
    path('movie/<id>/', cache_page(5 * 60)(vary_on_cookie(DetailMovieView.as_view())), name='movie-detail'),
    path('genres/', cache_page(360 * 60)(GenresView.as_view()), name='genres'),
    path('genres/<pk>/movies/', cache_page(30 * 60)(vary_on_cookie(GenreView.as_view())), name='genre-movies'),
    path('daily_recommend/', cache_page(120 * 60)(vary_on_cookie(DailyRecommendView.as_view())),
         name='daily_recommend'),
    path('search/', SearchMovieView.as_view(), name='search'),
    path('reviewed_films/', cache_page(120 * 60)(vary_on_cookie(ReviewedMoviesView.as_view())), name='reviewed_films')

]
