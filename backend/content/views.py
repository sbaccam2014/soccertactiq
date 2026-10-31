from django.db.models import OuterRef, Subquery
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from progress.models import Attempt

from .models import CategoryVideo, Video
from .serializers import (
    CategoryVideoSerializer,
    VideoDetailSerializer,
    VideoListSerializer,
)


class PublishedVideoListView(generics.ListAPIView):
    """
    GET /api/videos/ — published videos only, with each video annotated
    with the current player's latest attempt (if any) so the dashboard
    can show completion status and latest score without N+1 queries.
    """

    serializer_class = VideoListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        player_profile = self.request.user.player_profile
        latest_attempt_for_video = (
            Attempt.objects.filter(
                video=OuterRef("pk"), player_profile=player_profile
            )
            .order_by("-submitted_at")
        )
        return (
            Video.objects.filter(status=Video.Status.PUBLISHED)
            .annotate(
                latest_score=Subquery(latest_attempt_for_video.values("score")[:1]),
                latest_attempt_id=Subquery(
                    latest_attempt_for_video.values("id")[:1]
                ),
            )
            .order_by("title")
        )


class PublishedVideoDetailView(generics.RetrieveAPIView):
    """
    GET /api/videos/<id>/ — a single published video with its questions
    and choices, answer key withheld. 404s for draft/unavailable videos
    so players can never discover their existence or content.
    """

    serializer_class = VideoDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Video.objects.filter(status=Video.Status.PUBLISHED)


class CategoryVideoListView(generics.ListAPIView):
    """
    GET /api/category-videos/ — published category-reference videos,
    optionally filtered to one category via ?category=Defense (exact,
    case-sensitive match — see VideoCategoryListView for the set of
    categories that currently have at least one published video). No
    scoring/attempts attached — this is a simple browsable library,
    distinct from the questions-based Videos above.
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
