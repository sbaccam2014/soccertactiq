from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import CoachAssignment, PlayerProfile, Team
from progress.models import VideoWatch
from training.models import TrainingLog
from training.views import _current_streak

from .permissions import IsCoach
from .serializers import (
    AssignedPlayerSerializer,
    CoachTeamSerializer,
    CoachVideoSerializer,
    PlayerDetailSerializer,
)


def _assigned_player_profiles(coach):
    return PlayerProfile.objects.filter(coach_assignments__coach=coach)


class AssignedPlayerListView(APIView):
    """
    GET /api/coach/players/ — the players assigned to the authenticated
    coach, each with a lightweight progress summary. Coaches never see
    players they are not assigned to (enforced by filtering through
    CoachAssignment, not by trusting any client-supplied player id).
    """

    permission_classes = [permissions.IsAuthenticated, IsCoach]

    def get(self, request):
        rows = []
        for profile in _assigned_player_profiles(request.user).select_related("user"):
            watched_count = VideoWatch.objects.filter(player_profile=profile).count()
            rows.append(
                {
                    "player_profile": profile,
                    "watched_count": watched_count,
                    "current_streak": _current_streak(profile),
                }
            )
        return Response(AssignedPlayerSerializer(rows, many=True).data)


class AssignedPlayerDetailView(APIView):
    """
    GET /api/coach/players/<player_profile_id>/ — one assigned player's
    full attempt and training history. 404s (not 403) for a player the
    coach isn't assigned to, so a coach can't even confirm the player
    id exists.
    """

    permission_classes = [permissions.IsAuthenticated, IsCoach]

    def get(self, request, player_profile_id):
        profile = get_object_or_404(
            _assigned_player_profiles(request.user), pk=player_profile_id
        )
        data = {
            "player_profile": profile,
            "watches": VideoWatch.objects.filter(player_profile=profile).select_related(
                "video"
            ),
            "training_logs": TrainingLog.objects.filter(player_profile=profile),
        }
        return Response(PlayerDetailSerializer(data).data)


class CoachVideoListCreateView(generics.ListCreateAPIView):
    """
    GET /api/coach/videos/ — videos authored by the authenticated coach.
    POST /api/coach/videos/ — create a new video; publishes immediately
    (no admin review step for coach-authored content, per agreed scope).
    """

    serializer_class = CoachVideoSerializer
    permission_classes = [permissions.IsAuthenticated, IsCoach]

    def get_queryset(self):
        return self.request.user.authored_videos.all()


class CoachVideoDetailView(generics.RetrieveUpdateAPIView):
    """
    GET/PATCH/PUT /api/coach/videos/<id>/ — a coach can only view/edit
    (notably, re-assign) their own authored videos. 404s, not 403, for
    any other video so a coach can't confirm another coach's video ids.
    """

    serializer_class = CoachVideoSerializer
    permission_classes = [permissions.IsAuthenticated, IsCoach]

    def get_queryset(self):
        return self.request.user.authored_videos.all()


class CoachTeamListView(APIView):
    """
    GET /api/coach/teams/ — the distinct teams among the authenticated
    coach's assigned players, for populating the "assign to team"
    control when adding/editing a video.
    """

    permission_classes = [permissions.IsAuthenticated, IsCoach]

    def get(self, request):
        teams = Team.objects.filter(
            players__in=_assigned_player_profiles(request.user)
        ).distinct()
        return Response(CoachTeamSerializer(teams, many=True).data)
