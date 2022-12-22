from django.views.generic import View
from django.shortcuts import render, get_object_or_404

from film_recommender.models import Movie


# Create your views here.

class HomeView(View):
    async def get(self, request, *args, **kwargs):
        user_id = request.user.id
        most_rated_movies = Movie.get_10_most_rated_without_review(user_id=user_id)
        exclude_movies_ids = [movie.id for movie in most_rated_movies]
        most_rated_by_genres = Movie.get_10_most_rated_without_review_for_each_genre(user_id, exclude_movies_ids)

        context = {
            'most_rated_movies': most_rated_movies,
            'most_rated_by_genres': most_rated_by_genres,
        }

        return render(request, 'portal/home.html',context)


class DetailMovieView(View):
    async def get(self, request, movie_id):
        user_id = request.user.id
        movie = get_object_or_404(Movie, movie_id)
        return render(request, 'portal/home.html', {'movie': movie, })
