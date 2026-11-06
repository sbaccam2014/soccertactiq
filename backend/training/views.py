from datetime import date as date_cls
from datetime import timedelta

from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
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


def _trained_day_counts(player_profile, today) -> tuple[int, int]:
    """Counts of trained=True days so far this calendar month and year."""
    month_trained_days = TrainingLog.objects.filter(
        player_profile=player_profile,
        trained=True,
        date__year=today.year,
        date__month=today.month,
    ).count()
    year_trained_days = TrainingLog.objects.filter(
        player_profile=player_profile,
        trained=True,
        date__year=today.year,
    ).count()
    return month_trained_days, year_trained_days


def _streak_summary(player_profile, today, today_log):
    month_trained_days, year_trained_days = _trained_day_counts(player_profile, today)
    return {
        "today": today_log,
        "current_streak": _current_streak(player_profile),
        "month_trained_days": month_trained_days,
        "year_trained_days": year_trained_days,
    }


class TodayTrainingView(APIView):
    """
    GET /api/training/today/ — today's training log (if any) plus the
    player's current streak, for the Training screen's headline state.

    POST /api/training/today/ — body {"trained": true|false}. Creates
    or updates today's log for the authenticated player. See
    DayTrainingView for setting/correcting an earlier date (e.g. to
    backfill a day the player forgot to log).
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        player_profile = request.user.player_profile
        today = timezone.localdate()
        today_log = TrainingLog.objects.filter(
            player_profile=player_profile, date=today
        ).first()
        return Response(
            TrainingStreakSerializer(_streak_summary(player_profile, today, today_log)).data
        )

    def post(self, request):
        trained = request.data.get("trained")
        if not isinstance(trained, bool):
            return Response(
                {"trained": "This field is required and must be true or false."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        player_profile = request.user.player_profile
        today = timezone.localdate()
        today_log, _ = TrainingLog.objects.update_or_create(
            player_profile=player_profile,
            date=today,
            defaults={"trained": trained},
        )
        return Response(
            TrainingStreakSerializer(_streak_summary(player_profile, today, today_log)).data
        )


class DayTrainingView(APIView):
    """
    POST /api/training/<date>/ — body {"trained": true|false}. Creates
    or updates the log for any date up to and including today, so a
    player can backfill a day they forgot to log. Future dates are
    rejected (nothing to log yet). <date> is YYYY-MM-DD.

    Returns the same streak-summary shape as TodayTrainingView so the
    Training screen can refresh its headline state (today/streak/month/
    year totals) in one response after an edit to any date, not only
    today's.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, date):
        try:
            parsed_date = date_cls.fromisoformat(date)
        except ValueError:
            return Response(
                {"date": "Must be a valid date in YYYY-MM-DD format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        trained = request.data.get("trained")
        if not isinstance(trained, bool):
            return Response(
                {"trained": "This field is required and must be true or false."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        today = timezone.localdate()
        if parsed_date > today:
            return Response(
                {"date": "Can't log a future date."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        player_profile = request.user.player_profile
        TrainingLog.objects.update_or_create(
            player_profile=player_profile,
            date=parsed_date,
            defaults={"trained": trained},
        )
        today_log = TrainingLog.objects.filter(
            player_profile=player_profile, date=today
        ).first()
        return Response(
            TrainingStreakSerializer(_streak_summary(player_profile, today, today_log)).data
        )


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


class TrainingCalendarView(generics.ListAPIView):
    """
    GET /api/training/calendar/?year=YYYY&month=M — every logged day
    (trained or not) for one calendar month, unpaginated, for rendering
    a month-grid calendar. Defaults to the current year/month if not
    given. A dedicated endpoint rather than paging through
    TrainingHistoryView, since a calendar needs one month's data in a
    single response regardless of how much history exists.
    """

    serializer_class = TrainingLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        today = timezone.localdate()
        try:
            year = int(self.request.query_params.get("year", today.year))
            month = int(self.request.query_params.get("month", today.month))
        except ValueError:
            raise ValidationError("year and month must be integers.")
        if not 1 <= month <= 12:
            raise ValidationError("month must be between 1 and 12.")

        return TrainingLog.objects.filter(
            player_profile=self.request.user.player_profile,
            date__year=year,
            date__month=month,
        )
