from django.db import models


class Attempt(models.Model):
    """
    One submission of answers for a lesson by a player. Players may retry
    a lesson; each submission is its own Attempt row (never overwritten),
    so "My Progress" can show dated attempt history.

    `idempotency_key` lets the frontend safely retry a submit request
    (e.g. after a network timeout) without creating a duplicate Attempt:
    the API enforces uniqueness per (player_profile, idempotency_key).
    """

    player_profile = models.ForeignKey(
        "accounts.PlayerProfile", on_delete=models.CASCADE, related_name="attempts"
    )
    # Not a hard FK to Lesson's current state — see AttemptAnswer snapshots.
    # Still a real FK so we can list "attempts for lesson X" efficiently;
    # lessons are archived (status=unavailable) rather than deleted, so
    # historical attempts keep a valid reference.
    lesson = models.ForeignKey(
        "content.Lesson", on_delete=models.PROTECT, related_name="attempts"
    )
    lesson_title_snapshot = models.CharField(
        max_length=200,
        help_text="Lesson title at the time of this attempt, for display "
        "if the lesson is later edited or archived.",
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    correct_count = models.PositiveIntegerField()
    question_count = models.PositiveIntegerField()
    score = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Percentage score, 0-100."
    )
    idempotency_key = models.CharField(max_length=100)

    class Meta:
        ordering = ["-submitted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["player_profile", "idempotency_key"],
                name="progress_attempt_unique_idempotency_per_player",
            )
        ]
        indexes = [
            models.Index(fields=["player_profile", "lesson"]),
        ]

    def __str__(self) -> str:
        return f"{self.player_profile} — {self.lesson_title_snapshot} ({self.score}%)"


class AttemptAnswer(models.Model):
    """
    One answered question within an Attempt. Snapshots the question
    prompt/explanation and the choice texts/correctness exactly as they
    were at submission time, so edits to the live Lesson/Question/
    AnswerChoice content never change how a past attempt is displayed.
    """

    attempt = models.ForeignKey(
        Attempt, on_delete=models.CASCADE, related_name="answers"
    )
    question = models.ForeignKey(
        "content.Question",
        on_delete=models.PROTECT,
        related_name="attempt_answers",
    )
    selected_choice = models.ForeignKey(
        "content.AnswerChoice",
        on_delete=models.PROTECT,
        related_name="selected_in_answers",
    )
    is_correct = models.BooleanField()

    # Snapshots: what the player actually saw and chose, frozen at
    # submission time, independent of later edits to the live content.
    question_prompt_snapshot = models.TextField()
    question_explanation_snapshot = models.TextField()
    selected_choice_text_snapshot = models.CharField(max_length=300)
    correct_choice_text_snapshot = models.CharField(max_length=300)

    class Meta:
        ordering = ["attempt_id", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["attempt", "question"],
                name="progress_one_answer_per_question_per_attempt",
            )
        ]

    def __str__(self) -> str:
        return f"Attempt {self.attempt_id} — Q{self.question_id}"
