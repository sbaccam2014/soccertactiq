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
