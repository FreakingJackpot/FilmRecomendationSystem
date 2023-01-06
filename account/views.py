from django.shortcuts import render

from account.forms import ChangeEmailForm, ChangePasswordForm, FavouriteGenresForm
from film_recommender.models import FavouriteGenre


def change_email(request):
    if request.method == 'POST':
        form = ChangeEmailForm(request.POST, user=request.user)

        if form.is_valid():
            form.save()
    else:
        form = ChangeEmailForm(user=request.user)

    return render(request, 'account/change_email.html', {'form': form})


def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)

        if form.is_valid():
            form.save()
    else:
        form = ChangePasswordForm(user=request.user)

    return render(request, 'account/change_password.html', {'form': form})


def manage_favourite_genres(request):
    if request.method == 'POST':
        form = FavouriteGenresForm(request.POST, user=request.user)

        if form.is_valid():
            form.save()
    else:
        favourites = FavouriteGenre.objects.select_related('genre').filter(user=request.user)
        initial = {'genres': [favourite.genre for favourite in favourites] if favourites else ()}
        form = FavouriteGenresForm(user=request.user, initial=initial)

    return render(request, 'account/manage_favourite_genres.html', {'form': form})
