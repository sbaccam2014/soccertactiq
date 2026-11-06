from django.db import models

DAILY_GOAL_MINUTES = 10


class TrainingLog(models.Model):
    """
    One player's yes/no record for a single calendar date: "did you
    train at least DAILY_GOAL_MINUTES minutes today?" Deliberately
    simple — one row per player per day, a single boolean, no minute
    count or activity breakdown. A player can set or correct any date
    up to and including today (e.g. to backfill a day they forgot to
    log) — see training.views.DayTrainingView. Future dates can't be
    logged in advance.
    """

    player_profile = models.ForeignKey(
        "accounts.PlayerProfile",
        on_delete=models.CASCADE,
        related_name="training_logs",
    )
    date = models.DateField()
    trained = models.BooleanField(
        default=True,
        help_text=f"Did the player do at least {DAILY_GOAL_MINUTES} "
        "minutes of ball work this day?",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(
                fields=["player_profile", "date"],
                name="training_one_log_per_player_per_day",
            )
        ]
        indexes = [
            models.Index(fields=["player_profile", "date"]),
        ]

    def __str__(self) -> str:
        status = "trained" if self.trained else "skipped"
        return f"{self.player_profile} — {self.date} ({status})"
