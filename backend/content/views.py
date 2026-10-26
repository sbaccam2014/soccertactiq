from django.db.models import OuterRef, Subquery
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from progress.models import Attempt

from .models import CategoryVideo, Lesson
from .serializers import (
    CategoryVideoSerializer,
    LessonDetailSerializer,
    LessonListSerializer,
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


class CategoryVideoListView(generics.ListAPIView):
    """
    GET /api/category-videos/ — published category-reference videos,
    optionally filtered to one category via ?category=Defense (exact,
    case-sensitive match — see VideoCategoryListView for the set of
    categories that currently have at least one published video). No
    scoring/attempts attached — this is a simple browsable library, not
    a lesson.
    """

    serializer_class = CategoryVideoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = CategoryVideo.objects.filter(
            status=CategoryVideo.Status.PUBLISHED
        )
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category=category)
        return queryset


class VideoCategoryListView(APIView):
    """
    GET /api/video-categories/ — the distinct list of categories that
    currently have at least one published video, in display order. Lets
    the frontend render category tabs dynamically instead of hardcoding
    a fixed list, so a new category an admin adds in Django admin shows
    up in the app automatically.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        categories = list(
            CategoryVideo.objects.filter(status=CategoryVideo.Status.PUBLISHED)
            .order_by("category")
            .values_list("category", flat=True)
            .distinct()
        )
        return Response(categories)
