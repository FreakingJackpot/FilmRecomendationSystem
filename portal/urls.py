from django.urls import path
from portal.views import HomeView, DetailMovieView, review, GenresView, GenreView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('movie/<pk>/review/', review, name='review'),
    path('movie/<id>/', DetailMovieView.as_view(), name='movie-detail'),
    path('genres/', GenresView.as_view(), name='genres'),
    path('genre/<pk>/movies/', GenreView.as_view(), name='genre-movies'),

]
