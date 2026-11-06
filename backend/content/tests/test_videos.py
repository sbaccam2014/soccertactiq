from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from content.models import Video

User = get_user_model()


def make_video(status=Video.Status.PUBLISHED, title="Test Video", category="Defense"):
    return Video.objects.create(
        title=title,
        category=category,
        description="desc",
        video_url="https://www.youtube.com/watch?v=PLACEHOLDER",
        is_placeholder_video=True,
        status=status,
    )


class VideoVisibilityTests(APITestCase):
    """Covers: unpublished videos never being exposed to players."""

    def setUp(self):
        self.user = User.objects.create_user(username="player1", password="x")
        self.client.force_authenticate(user=self.user)

    def test_draft_video_not_in_list(self):
        make_video(status=Video.Status.DRAFT)
        response = self.client.get("/api/videos/")
        self.assertEqual(response.json()["count"], 0)

    def test_unavailable_video_not_in_list(self):
        make_video(status=Video.Status.UNAVAILABLE)
        response = self.client.get("/api/videos/")
        self.assertEqual(response.json()["count"], 0)

    def test_published_video_in_list(self):
        make_video(status=Video.Status.PUBLISHED)
        response = self.client.get("/api/videos/")
        self.assertEqual(response.json()["count"], 1)

    def test_draft_video_detail_404s(self):
        video = make_video(status=Video.Status.DRAFT)
        response = self.client.get(f"/api/videos/{video.id}/")
        self.assertEqual(response.status_code, 404)

    def test_published_video_detail_returns_video(self):
        video = make_video(status=Video.Status.PUBLISHED)
        response = self.client.get(f"/api/videos/{video.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], video.id)

    def test_anonymous_cannot_list_videos(self):
        self.client.force_authenticate(user=None)
        make_video(status=Video.Status.PUBLISHED)
        response = self.client.get("/api/videos/")
        self.assertIn(response.status_code, (401, 403))

    def test_anonymous_cannot_read_video_detail(self):
        self.client.force_authenticate(user=None)
        video = make_video(status=Video.Status.PUBLISHED)
        response = self.client.get(f"/api/videos/{video.id}/")
        self.assertIn(response.status_code, (401, 403))


class VideoCategoryFilterTests(APITestCase):
    """Covers: filtering the video list by category, and the distinct-categories endpoint."""

    def setUp(self):
        self.user = User.objects.create_user(username="player2", password="x")
        self.client.force_authenticate(user=self.user)

    def test_filter_by_category(self):
        make_video(category="Defense", title="Defense video")
        make_video(category="Midfield", title="Midfield video")
        make_video(category="Forward", title="Forward video")

        response = self.client.get("/api/videos/?category=Midfield")
        results = response.json()["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Midfield video")

    def test_category_filter_is_case_sensitive_exact_match(self):
        make_video(category="Defense", title="Defense video")
        response = self.client.get("/api/videos/?category=defense")
        self.assertEqual(response.json()["count"], 0)

    def test_no_category_filter_returns_all_categories(self):
        make_video(category="Defense")
        make_video(category="Midfield")
        make_video(category="Forward")
        response = self.client.get("/api/videos/")
        self.assertEqual(response.json()["count"], 3)

    def test_video_categories_returns_distinct_published_categories_sorted(self):
        make_video(category="Midfield", title="A")
        make_video(category="Defense", title="B")
        make_video(category="Defense", title="C")  # duplicate category
        make_video(category="Drills", status=Video.Status.DRAFT)  # draft, excluded

        response = self.client.get("/api/video-categories/")
        self.assertEqual(response.json(), ["Defense", "Midfield"])

    def test_video_categories_empty_when_no_published_videos(self):
        response = self.client.get("/api/video-categories/")
        self.assertEqual(response.json(), [])

    def test_anonymous_cannot_list_categories(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/video-categories/")
        self.assertIn(response.status_code, (401, 403))


class YoutubeUrlValidatorTests(APITestCase):
    def test_rejects_non_youtube_url(self):
        from django.core.exceptions import ValidationError

        from content.validators import validate_youtube_url

        with self.assertRaises(ValidationError):
            validate_youtube_url("https://example.com/video")

    def test_accepts_standard_watch_url(self):
        from content.validators import validate_youtube_url

        validate_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    def test_accepts_short_url(self):
        from content.validators import validate_youtube_url

        validate_youtube_url("https://youtu.be/dQw4w9WgXcQ")

    def test_accepts_shorts_url(self):
        from content.validators import validate_youtube_url

        validate_youtube_url("https://www.youtube.com/shorts/yx2w10P3yjc")
