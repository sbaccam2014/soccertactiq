from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from training.models import TrainingLog

User = get_user_model()


class TrainingTodayTests(APITestCase):
    """Covers: the daily yes/no training check-in and current streak."""

    def setUp(self):
        self.user = User.objects.create_user(username="trainer", password="x")
        self.client.force_authenticate(user=self.user)

    def test_get_today_with_no_log_yet(self):
        response = self.client.get("/api/training/today/")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIsNone(body["today"])
        self.assertEqual(body["current_streak"], 0)

    def test_post_today_true_creates_log(self):
        response = self.client.post("/api/training/today/", {"trained": True}, format="json")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["today"]["trained"])
        self.assertEqual(body["current_streak"], 1)
        self.assertEqual(TrainingLog.objects.count(), 1)

    def test_post_today_twice_updates_not_duplicates(self):
        self.client.post("/api/training/today/", {"trained": True}, format="json")
        response = self.client.post("/api/training/today/", {"trained": False}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(TrainingLog.objects.count(), 1)
        self.assertFalse(response.json()["today"]["trained"])
        self.assertEqual(response.json()["current_streak"], 0)

    def test_post_missing_trained_field_rejected(self):
        response = self.client.post("/api/training/today/", {}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_post_non_boolean_trained_rejected(self):
        response = self.client.post(
            "/api/training/today/", {"trained": "yes"}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_streak_counts_consecutive_trained_days(self):
        player_profile = self.user.player_profile
        today = timezone.localdate()
        for days_ago in range(4):
            TrainingLog.objects.create(
                player_profile=player_profile,
                date=today - timedelta(days=days_ago),
                trained=True,
            )
        response = self.client.get("/api/training/today/")
        self.assertEqual(response.json()["current_streak"], 4)

    def test_streak_breaks_on_missed_day(self):
        player_profile = self.user.player_profile
        today = timezone.localdate()
        TrainingLog.objects.create(player_profile=player_profile, date=today, trained=True)
        TrainingLog.objects.create(
            player_profile=player_profile, date=today - timedelta(days=1), trained=True
        )
        # Gap at days_ago=2 (not created) breaks the streak before this one.
        TrainingLog.objects.create(
            player_profile=player_profile, date=today - timedelta(days=3), trained=True
        )
        response = self.client.get("/api/training/today/")
        self.assertEqual(response.json()["current_streak"], 2)

    def test_streak_still_counts_yesterday_if_today_not_logged_yet(self):
        player_profile = self.user.player_profile
        today = timezone.localdate()
        TrainingLog.objects.create(
            player_profile=player_profile, date=today - timedelta(days=1), trained=True
        )
        response = self.client.get("/api/training/today/")
        self.assertEqual(response.json()["current_streak"], 1)

    def test_anonymous_cannot_access_training_today(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/training/today/")
        self.assertIn(response.status_code, (401, 403))

    def test_month_and_year_trained_day_counts(self):
        player_profile = self.user.player_profile
        today = timezone.localdate()
        # 3 trained days this month (including today), 1 untrained day
        # (shouldn't count), and 1 trained day last year (shouldn't
        # count toward this year's total).
        TrainingLog.objects.create(player_profile=player_profile, date=today, trained=True)
        TrainingLog.objects.create(
            player_profile=player_profile, date=today - timedelta(days=1), trained=True
        )
        TrainingLog.objects.create(
            player_profile=player_profile, date=today - timedelta(days=2), trained=True
        )
        TrainingLog.objects.create(
            player_profile=player_profile, date=today - timedelta(days=3), trained=False
        )
        TrainingLog.objects.create(
            player_profile=player_profile,
            date=today - timedelta(days=366),
            trained=True,
        )
        response = self.client.get("/api/training/today/")
        body = response.json()
        self.assertEqual(body["month_trained_days"], 3)
        self.assertEqual(body["year_trained_days"], 3)

    def test_post_today_updates_month_and_year_counts(self):
        response = self.client.post("/api/training/today/", {"trained": True}, format="json")
        body = response.json()
        self.assertEqual(body["month_trained_days"], 1)
        self.assertEqual(body["year_trained_days"], 1)


class TrainingHistoryTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="x")
        self.intruder = User.objects.create_user(username="intruder", password="x")

    def test_owner_sees_own_history(self):
        TrainingLog.objects.create(
            player_profile=self.owner.player_profile,
            date=timezone.localdate(),
            trained=True,
        )
        self.client.force_authenticate(user=self.owner)
        response = self.client.get("/api/training/")
        self.assertEqual(response.json()["count"], 1)

    def test_other_user_does_not_see_owners_history(self):
        TrainingLog.objects.create(
            player_profile=self.owner.player_profile,
            date=timezone.localdate(),
            trained=True,
        )
        self.client.force_authenticate(user=self.intruder)
        response = self.client.get("/api/training/")
        self.assertEqual(response.json()["count"], 0)

    def test_anonymous_cannot_access_history(self):
        response = self.client.get("/api/training/")
        self.assertIn(response.status_code, (401, 403))


class TrainingCalendarTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="x")
        self.intruder = User.objects.create_user(username="intruder", password="x")
        self.client.force_authenticate(user=self.owner)

    def test_defaults_to_current_month(self):
        today = timezone.localdate()
        TrainingLog.objects.create(
            player_profile=self.owner.player_profile, date=today, trained=True
        )
        response = self.client.get("/api/training/calendar/")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]["date"], str(today))

    def test_filters_to_requested_year_and_month(self):
        today = timezone.localdate()
        TrainingLog.objects.create(
            player_profile=self.owner.player_profile, date=today, trained=True
        )
        TrainingLog.objects.create(
            player_profile=self.owner.player_profile,
            date=today - timedelta(days=366),
            trained=True,
        )
        other_date = today - timedelta(days=366)
        response = self.client.get(
            f"/api/training/calendar/?year={other_date.year}&month={other_date.month}"
        )
        body = response.json()
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]["date"], str(other_date))

    def test_unpaginated_response_is_a_plain_list(self):
        response = self.client.get("/api/training/calendar/")
        self.assertIsInstance(response.json(), list)

    def test_invalid_month_rejected(self):
        response = self.client.get("/api/training/calendar/?month=13")
        self.assertEqual(response.status_code, 400)

    def test_non_integer_year_rejected(self):
        response = self.client.get("/api/training/calendar/?year=abc")
        self.assertEqual(response.status_code, 400)

    def test_other_user_does_not_see_owners_calendar(self):
        today = timezone.localdate()
        TrainingLog.objects.create(
            player_profile=self.owner.player_profile, date=today, trained=True
        )
        self.client.force_authenticate(user=self.intruder)
        response = self.client.get("/api/training/calendar/")
        self.assertEqual(response.json(), [])

    def test_anonymous_cannot_access_calendar(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/training/calendar/")
        self.assertIn(response.status_code, (401, 403))


class DayTrainingTests(APITestCase):
    """Covers: backfilling a missed day via POST /api/training/<date>/."""

    def setUp(self):
        self.user = User.objects.create_user(username="backfiller", password="x")
        self.client.force_authenticate(user=self.user)

    def test_backfill_past_date_creates_log(self):
        past = timezone.localdate() - timedelta(days=5)
        response = self.client.post(
            f"/api/training/{past.isoformat()}/", {"trained": True}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            TrainingLog.objects.filter(
                player_profile=self.user.player_profile, date=past, trained=True
            ).exists()
        )

    def test_backfill_updates_existing_log_not_duplicate(self):
        past = timezone.localdate() - timedelta(days=3)
        TrainingLog.objects.create(
            player_profile=self.user.player_profile, date=past, trained=False
        )
        response = self.client.post(
            f"/api/training/{past.isoformat()}/", {"trained": True}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(TrainingLog.objects.count(), 1)
        self.assertTrue(
            TrainingLog.objects.get(player_profile=self.user.player_profile, date=past).trained
        )

    def test_future_date_rejected(self):
        future = timezone.localdate() + timedelta(days=1)
        response = self.client.post(
            f"/api/training/{future.isoformat()}/", {"trained": True}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(
            TrainingLog.objects.filter(
                player_profile=self.user.player_profile, date=future
            ).exists()
        )

    def test_today_is_allowed(self):
        today = timezone.localdate()
        response = self.client.post(
            f"/api/training/{today.isoformat()}/", {"trained": True}, format="json"
        )
        self.assertEqual(response.status_code, 200)

    def test_invalid_date_format_rejected(self):
        response = self.client.post(
            "/api/training/not-a-date/", {"trained": True}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_missing_trained_field_rejected(self):
        past = timezone.localdate() - timedelta(days=1)
        response = self.client.post(f"/api/training/{past.isoformat()}/", {}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_backfill_recomputes_streak(self):
        today = timezone.localdate()
        TrainingLog.objects.create(
            player_profile=self.user.player_profile, date=today, trained=True
        )
        # Yesterday was forgotten — backfilling it should extend the streak to 2.
        yesterday = today - timedelta(days=1)
        response = self.client.post(
            f"/api/training/{yesterday.isoformat()}/", {"trained": True}, format="json"
        )
        self.assertEqual(response.json()["current_streak"], 2)

    def test_anonymous_cannot_backfill(self):
        self.client.force_authenticate(user=None)
        past = timezone.localdate() - timedelta(days=1)
        response = self.client.post(
            f"/api/training/{past.isoformat()}/", {"trained": True}, format="json"
        )
        self.assertIn(response.status_code, (401, 403))

    def test_cannot_backfill_another_players_log(self):
        other = User.objects.create_user(username="intruder", password="x")
        past = timezone.localdate() - timedelta(days=1)
        TrainingLog.objects.create(
            player_profile=other.player_profile, date=past, trained=False
        )
        self.client.post(f"/api/training/{past.isoformat()}/", {"trained": True}, format="json")
        # The requesting user's own log was created/updated...
        self.assertTrue(
            TrainingLog.objects.get(
                player_profile=self.user.player_profile, date=past
            ).trained
        )
        # ...and the other player's log is untouched.
        self.assertFalse(
            TrainingLog.objects.get(player_profile=other.player_profile, date=past).trained
        )
