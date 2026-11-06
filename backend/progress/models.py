from django.db import models


class VideoWatch(models.Model):
    """
    Marks that a player has watched a video. One row per
    (player_profile, video) — watching again doesn't create duplicates,
    it just confirms the same fact. No quiz/scoring in this version:
    "watched" is the only signal tracked.
    """

    player_profile = models.ForeignKey(
        "accounts.PlayerProfile", on_delete=models.CASCADE, related_name="video_watches"
    )
    video = models.ForeignKey(
        "content.Video", on_delete=models.CASCADE, related_name="watches"
    )
    video_title_snapshot = models.CharField(
        max_length=200,
        help_text="Video title at the time it was marked watched, for "
        "display if the video is later edited or archived.",
    )
    watched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-watched_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["player_profile", "video"],
                name="progress_one_watch_per_player_per_video",
            )
        ]

    def __str__(self) -> str:
        return f"{self.player_profile} watched {self.video_title_snapshot}"
