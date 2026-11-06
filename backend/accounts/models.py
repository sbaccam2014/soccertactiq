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
    is_coach = models.BooleanField(
        default=False,
        help_text="Coaches get a separate in-app dashboard (assigned "
        "players' progress/training, their own videos & questions) "
        "instead of the regular player app. Independent of is_staff — "
        "a coach does not get Django admin access by default.",
    )
    is_parent = models.BooleanField(
        default=False,
        help_text="Parents get a separate, read-only in-app dashboard "
        "(linked children's progress/training) instead of the regular "
        "player app. Independent of is_staff/is_coach — a parent does "
        "not get Django admin access or video-authoring by default.",
    )

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
    A player's profile within SoccerTactiq. Separated from User now so that, later,
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


class CoachAssignment(models.Model):
    """
    Links a coach (User with is_coach=True) to a PlayerProfile they're
    assigned to monitor. A coach only sees players they're assigned to;
    assignment is managed by a superuser via Django admin.
    """

    coach = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="coach_assignments",
        limit_choices_to={"is_coach": True},
    )
    player_profile = models.ForeignKey(
        "accounts.PlayerProfile",
        on_delete=models.CASCADE,
        related_name="coach_assignments",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["coach", "player_profile"],
                name="accounts_coachassignment_unique",
            )
        ]

    def __str__(self) -> str:
        return f"{self.coach.username} -> {self.player_profile}"


class ParentLink(models.Model):
    """
    Links a parent (User with is_parent=True) to a PlayerProfile (their
    child). A parent only sees children they're linked to, read-only;
    linking is managed by a superuser via Django admin.
    """

    parent = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="parent_links",
        limit_choices_to={"is_parent": True},
    )
    player_profile = models.ForeignKey(
        "accounts.PlayerProfile",
        on_delete=models.CASCADE,
        related_name="parent_links",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["parent", "player_profile"],
                name="accounts_parentlink_unique",
            )
        ]

    def __str__(self) -> str:
        return f"{self.parent.username} -> {self.player_profile}"
