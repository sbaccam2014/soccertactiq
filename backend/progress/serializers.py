from rest_framework import serializers

from content.models import AnswerChoice, Lesson, Question

from .models import Attempt, AttemptAnswer


class AnswerSubmissionSerializer(serializers.Serializer):
    """One answer within a submission: which question, which choice."""

    question_id = serializers.IntegerField()
    choice_id = serializers.IntegerField()


class AttemptSubmissionSerializer(serializers.Serializer):
    """
    Request body for POST /api/lessons/<id>/attempts/.

    The lesson is taken from the URL, and the player from
    request.user — never from the request body — so a client can never
    submit on behalf of another player or against a lesson ID mismatched
    with the answers. `idempotency_key` lets a client safely retry a
    submit (e.g. after a timeout) without creating a duplicate attempt.
    """

    idempotency_key = serializers.CharField(max_length=100)
    answers = AnswerSubmissionSerializer(many=True)

    def validate(self, attrs):
        lesson: Lesson = self.context["lesson"]
        answers = attrs["answers"]

        question_ids_submitted = [a["question_id"] for a in answers]
        if len(question_ids_submitted) != len(set(question_ids_submitted)):
            raise serializers.ValidationError(
                "Each question may only be answered once per submission."
            )

        lesson_question_ids = set(
            lesson.questions.values_list("id", flat=True)
        )
        if set(question_ids_submitted) != lesson_question_ids:
            raise serializers.ValidationError(
                "An answer is required for every question in this lesson, "
                "and only for questions that belong to it."
            )

        # Validate each selected choice actually belongs to the question
        # it was submitted for — never trust client-side pairing.
        choices_by_question = {
            question_id: set(
                AnswerChoice.objects.filter(question_id=question_id).values_list(
                    "id", flat=True
                )
            )
            for question_id in question_ids_submitted
        }
        for answer in answers:
            valid_choice_ids = choices_by_question.get(answer["question_id"], set())
            if answer["choice_id"] not in valid_choice_ids:
                raise serializers.ValidationError(
                    f"Choice {answer['choice_id']} does not belong to "
                    f"question {answer['question_id']}."
                )

        return attrs


class AttemptAnswerResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttemptAnswer
        fields = [
            "question",
            "question_prompt_snapshot",
            "question_explanation_snapshot",
            "selected_choice_text_snapshot",
            "correct_choice_text_snapshot",
            "is_correct",
        ]


class AttemptResultSerializer(serializers.ModelSerializer):
    """
    Full result shape returned after submission AND when viewing a past
    attempt's detail: submitted answers, correct answers, explanations,
    and score — all taken from snapshots so later lesson edits never
    change how a historical attempt is displayed.
    """

    answers = AttemptAnswerResultSerializer(many=True, read_only=True)

    class Meta:
        model = Attempt
        fields = [
            "id",
            "lesson",
            "lesson_title_snapshot",
            "submitted_at",
            "correct_count",
            "question_count",
            "score",
            "answers",
        ]


class AttemptSummarySerializer(serializers.ModelSerializer):
    """Compact shape for the My Progress list: one row per attempt."""

    class Meta:
        model = Attempt
        fields = [
            "id",
            "lesson",
            "lesson_title_snapshot",
            "submitted_at",
            "correct_count",
            "question_count",
            "score",
        ]
