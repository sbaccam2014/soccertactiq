from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from content.models import Video
from progress.models import VideoWatch

User = get_user_model()


def make_video(title="Watch Video"):
    return Video.objects.create(
        title=title,
        category="Defense",
        description="desc",
        video_url="https://www.youtube.com/watch?v=PLACEHOLDER",
        is_placeholder_video=True,
        status=Video.Status.PUBLISHED,
    )


class MarkVideoWatchedTests(APITestCase):
    """Covers: marking a video watched, idempotency, and ownership checks."""

    def setUp(self):
        self.video = make_video()
        self.user = User.objects.create_user(username="watcher", password="x")
        self.client.force_authenticate(user=self.user)

    def test_marks_video_watched(self):
        response = self.client.post(f"/api/videos/{self.video.id}/watch/")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            VideoWatch.objects.filter(
                player_profile=self.user.player_profile, video=self.video
            ).exists()
        )

    def test_repeated_watch_does_not_duplicate(self):
        first = self.client.post(f"/api/videos/{self.video.id}/watch/")
        second = self.client.post(f"/api/videos/{self.video.id}/watch/")
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(VideoWatch.objects.count(), 1)
        self.assertEqual(first.json()["id"], second.json()["id"])

    def test_draft_video_rejects_watch(self):
        self.video.status = Video.Status.DRAFT
        self.video.save()
        response = self.client.post(f"/api/videos/{self.video.id}/watch/")
        self.assertEqual(response.status_code, 404)

    def test_anonymous_cannot_mark_watched(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(f"/api/videos/{self.video.id}/watch/")
        self.assertIn(response.status_code, (401, 403))

    def test_nonexistent_video_404s(self):
        response = self.client.post("/api/videos/999999/watch/")
        self.assertEqual(response.status_code, 404)


class VideoListIsWatchedTests(APITestCase):
    """Covers: the video list's is_watched flag reflects the requesting player only."""

    def setUp(self):
        self.video = make_video()
        self.owner = User.objects.create_user(username="owner", password="x")
        self.other = User.objects.create_user(username="other", password="x")

    def test_unwatched_video_shows_false(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get("/api/videos/")
        body = response.json()["results"][0]
        self.assertFalse(body["is_watched"])

    def test_watched_video_shows_true_for_watcher_only(self):
        self.client.force_authenticate(user=self.owner)
        self.client.post(f"/api/videos/{self.video.id}/watch/")

        response = self.client.get("/api/videos/")
        self.assertTrue(response.json()["results"][0]["is_watched"])

        self.client.force_authenticate(user=self.other)
        response = self.client.get("/api/videos/")
        self.assertFalse(response.json()["results"][0]["is_watched"])


class ProgressListOwnershipTests(APITestCase):
    """Covers: one user being unable to read another user's watch history."""

    def setUp(self):
        self.video = make_video()
        self.owner = User.objects.create_user(username="owner", password="x")
        self.intruder = User.objects.create_user(username="intruder", password="x")

        self.client.force_authenticate(user=self.owner)
        self.client.post(f"/api/videos/{self.video.id}/watch/")

    def test_owner_progress_list_includes_watch(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get("/api/progress/")
        self.assertEqual(response.json()["count"], 1)

    def test_other_user_progress_list_is_empty(self):
        self.client.force_authenticate(user=self.intruder)
        response = self.client.get("/api/progress/")
        self.assertEqual(response.json()["count"], 0)

    def test_anonymous_cannot_access_progress(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/progress/")
        self.assertIn(response.status_code, (401, 403))


class ArchivedVideoPreservesWatchTests(APITestCase):
    """Covers: a watch record's title snapshot stays accurate after the video is archived."""

    def setUp(self):
        self.video = make_video()
        self.user = User.objects.create_user(username="historian", password="x")
        self.client.force_authenticate(user=self.user)
        self.client.post(f"/api/videos/{self.video.id}/watch/")

    def test_archiving_video_preserves_watch_title_snapshot(self):
        original_title = self.video.title
        self.video.status = Video.Status.UNAVAILABLE
        self.video.title = "Renamed after archiving"
        self.video.save()

        response = self.client.get("/api/progress/")
        body = response.json()["results"][0]
        self.assertEqual(body["video_title_snapshot"], original_title)
