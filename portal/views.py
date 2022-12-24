from django.views.generic import View, ListView, DetailView
from django.shortcuts import render, get_object_or_404

from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.decorators import api_view

from film_recommender.models import Movie, UserReview, Genre, DailyRecommendation


# Create your views here.

class HomeView(View):
    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        most_rated_movies = Movie.get_k_most_rated_without_review(user_id=user_id)
        exclude_movies_ids = [movie.id for movie in most_rated_movies]
        most_rated_by_genres = Movie.get_k_most_rated_without_review_for_each_genre(user_id, exclude_movies_ids)

        context = {
            'most_rated_movies': most_rated_movies,
            'most_rated_by_genres': most_rated_by_genres,
        }

        return render(request, 'portal/home.html', context)


class DetailMovieView(View):
    def get(self, request, id):
        movie = get_object_or_404(Movie, id=id)
        Movie.set_predictions_on_movies_for_user([movie, ], request.user.id)
        same_genres_recommends = Movie.get_same_genres_recommends(request.user.id, movie_id=id,
                                                                  genres=movie.genres.all())
        return render(request, 'portal/detail.html', {'movie': movie, 'same_genres_recommends': same_genres_recommends})


class GenresView(ListView):
    paginate_by = 20
    model = Genre
    template_name = 'portal/genres.html'


class GenreView(ListView):
    paginate_by = 20
    template_name = 'portal/genre.html'

    def get_queryset(self):
        genre_pk = self.kwargs.get('pk')
        queryset = Movie.get_most_related_without_review_on_genre_with_prediction(self.request.user.id, genre_pk)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        pk = self.kwargs.get('pk')
        genre = Genre.objects.get(pk=pk)
        context['genre_name'] = genre.name

        return context


class DailyRecommendView(DetailView):
    template_name = 'portal/daily_recommend.html'
    model = DailyRecommendation
    context_object_name = 'daily_recommendation'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            obj = None
        return obj

    def get_queryset(self):
        user = self.request.user
        queryset = self.model.objects.prefetch_related('movies__movie__genres').filter(user=user)
        return queryset


@api_view(['POST'])
def review(request, pk, **kwargs):
    rating = request.data.get('rating')
    user = request.user

    review, created = UserReview.objects.get_or_create(user=user, movie_id=pk, defaults={
        'rating': rating,
    })

    if not created:
        review.rating = rating
        review.save()

    return Response(data={'status': 'ok'}, status=HTTP_200_OK)


class SearchMovieView(View):
    def get(self, request):
        movies = Movie.search(request.user.id, request.GET.get('query'))
        return render(request, 'portal/search_results.html', {'movies': movies})
