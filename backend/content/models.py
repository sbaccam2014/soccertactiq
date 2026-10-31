from django.db import models

from .validators import validate_youtube_url


class Video(models.Model):
    """
    A video with an ordered set of questions. Admins author these
    entirely through Django admin (create, edit, order questions/
    choices, publish, unpublish) — no custom coach dashboard in this
    version. This replaces the earlier "Lesson" concept with a plainer
    one: just a video and its questions, no separate learning-objective
    field or topic tagging.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        UNAVAILABLE = "unavailable", "Unavailable"

    title = models.CharField(max_length=200)
    description = models.TextField(
        blank=True, help_text="Shown on the dashboard and video screen."
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


class Question(models.Model):
    """A single-answer multiple-choice question belonging to a Video."""

    video = models.ForeignKey(
        Video, on_delete=models.CASCADE, related_name="questions"
    )
    prompt = models.TextField()
    explanation = models.TextField(
        help_text="The soccer reasoning behind the correct answer. Shown "
        "to the player only after they submit the attempt."
    )
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["video_id", "display_order", "id"]

    def __str__(self) -> str:
        return f"{self.video.title} — {self.prompt[:50]}"


class AnswerChoice(models.Model):
    """One choice for a Question. Exactly one choice per question should
    have is_correct=True (enforced in admin/clean, not at the DB level,
    to keep this version simple)."""

    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="choices"
    )
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["question_id", "display_order", "id"]

    def __str__(self) -> str:
        return self.text


class CategoryVideo(models.Model):
    """
    A simple, unscored reference video filed under a free-text category
    (e.g. "Defense", "Midfield", "Work Ethics", "Drills") — distinct
    from Video, which has attached questions and scored attempts. No
    questions, no attempts, no scoring: just a title, an ordinary
    YouTube link, and an optional description, organized by category so
    players can browse by topic. Category is free text rather than a
    fixed choice list so new categories can be added from admin without
    a code change.
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
        blank=True, help_text="Optional short note shown with the link."
    )
    video_url = models.URLField(
        "YouTube URL",
        max_length=500,
        validators=[validate_youtube_url],
        help_text="An ordinary youtube.com/watch, youtube.com/embed, "
        "youtube.com/shorts, or youtu.be link.",
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
        "reviewed, real video.",
    )
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "display_order", "-created_at"]

    def __str__(self) -> str:
        return f"{self.category} — {self.title}"
