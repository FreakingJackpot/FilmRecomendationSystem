from django.conf import settings
from django.utils import translation
from django.shortcuts import render
from rest_framework.authtoken.models import Token

from account.forms import ChangeEmailForm, ChangePasswordForm, FavouriteGenresForm, LanguagesForm, UserFeaturesForm
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


def generate_api_token(request):
    token = None

    if request.method == 'POST':
        Token.objects.filter(user=request.user).delete()

        if 'generate_token' in request.POST:
            token = Token.objects.create(user=request.user)
    else:
        token = Token.objects.filter(user=request.user).first()

    context = {'token': token}
    return render(request, 'account/generate_api_token.html', context)


def update_languages(request):
    if request.method == 'POST':
        form = LanguagesForm(request.POST)

        if form.is_valid():
            user_language = form.cleaned_data['language']
            translation.activate(user_language)

        response = render(request, 'account/languages.html', {'form': form})
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, translation.get_language())
    else:
        initial = {'language': translation.get_language()}
        form = LanguagesForm(initial=initial)
        response = render(request, 'account/languages.html', {'form': form})

    return response


def update_user_features(request):
    if request.method == 'POST':
        form = UserFeaturesForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
    else:
        form = UserFeaturesForm(instance=request.user)
    return render(request, 'account/user_features.html', {'form': form})