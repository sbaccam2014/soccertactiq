from rest_framework import serializers

from .models import TrainingLog


class TrainingLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingLog
        fields = ["id", "date", "trained"]


class TrainingStreakSerializer(serializers.Serializer):
    """Summary shape for the Training screen: today's status plus a
    simple current-streak count (consecutive days up to and including
    today/yesterday with trained=True)."""

    today = TrainingLogSerializer(allow_null=True)
    current_streak = serializers.IntegerField()
