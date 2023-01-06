from django import forms
from django.contrib.auth import password_validation, get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.contrib.auth.hashers import make_password

from film_recommender.models import Genre, FavouriteGenre

UserModel = get_user_model()


class ChangeEmailForm(forms.Form):
    error_messages = {
        "email_already_exist": _("This email already have account"),
    }

    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(ChangeEmailForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        validate_email(email)

        if UserModel.objects.exclude(id=self.user).filter(email=email).exists():
            raise ValidationError(
                self.error_messages["email_already_exist"],
                code="email_already_exist",
            )

        return email

    def save(self):
        email = self.cleaned_data['email']

        self.user.email = email
        self.user.save()


class ChangePasswordForm(forms.Form):
    error_messages = {
        "password_mismatch": _("The two password fields didn’t match."),
    }

    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2:
            if password1 != password2:
                raise ValidationError(
                    self.error_messages["password_mismatch"],
                    code="password_mismatch",
                )
        password_validation.validate_password(password2)
        return password2

    def save(self):
        password = make_password(self.cleaned_data["password1"])

        self.user.password = password
        self.user.save()


class FavouriteGenresForm(forms.Form):
    genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(FavouriteGenresForm, self).__init__(*args, **kwargs)

    def save(self):
        genres = self.cleaned_data["genres"]
        favourites = FavouriteGenre.objects.filter(user=self.user)
        favourites.delete()

        if genres:
            new_favourites = [FavouriteGenre(user=self.user, genre=genre) for genre in genres]
            FavouriteGenre.objects.bulk_create(new_favourites)
