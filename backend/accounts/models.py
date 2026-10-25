from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model, in place from the project's first migration per the
    brief. Behaves like Django's default AbstractUser for now (username,
    optional email, password hash, staff/active flags, timestamps) but
    gives us room to evolve auth (e.g. verified email login, username-or-
    email login) without a disruptive migration later.

    Username uniqueness/matching is handled case-insensitively — see
    accounts.validators and the custom manager below. The primary key
    (`id`) is the permanent, immutable identifier that all saved progress
    must reference; never use username or email as a foreign key target.
    """

    email = models.EmailField("email address", blank=True)

    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"
        constraints = [
            models.UniqueConstraint(
                models.functions.Lower("username"),
                name="accounts_user_username_ci_unique",
            )
        ]

    def __str__(self) -> str:
        return self.username


class PlayerProfile(models.Model):
    """
    A player's profile within BSA. Separated from User now so that, later,
    a parent/coach account can own one or more player profiles without a
    disruptive migration. For this version each User has exactly one
    PlayerProfile, created automatically at registration.
    """

    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="player_profile",
    )
    display_name = models.CharField(
        "display name",
        max_length=50,
        blank=True,
        help_text="Optional nickname shown in the app. Defaults to the username.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.display_name or self.user.username
