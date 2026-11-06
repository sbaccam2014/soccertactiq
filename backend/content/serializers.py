from rest_framework import serializers

from .models import Video


class VideoListSerializer(serializers.ModelSerializer):
    """
    Dashboard/progress list shape: brief description plus whether the
    current player has watched it. `is_watched` is expected to be
    annotated onto the queryset by the view (see
    PublishedVideoListView.get_queryset) — keeps it a single annotated
    query instead of one query per video.
    """

    is_watched = serializers.BooleanField(read_only=True)

    class Meta:
        model = Video
        fields = ["id", "title", "category", "description", "status", "is_watched"]


class VideoDetailSerializer(serializers.ModelSerializer):
    """Video screen shape: everything needed to render and watch the video."""

    class Meta:
        model = Video
        fields = [
            "id",
            "title",
            "category",
            "description",
            "video_url",
            "video_start_seconds",
            "status",
        ]
