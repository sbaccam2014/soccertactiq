from django.core.exceptions import ValidationError
from django.db import models

from .validators import validate_youtube_url


class Lesson(models.Model):
    """
    A single lesson: a coaching concept, a YouTube video to watch, and an
    ordered set of questions. Admins author these entirely through Django
    admin (create, edit, order questions/choices, preview, publish,
    unpublish) — no custom coach dashboard in this version.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        UNAVAILABLE = "unavailable", "Unavailable"

    title = models.CharField(max_length=200)
    description = models.TextField(
        help_text="Shown on the dashboard and lesson screen."
    )
    learning_objective = models.TextField(
        help_text="What the player should understand after this lesson "
        "(e.g. the soccer reasoning being taught), shown on the lesson screen."
    )
    topic = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional free-text topic/tag, e.g. 'Passing angles'.",
    )
    video_url = models.URLField(
        "YouTube URL",
        max_length=500,
        validators=[validate_youtube_url],
        help_text="An ordinary youtube.com/watch, youtube.com/embed, or "
        "youtu.be link. Use the clearly-marked placeholder for unreviewed "
        "seed content.",
    )
    video_start_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Optional: where players should start watching.",
    )
    video_end_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Optional: where players can stop watching.",
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

    def clean(self):
        super().clean()
        if (
            self.video_start_seconds is not None
            and self.video_end_seconds is not None
            and self.video_start_seconds >= self.video_end_seconds
        ):
            raise ValidationError(
                {"video_end_seconds": "End timestamp must be after the start timestamp."}
            )


class Question(models.Model):
    """A single-answer multiple-choice question belonging to a Lesson."""

    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="questions"
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
        ordering = ["lesson_id", "display_order", "id"]

    def __str__(self) -> str:
        return f"{self.lesson.title} — {self.prompt[:50]}"


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


class PositionVideo(models.Model):
    """
    A simple, unscored reference video for a specific playing position —
    distinct from Lesson, which is a full quiz-based lesson. No
    questions, no attempts, no scoring: just a title, an ordinary
    YouTube link, and an optional description, organized by position so
    players can browse "videos for my position."
    """

    class Position(models.TextChoices):
        FULLBACK = "fullback", "Fullback"
        MIDFIELDER = "midfielder", "Midfielder"
        FORWARD = "forward", "Forward"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        UNAVAILABLE = "unavailable", "Unavailable"

    title = models.CharField(max_length=200)
    position = models.CharField(max_length=20, choices=Position.choices)
    description = models.TextField(
        blank=True, help_text="Optional short note shown with the link."
    )
    video_url = models.URLField(
        "YouTube URL",
        max_length=500,
        validators=[validate_youtube_url],
        help_text="An ordinary youtube.com/watch, youtube.com/embed, or "
        "youtu.be link.",
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
        ordering = ["position", "display_order", "-created_at"]

    def __str__(self) -> str:
        return f"{self.get_position_display()} — {self.title}"
