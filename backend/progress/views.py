from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from content.models import Video

from .models import VideoWatch
from .serializers import VideoWatchSerializer


class MarkVideoWatchedView(APIView):
    """
    POST /api/videos/<video_id>/watch/ — marks the video watched for the
    authenticated player. Idempotent: watching the same video again
    just returns the existing watch record rather than erroring or
    creating a duplicate.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, video_id):
        # Draft/unavailable videos 404 here too — players must never be
        # able to mark watched a video they couldn't retrieve.
        video = get_object_or_404(Video, pk=video_id, status=Video.Status.PUBLISHED)
        player_profile = request.user.player_profile

        watch, created = VideoWatch.objects.get_or_create(
            player_profile=player_profile,
            video=video,
            defaults={"video_title_snapshot": video.title},
        )
        return Response(
            VideoWatchSerializer(watch).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class MyProgressView(generics.ListAPIView):
    """
    GET /api/progress/ — the authenticated player's watched videos,
    most recently watched first, paginated.
    """

    serializer_class = VideoWatchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return VideoWatch.objects.filter(
            player_profile=self.request.user.player_profile
        ).select_related("video")
