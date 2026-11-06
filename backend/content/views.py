from django.db.models import Exists, OuterRef
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from progress.models import VideoWatch

from .models import Video
from .serializers import VideoDetailSerializer, VideoListSerializer


class PublishedVideoListView(generics.ListAPIView):
    """
    GET /api/videos/ — published videos, with each video annotated with
    whether the current player has watched it (so the list can show a
    watched badge without N+1 queries). Optionally filtered to one
    category via ?category=Defense (exact, case-sensitive match — see
    VideoCategoryListView for the set of categories that currently have
    at least one published video).
    """

    serializer_class = VideoListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        player_profile = self.request.user.player_profile
        watch_exists = VideoWatch.objects.filter(
            video=OuterRef("pk"), player_profile=player_profile
        )
        queryset = Video.objects.filter(status=Video.Status.PUBLISHED).annotate(
            is_watched=Exists(watch_exists)
        )
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category=category)
        return queryset


class PublishedVideoDetailView(generics.RetrieveAPIView):
    """
    GET /api/videos/<id>/ — a single published video. 404s for
    draft/unavailable videos so players can never discover their
    existence or content.
    """

    serializer_class = VideoDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Video.objects.filter(status=Video.Status.PUBLISHED)


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
            Video.objects.filter(status=Video.Status.PUBLISHED)
            .order_by("category")
            .values_list("category", flat=True)
            .distinct()
        )
        return Response(categories)
