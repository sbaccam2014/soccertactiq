from rest_framework import serializers

from .models import AnswerChoice, Lesson, Question


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


class LessonListSerializer(serializers.ModelSerializer):
    """
    Dashboard shape: brief description, completion status, and latest
    score. `latest_score` and `latest_attempt_id` are expected to be
    annotated onto the queryset by the view (see
    PublishedLessonListView.get_queryset) — this keeps "has this player
    completed this lesson, and with what score" a single annotated query
    instead of one query per lesson.
    """

    latest_score = serializers.DecimalField(
        max_digits=5, decimal_places=2, read_only=True, allow_null=True
    )
    latest_attempt_id = serializers.IntegerField(read_only=True, allow_null=True)
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            "id",
            "title",
            "description",
            "topic",
            "status",
            "is_completed",
            "latest_score",
            "latest_attempt_id",
        ]

    def get_is_completed(self, obj) -> bool:
        return obj.latest_attempt_id is not None


class LessonDetailSerializer(serializers.ModelSerializer):
    """
    Lesson screen shape: everything needed to render the lesson and
    answer its questions, but still no answer key (see
    QuestionPublicSerializer).
    """

    questions = QuestionPublicSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = [
            "id",
            "title",
            "description",
            "learning_objective",
            "topic",
            "video_url",
            "video_start_seconds",
            "video_end_seconds",
            "status",
            "questions",
        ]
