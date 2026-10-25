from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from content.models import AnswerChoice, Lesson

from .models import Attempt, AttemptAnswer
from .serializers import (
    AttemptResultSerializer,
    AttemptSubmissionSerializer,
    AttemptSummarySerializer,
)


class SubmitAttemptView(APIView):
    """
    POST /api/lessons/<lesson_id>/attempts/

    Scores the submission server-side and writes the Attempt + its
    AttemptAnswers atomically. Returns correct answers and explanations
    only in this post-submission response — never before.

    Duplicate-submission safety: a (player_profile, idempotency_key)
    database constraint means a retried request with the same key either
    returns the original attempt's result (if the first request actually
    completed) or fails cleanly without creating a second attempt (if a
    concurrent duplicate is still in flight) — see the IntegrityError
    handling below.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, lesson_id):
        # Draft/unavailable lessons 404 here too — players must never be
        # able to submit against lesson content they couldn't retrieve.
        lesson = get_object_or_404(
            Lesson, pk=lesson_id, status=Lesson.Status.PUBLISHED
        )
        player_profile = request.user.player_profile

        serializer = AttemptSubmissionSerializer(
            data=request.data, context={"lesson": lesson}
        )
        serializer.is_valid(raise_exception=True)
        answers = serializer.validated_data["answers"]
        idempotency_key = serializer.validated_data["idempotency_key"]

        existing = Attempt.objects.filter(
            player_profile=player_profile, idempotency_key=idempotency_key
        ).first()
        if existing is not None:
            return Response(
                AttemptResultSerializer(existing).data, status=status.HTTP_200_OK
            )

        choice_ids = [a["choice_id"] for a in answers]
        choices_by_id = {
            c.id: c
            for c in AnswerChoice.objects.select_related("question").filter(
                id__in=choice_ids
            )
        }

        try:
            with transaction.atomic():
                correct_count = sum(
                    1
                    for a in answers
                    if choices_by_id[a["choice_id"]].is_correct
                )
                question_count = len(answers)
                score = (
                    (correct_count / question_count) * 100
                    if question_count
                    else 0
                )

                attempt = Attempt.objects.create(
                    player_profile=player_profile,
                    lesson=lesson,
                    lesson_title_snapshot=lesson.title,
                    correct_count=correct_count,
                    question_count=question_count,
                    score=score,
                    idempotency_key=idempotency_key,
                )

                attempt_answers = []
                for a in answers:
                    choice = choices_by_id[a["choice_id"]]
                    question = choice.question
                    correct_choice = next(
                        c for c in question.choices.all() if c.is_correct
                    )
                    attempt_answers.append(
                        AttemptAnswer(
                            attempt=attempt,
                            question=question,
                            selected_choice=choice,
                            is_correct=choice.is_correct,
                            question_prompt_snapshot=question.prompt,
                            question_explanation_snapshot=question.explanation,
                            selected_choice_text_snapshot=choice.text,
                            correct_choice_text_snapshot=correct_choice.text,
                        )
                    )
                AttemptAnswer.objects.bulk_create(attempt_answers)
        except IntegrityError:
            # Lost a race against a concurrent duplicate submission with
            # the same idempotency key. The other request's attempt is
            # now the record of truth — return it instead of erroring.
            existing = Attempt.objects.filter(
                player_profile=player_profile, idempotency_key=idempotency_key
            ).first()
            if existing is not None:
                return Response(
                    AttemptResultSerializer(existing).data,
                    status=status.HTTP_200_OK,
                )
            raise

        attempt.refresh_from_db()
        return Response(
            AttemptResultSerializer(attempt).data, status=status.HTTP_201_CREATED
        )


class AttemptDetailView(generics.RetrieveAPIView):
    """
    GET /api/attempts/<id>/ — a past attempt's full result. Players can
    only ever retrieve their own attempts (404, not 403, to avoid
    confirming the attempt ID exists at all to a non-owner).
    """

    serializer_class = AttemptResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Attempt.objects.filter(
            player_profile=self.request.user.player_profile
        )


class MyProgressView(generics.ListAPIView):
    """
    GET /api/progress/ — the authenticated player's full attempt history,
    most recent first, paginated.
    """

    serializer_class = AttemptSummarySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Attempt.objects.filter(
            player_profile=self.request.user.player_profile
        ).select_related("lesson")
