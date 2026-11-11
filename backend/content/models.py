from django.db import models

from .validators import validate_youtube_url
from .youtube import fetch_description


class Video(models.Model):
    """
    A single tactics video, filed under a free-text category (e.g.
    "Defense", "Midfield", "Work Ethics", "Drills"). Admins and coaches
    author these; players watch and mark them as watched (see
    progress.models.VideoWatch) — no quiz/questions in this version.
    Category is free text rather than a fixed choice list so new
    categories can be added from admin without a code change.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        UNAVAILABLE = "unavailable", "Unavailable"

    title = models.CharField(max_length=200)
    category = models.CharField(
        max_length=50,
        help_text='Free-text category, e.g. "Defense", "Midfield", '
        '"Work Ethics", "Drills". Matched exactly (case-sensitive) when '
        "players filter by category, so reuse existing spelling/casing "
        "for a category rather than creating near-duplicates.",
    )
    description = models.TextField(
        blank=True,
        editable=False,
        help_text="Shown on the dashboard and video screen. Fetched "
        "automatically from YouTube when video_url is set — not "
        "hand-edited.",
    )
    video_url = models.URLField(
        "YouTube URL",
        max_length=500,
        validators=[validate_youtube_url],
        help_text="An ordinary youtube.com/watch, youtube.com/embed, "
        "youtube.com/shorts, or youtu.be link. Use the clearly-marked "
        "placeholder for unreviewed seed content.",
    )
    video_start_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Optional: where players should start watching.",
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    is_placeholder_video = models.BooleanField(
        default=False,
        help_text="Mark on if video_url is a placeholder rather than a "
        "reviewed, real video. Shown to admins; not asserted to players "
        "as fact about an unwatched video.",
    )
    display_order = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="authored_videos",
        help_text="The coach who added this video, if any. Null for "
        "admin/seed-authored videos.",
    )
    assigned_teams = models.ManyToManyField(
        "accounts.Team",
        blank=True,
        related_name="assigned_videos",
        help_text="Optional. Every player still sees this video in the "
        "global library regardless — assigning a team additionally "
        "surfaces it in that team's players' \"Assigned\" tab.",
    )
    assigned_players = models.ManyToManyField(
        "accounts.PlayerProfile",
        blank=True,
        related_name="assigned_videos",
        help_text="Optional. Every player still sees this video in the "
        "global library regardless — assigning a player additionally "
        "surfaces it in that player's \"Assigned\" tab.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "display_order", "-created_at"]

    def __str__(self) -> str:
        return f"{self.category} — {self.title}"

    def save(self, *args, **kwargs):
        # Placeholder videos aren't real YouTube content, so there's
        # nothing to look up — leave whatever description was set
        # (e.g. the seed command's own explanatory text) alone.
        url_changed = self._state.adding or self._video_url_changed()
        if url_changed and not self.is_placeholder_video:
            self.description = fetch_description(self.video_url)
        super().save(*args, **kwargs)

    def _video_url_changed(self) -> bool:
        try:
            previous_url = Video.objects.only("video_url").get(pk=self.pk).video_url
        except Video.DoesNotExist:
            return True
        return previous_url != self.video_url
