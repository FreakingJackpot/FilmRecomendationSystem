from django.shortcuts import render
from rest_framework.decorators import api_view

from account.forms import ChangeEmailForm, ChangePasswordForm, FavouriteGenresForm
from film_recommender.models import FavouriteGenres


@api_view(['POST', 'GET'])
def change_email(request):
    if request.method == 'POST':
        form = ChangeEmailForm(request.POST, user=request.user)

        if form.is_valid():
            form.save()
    else:
        form = ChangeEmailForm(user=request.user)

    return render(request, 'account/change_email.html', {'form': form})


@api_view(['POST', 'GET'])
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)

        if form.is_valid():
            form.save()
    else:
        form = ChangePasswordForm(user=request.user)

    return render(request, 'account/change_password.html', {'form': form})


@api_view(['POST', 'GET'])
def manage_favourite_genres(request):
    if request.method == 'POST':
        form = FavouriteGenresForm(request.POST, user=request.user)

        if form.is_valid():
            form.save()
    else:
        favourites = FavouriteGenres.objects.prefetch_related('genres').filter(user=request.user).first()
        initial = {'genres': favourites.genres.all() if favourites else ()}
        form = FavouriteGenresForm(user=request.user, initial=initial)

    return render(request, 'account/manage_favourite_genres.html', {'form': form})
