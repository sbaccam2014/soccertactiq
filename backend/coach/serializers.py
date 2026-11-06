from rest_framework import serializers

from content.models import Video
from progress.serializers import VideoWatchSerializer
from training.serializers import TrainingLogSerializer


class AssignedPlayerSerializer(serializers.Serializer):
    """
    One assigned player row for the coach dashboard list: identity plus
    a lightweight progress summary (counts only — full history is on
    the player detail endpoint).
    """

    id = serializers.IntegerField(source="player_profile.id")
    display_name = serializers.SerializerMethodField()
    username = serializers.CharField(source="player_profile.user.username")
    watched_count = serializers.IntegerField()
    current_streak = serializers.IntegerField()

    def get_display_name(self, obj):
        profile = obj["player_profile"]
        return profile.display_name or profile.user.username


class PlayerDetailSerializer(serializers.Serializer):
    """A single assigned player's full watch and training history for the coach's player-detail screen."""

    id = serializers.IntegerField(source="player_profile.id")
    display_name = serializers.SerializerMethodField()
    username = serializers.CharField(source="player_profile.user.username")
    watches = VideoWatchSerializer(many=True)
    training_logs = TrainingLogSerializer(many=True)

    def get_display_name(self, obj):
        profile = obj["player_profile"]
        return profile.display_name or profile.user.username


class CoachVideoSerializer(serializers.ModelSerializer):
    """
    Create/view shape for a coach-authored video. Publishes immediately
    on creation (no draft/review step for coach-created content, per
    agreed scope) and always attributes created_by to the requesting
    coach — never trusted from the request body.
    """

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
            "created_by",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "description",
            "status",
            "created_by",
            "created_at",
        ]

    def create(self, validated_data):
        coach = self.context["request"].user
        return Video.objects.create(
            **validated_data, created_by=coach, status=Video.Status.PUBLISHED
        )
