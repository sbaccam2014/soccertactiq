from datetime import timedelta

from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import TrainingLog
from .serializers import TrainingLogSerializer, TrainingStreakSerializer


def _current_streak(player_profile) -> int:
    """
    Counts consecutive trained=True days ending today or yesterday
    (so the streak doesn't visually reset to 0 the moment today hasn't
    been logged yet — it only breaks once a day is actually missed).
    """
    logs_by_date = {
        log.date: log.trained
        for log in TrainingLog.objects.filter(player_profile=player_profile)
    }
    today = timezone.localdate()
    if logs_by_date.get(today):
        cursor = today
    elif logs_by_date.get(today - timedelta(days=1)):
        cursor = today - timedelta(days=1)
    else:
        return 0

    streak = 0
    while logs_by_date.get(cursor):
        streak += 1
        cursor -= timedelta(days=1)
    return streak


class TodayTrainingView(APIView):
    """
    GET /api/training/today/ — today's training log (if any) plus the
    player's current streak, for the Training screen's headline state.

    POST /api/training/today/ — body {"trained": true|false}. Creates
    or updates today's log for the authenticated player. Only today's
    entry can be set this way — there is no endpoint to edit a past
    date, by design (today's log is the one thing a player should be
    able to correct; the rest is history).
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        player_profile = request.user.player_profile
        today_log = TrainingLog.objects.filter(
            player_profile=player_profile, date=timezone.localdate()
        ).first()
        data = {
            "today": today_log,
            "current_streak": _current_streak(player_profile),
        }
        return Response(TrainingStreakSerializer(data).data)

    def post(self, request):
        trained = request.data.get("trained")
        if not isinstance(trained, bool):
            return Response(
                {"trained": "This field is required and must be true or false."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        player_profile = request.user.player_profile
        TrainingLog.objects.update_or_create(
            player_profile=player_profile,
            date=timezone.localdate(),
            defaults={"trained": trained},
        )

        today_log = TrainingLog.objects.get(
            player_profile=player_profile, date=timezone.localdate()
        )
        data = {
            "today": today_log,
            "current_streak": _current_streak(player_profile),
        }
        return Response(TrainingStreakSerializer(data).data)


class TrainingHistoryView(generics.ListAPIView):
    """
    GET /api/training/ — the authenticated player's full training log
    history, most recent first, paginated.
    """

    serializer_class = TrainingLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TrainingLog.objects.filter(
            player_profile=self.request.user.player_profile
        )
