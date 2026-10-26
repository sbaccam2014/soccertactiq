from django.db.models import OuterRef, Subquery
from rest_framework import generics, permissions

from progress.models import Attempt

from .models import Lesson, PositionVideo
from .serializers import (
    LessonDetailSerializer,
    LessonListSerializer,
    PositionVideoSerializer,
)


class PublishedLessonListView(generics.ListAPIView):
    """
    GET /api/lessons/ — published lessons only, with each lesson annotated
    with the current player's latest attempt (if any) so the dashboard
    can show completion status and latest score without N+1 queries.
    """

    serializer_class = LessonListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        player_profile = self.request.user.player_profile
        latest_attempt_for_lesson = (
            Attempt.objects.filter(
                lesson=OuterRef("pk"), player_profile=player_profile
            )
            .order_by("-submitted_at")
        )
        return (
            Lesson.objects.filter(status=Lesson.Status.PUBLISHED)
            .annotate(
                latest_score=Subquery(latest_attempt_for_lesson.values("score")[:1]),
                latest_attempt_id=Subquery(
                    latest_attempt_for_lesson.values("id")[:1]
                ),
            )
            .order_by("title")
        )


class PublishedLessonDetailView(generics.RetrieveAPIView):
    """
    GET /api/lessons/<id>/ — a single published lesson with its questions
    and choices, answer key withheld. 404s for draft/unavailable lessons
    so players can never discover their existence or content.
    """

    serializer_class = LessonDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Lesson.objects.filter(status=Lesson.Status.PUBLISHED)


class PositionVideoListView(generics.ListAPIView):
    """
    GET /api/position-videos/ — published position-reference videos,
    optionally filtered to one position via ?position=fullback (valid
    values: fullback, midfielder, forward). No scoring/attempts attached
    — this is a simple browsable library, not a lesson.
    """

    serializer_class = PositionVideoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = PositionVideo.objects.filter(
            status=PositionVideo.Status.PUBLISHED
        )
        position = self.request.query_params.get("position")
        if position:
            queryset = queryset.filter(position=position)
        return queryset
