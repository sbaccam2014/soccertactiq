from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import PlayerProfile
from progress.models import VideoWatch
from training.models import TrainingLog
from training.views import _current_streak

from .permissions import IsParent
from .serializers import ChildDetailSerializer, ChildSerializer


def _linked_player_profiles(parent):
    return PlayerProfile.objects.filter(parent_links__parent=parent)


class LinkedChildListView(APIView):
    """
    GET /api/parent/children/ — the children linked to the authenticated
    parent, each with a read-only progress summary. Mirrors the coach
    player-list endpoint's shape but is scoped through ParentLink, and
    there is no corresponding write endpoint — parents never create or
    edit content.
    """

    permission_classes = [permissions.IsAuthenticated, IsParent]

    def get(self, request):
        rows = []
        for profile in _linked_player_profiles(request.user).select_related("user"):
            watched_count = VideoWatch.objects.filter(player_profile=profile).count()
            rows.append(
                {
                    "player_profile": profile,
                    "watched_count": watched_count,
                    "current_streak": _current_streak(profile),
                }
            )
        return Response(ChildSerializer(rows, many=True).data)


class LinkedChildDetailView(APIView):
    """
    GET /api/parent/children/<player_profile_id>/ — one linked child's
    full watch and training history. 404s (not 403) for a player the
    parent isn't linked to, so a parent can't even confirm the player id
    exists.
    """

    permission_classes = [permissions.IsAuthenticated, IsParent]

    def get(self, request, player_profile_id):
        profile = get_object_or_404(
            _linked_player_profiles(request.user), pk=player_profile_id
        )
        data = {
            "player_profile": profile,
            "watches": VideoWatch.objects.filter(player_profile=profile).select_related(
                "video"
            ),
            "training_logs": TrainingLog.objects.filter(player_profile=profile),
        }
        return Response(ChildDetailSerializer(data).data)
