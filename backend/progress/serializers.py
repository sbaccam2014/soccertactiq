from rest_framework import serializers

from .models import VideoWatch


class VideoWatchSerializer(serializers.ModelSerializer):
    """Shape returned after marking a video watched, and for the My Progress list."""

    class Meta:
        model = VideoWatch
        fields = ["id", "video", "video_title_snapshot", "watched_at"]
