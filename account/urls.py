from django.urls import path

from account.views import change_email, change_password, manage_favourite_genres, generate_api_token, update_languages, \
    update_user_features

urlpatterns = [
    path('email/', change_email, name='change_email'),
    path('password/', change_password, name='change_password'),
    path('favourite_genres/', manage_favourite_genres, name='manage_favourite_genres'),
    path('api-token/', generate_api_token, name='generate_api_token'),
    path('languages/', update_languages, name='update_languages'),
    path('user-features/', update_user_features, name='update_user_features'),
]
