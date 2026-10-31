from rest_framework import serializers

from .models import AnswerChoice, CategoryVideo, Question, Video


class AnswerChoicePublicSerializer(serializers.ModelSerializer):
    """Choice shape shown to players BEFORE submission: no is_correct."""

    class Meta:
        model = AnswerChoice
        fields = ["id", "text", "display_order"]


class QuestionPublicSerializer(serializers.ModelSerializer):
    """
    Question shape shown to players before submission. Deliberately omits
    `explanation` and each choice's `is_correct` — the answer key must not
    be exposed before submission.
    """

    choices = AnswerChoicePublicSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "prompt", "display_order", "choices"]


class VideoListSerializer(serializers.ModelSerializer):
    """
    Dashboard shape: brief description, completion status, and latest
    score. `latest_score` and `latest_attempt_id` are expected to be
    annotated onto the queryset by the view (see
    PublishedVideoListView.get_queryset) — this keeps "has this player
    completed this video, and with what score" a single annotated query
    instead of one query per video.
    """

    latest_score = serializers.DecimalField(
        max_digits=5, decimal_places=2, read_only=True, allow_null=True
    )
    latest_attempt_id = serializers.IntegerField(read_only=True, allow_null=True)
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            "id",
            "title",
            "description",
            "status",
            "is_completed",
            "latest_score",
            "latest_attempt_id",
        ]

    def get_is_completed(self, obj) -> bool:
        return obj.latest_attempt_id is not None


class VideoDetailSerializer(serializers.ModelSerializer):
    """
    Video screen shape: everything needed to render the video and
    answer its questions, but still no answer key (see
    QuestionPublicSerializer).
    """

    questions = QuestionPublicSerializer(many=True, read_only=True)

    class Meta:
        model = Video
        fields = [
            "id",
            "title",
            "description",
            "video_url",
            "video_start_seconds",
            "status",
            "questions",
        ]


class CategoryVideoSerializer(serializers.ModelSerializer):
    """Public shape for the category video library — no admin-only fields."""

    class Meta:
        model = CategoryVideo
        fields = [
            "id",
            "title",
            "category",
            "description",
            "video_url",
            "video_start_seconds",
            "display_order",
        ]
