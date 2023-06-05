from django import forms
from django.contrib.auth import password_validation, get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password

UserModel = get_user_model()


class RegistrationForm(forms.Form):
    error_messages = {
        "password_mismatch": _("The two password fields didn’t match."),
        "email_already_exist": _("This email already have account"),
        "username_already_exist": _("This username already have account"),
    }

    username = forms.CharField(label=_('username'), max_length=255)

    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )

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

    def clean_email(self):
        email = self.cleaned_data.get("email")
        validate_email(email)

        if UserModel.objects.filter(email=email).exists():
            raise ValidationError(
                self.error_messages["email_already_exist"],
                code="email_already_exist",
            )

        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if UserModel.objects.filter(username=username).exists():
            raise ValidationError(
                self.error_messages["username_already_exist"],
                code="username_already_exist",
            )

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
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']

        UserModel.objects.create(username=username, password=password, email=email)
