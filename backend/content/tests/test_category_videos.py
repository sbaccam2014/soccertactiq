from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from content.models import CategoryVideo

User = get_user_model()


def make_video(category="Defense", status=CategoryVideo.Status.PUBLISHED, title="Test Video"):
    return CategoryVideo.objects.create(
        title=title,
        category=category,
        video_url="https://www.youtube.com/watch?v=PLACEHOLDER",
        is_placeholder_video=True,
        status=status,
    )


class CategoryVideoListTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="player1", password="x")
        self.client.force_authenticate(user=self.user)

    def test_published_video_in_list(self):
        make_video()
        response = self.client.get("/api/category-videos/")
        self.assertEqual(response.json()["count"], 1)

    def test_draft_video_not_in_list(self):
        make_video(status=CategoryVideo.Status.DRAFT)
        response = self.client.get("/api/category-videos/")
        self.assertEqual(response.json()["count"], 0)

    def test_unavailable_video_not_in_list(self):
        make_video(status=CategoryVideo.Status.UNAVAILABLE)
        response = self.client.get("/api/category-videos/")
        self.assertEqual(response.json()["count"], 0)

    def test_filter_by_category(self):
        make_video(category="Defense", title="Defense video")
        make_video(category="Midfield", title="Midfield video")
        make_video(category="Forward", title="Forward video")

        response = self.client.get("/api/category-videos/?category=Midfield")
        results = response.json()["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Midfield video")

    def test_category_filter_is_case_sensitive_exact_match(self):
        make_video(category="Defense", title="Defense video")
        response = self.client.get("/api/category-videos/?category=defense")
        self.assertEqual(response.json()["count"], 0)

    def test_no_category_filter_returns_all_categories(self):
        make_video(category="Defense")
        make_video(category="Midfield")
        make_video(category="Forward")
        response = self.client.get("/api/category-videos/")
        self.assertEqual(response.json()["count"], 3)

    def test_anonymous_cannot_list_category_videos(self):
        self.client.force_authenticate(user=None)
        make_video()
        response = self.client.get("/api/category-videos/")
        self.assertIn(response.status_code, (401, 403))


class VideoCategoryListTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="player2", password="x")
        self.client.force_authenticate(user=self.user)

    def test_returns_distinct_published_categories_sorted(self):
        make_video(category="Midfield", title="A")
        make_video(category="Defense", title="B")
        make_video(category="Defense", title="C")  # duplicate category
        make_video(category="Drills", status=CategoryVideo.Status.DRAFT)  # draft, excluded

        response = self.client.get("/api/video-categories/")
        self.assertEqual(response.json(), ["Defense", "Midfield"])

    def test_empty_when_no_published_videos(self):
        response = self.client.get("/api/video-categories/")
        self.assertEqual(response.json(), [])

    def test_anonymous_cannot_list_categories(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/video-categories/")
        self.assertIn(response.status_code, (401, 403))
