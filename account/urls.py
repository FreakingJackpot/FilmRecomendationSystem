from django.urls import path

from account.views import change_email, change_password, manage_favourite_genres,generate_api_token

urlpatterns = [
    path('email/', change_email, name='change_email'),
    path('password/', change_password, name='change_password'),
    path('favourite_genres/', manage_favourite_genres, name='manage_favourite_genres'),
    path('api_token/', generate_api_token, name='generate_api_token'),
]
