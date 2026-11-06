from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from accounts.models import ParentLink, PlayerProfile
from content.models import Video
from progress.models import VideoWatch
from training.models import TrainingLog

User = get_user_model()


def _make_player(username):
    user = User.objects.create_user(username=username, password="x")
    return PlayerProfile.objects.get(user=user)


class ParentPermissionTests(APITestCase):
    """A regular (non-parent) player must be rejected by every parent endpoint."""

    def setUp(self):
        self.player = _make_player("player1")
        self.client.force_authenticate(user=self.player.user)

    def test_child_list_rejected_for_non_parent(self):
        response = self.client.get("/api/parent/children/")
        self.assertEqual(response.status_code, 403)

    def test_coach_without_is_parent_rejected(self):
        coach = User.objects.create_user(username="coach1", password="x", is_coach=True)
        self.client.force_authenticate(user=coach)
        response = self.client.get("/api/parent/children/")
        self.assertEqual(response.status_code, 403)

    def test_anonymous_rejected(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/parent/children/")
        self.assertEqual(response.status_code, 403)


class LinkedChildListTests(APITestCase):
    """A parent sees only children linked to them, with a progress summary."""

    def setUp(self):
        self.parent = User.objects.create_user(
            username="parent1", password="x", is_parent=True
        )
        self.client.force_authenticate(user=self.parent)

        self.linked = _make_player("linked-child")
        self.unlinked = _make_player("unlinked-child")
        ParentLink.objects.create(parent=self.parent, player_profile=self.linked)

        self.video = Video.objects.create(
            title="Test Video",
            category="Defense",
            video_url="https://www.youtube.com/watch?v=abc123",
            status=Video.Status.PUBLISHED,
        )
        VideoWatch.objects.create(
            player_profile=self.linked,
            video=self.video,
            video_title_snapshot=self.video.title,
        )
        TrainingLog.objects.create(
            player_profile=self.linked, date=timezone.localdate(), trained=True
        )

    def test_only_linked_child_returned(self):
        response = self.client.get("/api/parent/children/")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]["username"], "linked-child")
        self.assertEqual(body[0]["watched_count"], 1)
        self.assertEqual(body[0]["current_streak"], 1)

    def test_unlinked_child_detail_404s(self):
        response = self.client.get(f"/api/parent/children/{self.unlinked.id}/")
        self.assertEqual(response.status_code, 404)

    def test_linked_child_detail_returns_history(self):
        response = self.client.get(f"/api/parent/children/{self.linked.id}/")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body["watches"]), 1)
        self.assertEqual(len(body["training_logs"]), 1)

    def test_other_parent_without_link_sees_no_children(self):
        other_parent = User.objects.create_user(
            username="parent2", password="x", is_parent=True
        )
        self.client.force_authenticate(user=other_parent)
        response = self.client.get("/api/parent/children/")
        self.assertEqual(response.json(), [])
