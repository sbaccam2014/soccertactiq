from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from accounts.models import CoachAssignment, PlayerProfile
from content.models import Video
from progress.models import VideoWatch
from training.models import TrainingLog

User = get_user_model()


def _make_player(username):
    user = User.objects.create_user(username=username, password="x")
    return PlayerProfile.objects.get(user=user)


class CoachPermissionTests(APITestCase):
    """A regular (non-coach) player must be rejected by every coach endpoint."""

    def setUp(self):
        self.player = _make_player("player1")
        self.client.force_authenticate(user=self.player.user)

    def test_player_list_rejected_for_non_coach(self):
        response = self.client.get("/api/coach/players/")
        self.assertEqual(response.status_code, 403)

    def test_video_create_rejected_for_non_coach(self):
        response = self.client.post("/api/coach/videos/", {}, format="json")
        self.assertEqual(response.status_code, 403)

    def test_anonymous_rejected(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/coach/players/")
        self.assertEqual(response.status_code, 403)


class AssignedPlayerListTests(APITestCase):
    """A coach sees only players assigned to them, with a progress summary."""

    def setUp(self):
        self.coach = User.objects.create_user(
            username="coach1", password="x", is_coach=True
        )
        self.client.force_authenticate(user=self.coach)

        self.assigned = _make_player("assigned-player")
        self.unassigned = _make_player("unassigned-player")
        CoachAssignment.objects.create(coach=self.coach, player_profile=self.assigned)

        self.video = Video.objects.create(
            title="Test Video",
            category="Defense",
            video_url="https://www.youtube.com/watch?v=abc123",
            status=Video.Status.PUBLISHED,
        )
        VideoWatch.objects.create(
            player_profile=self.assigned,
            video=self.video,
            video_title_snapshot=self.video.title,
        )
        TrainingLog.objects.create(
            player_profile=self.assigned, date=timezone.localdate(), trained=True
        )

    def test_only_assigned_player_returned(self):
        response = self.client.get("/api/coach/players/")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]["username"], "assigned-player")
        self.assertEqual(body[0]["watched_count"], 1)
        self.assertEqual(body[0]["current_streak"], 1)

    def test_unassigned_player_detail_404s(self):
        response = self.client.get(f"/api/coach/players/{self.unassigned.id}/")
        self.assertEqual(response.status_code, 404)

    def test_assigned_player_detail_returns_history(self):
        response = self.client.get(f"/api/coach/players/{self.assigned.id}/")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body["watches"]), 1)
        self.assertEqual(len(body["training_logs"]), 1)

    def test_other_coach_without_assignment_sees_no_players(self):
        other_coach = User.objects.create_user(
            username="coach2", password="x", is_coach=True
        )
        self.client.force_authenticate(user=other_coach)
        response = self.client.get("/api/coach/players/")
        self.assertEqual(response.json(), [])


class CoachVideoCreateTests(APITestCase):
    """Coach-authored videos publish immediately and are attributed to the coach."""

    def setUp(self):
        self.coach = User.objects.create_user(
            username="coach1", password="x", is_coach=True
        )
        self.client.force_authenticate(user=self.coach)

    def _payload(self, **overrides):
        payload = {
            "title": "New Video",
            "category": "Defense",
            "description": "A coach-made video",
            "video_url": "https://www.youtube.com/watch?v=xyz789",
        }
        payload.update(overrides)
        return payload

    def test_create_video_publishes_immediately_and_sets_created_by(self):
        response = self.client.post(
            "/api/coach/videos/", self._payload(), format="json"
        )
        self.assertEqual(response.status_code, 201, response.data)
        video = Video.objects.get(title="New Video")
        self.assertEqual(video.status, Video.Status.PUBLISHED)
        self.assertEqual(video.created_by, self.coach)

    def test_coach_video_list_only_shows_own_videos(self):
        self.client.post("/api/coach/videos/", self._payload(), format="json")
        other_coach = User.objects.create_user(
            username="coach2", password="x", is_coach=True
        )
        self.client.force_authenticate(user=other_coach)
        self.client.post(
            "/api/coach/videos/", self._payload(title="Other Video"), format="json"
        )

        self.client.force_authenticate(user=self.coach)
        response = self.client.get("/api/coach/videos/")
        self.assertEqual(response.status_code, 200)
        titles = [v["title"] for v in response.json()["results"]]
        self.assertEqual(titles, ["New Video"])
