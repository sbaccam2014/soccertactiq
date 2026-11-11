from rest_framework import serializers

from accounts.models import PlayerProfile, Team
from content.models import Video
from progress.serializers import VideoWatchSerializer
from training.serializers import TrainingLogSerializer


class CoachTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ["id", "name"]


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
    Create/view/update shape for a coach-authored video. Publishes
    immediately on creation (no draft/review step for coach-created
    content, per agreed scope) and always attributes created_by to the
    requesting coach — never trusted from the request body.

    assigned_teams/assigned_players are restricted to the requesting
    coach's own roster (their assigned players, and the teams those
    players belong to) — a coach can't target another coach's players
    or an unrelated team, even by guessing an id.
    """

    assigned_teams = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.none(), many=True, required=False
    )
    assigned_players = serializers.PrimaryKeyRelatedField(
        queryset=PlayerProfile.objects.none(), many=True, required=False
    )

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
            "assigned_teams",
            "assigned_players",
        ]
        read_only_fields = [
            "id",
            "description",
            "status",
            "created_by",
            "created_at",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        coach = self.context["request"].user
        assigned_players = PlayerProfile.objects.filter(coach_assignments__coach=coach)
        teams = Team.objects.filter(players__in=assigned_players).distinct()
        # many=True wraps the field in a ManyRelatedField — the queryset
        # used for pk validation lives on .child_relation, not the field
        # itself; setting .queryset directly is silently a no-op.
        self.fields["assigned_players"].child_relation.queryset = assigned_players
        self.fields["assigned_teams"].child_relation.queryset = teams

    def create(self, validated_data):
        coach = self.context["request"].user
        assigned_teams = validated_data.pop("assigned_teams", [])
        assigned_players = validated_data.pop("assigned_players", [])
        video = Video.objects.create(
            **validated_data, created_by=coach, status=Video.Status.PUBLISHED
        )
        video.assigned_teams.set(assigned_teams)
        video.assigned_players.set(assigned_players)
        return video

    def update(self, instance, validated_data):
        assigned_teams = validated_data.pop("assigned_teams", None)
        assigned_players = validated_data.pop("assigned_players", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if assigned_teams is not None:
            instance.assigned_teams.set(assigned_teams)
        if assigned_players is not None:
            instance.assigned_players.set(assigned_players)
        return instance
