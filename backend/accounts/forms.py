from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User


class CaseInsensitiveUsernameFormMixin:
    """
    Django's own UserCreationForm/UserChangeForm validate username
    uniqueness case-*sensitively* (an exact `=` lookup), while our DB
    constraint (accounts.User.Meta.constraints) is case-*insensitive*
    (Lower("username")). Without this check, an admin creating "Sam"
    when "sam" already exists would pass Django's form validation and
    then hit a raw IntegrityError at save() instead of a clean form
    error. This mirrors allauth's own case-insensitive signup check
    (allauth.account.adapter.DefaultAccountAdapter.clean_username) for
    the admin-created-user path, which doesn't go through allauth at all.
    """

    def clean_username(self):
        username = self.cleaned_data["username"]
        existing = User.objects.filter(username__iexact=username)
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise forms.ValidationError(
                "That username is already taken.", code="username_taken"
            )
        return username


class BsaUserCreationForm(CaseInsensitiveUsernameFormMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User


class BsaUserChangeForm(CaseInsensitiveUsernameFormMixin, UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
