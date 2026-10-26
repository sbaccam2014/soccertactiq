from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from content.models import PositionVideo

User = get_user_model()


def make_video(position=PositionVideo.Position.FULLBACK, status=PositionVideo.Status.PUBLISHED, title="Test Video"):
    return PositionVideo.objects.create(
        title=title,
        position=position,
        video_url="https://www.youtube.com/watch?v=PLACEHOLDER",
        is_placeholder_video=True,
        status=status,
    )


class PositionVideoListTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="player1", password="x")
        self.client.force_authenticate(user=self.user)

    def test_published_video_in_list(self):
        make_video()
        response = self.client.get("/api/position-videos/")
        self.assertEqual(response.json()["count"], 1)

    def test_draft_video_not_in_list(self):
        make_video(status=PositionVideo.Status.DRAFT)
        response = self.client.get("/api/position-videos/")
        self.assertEqual(response.json()["count"], 0)

    def test_unavailable_video_not_in_list(self):
        make_video(status=PositionVideo.Status.UNAVAILABLE)
        response = self.client.get("/api/position-videos/")
        self.assertEqual(response.json()["count"], 0)

    def test_filter_by_position(self):
        make_video(position=PositionVideo.Position.FULLBACK, title="FB video")
        make_video(position=PositionVideo.Position.MIDFIELDER, title="MF video")
        make_video(position=PositionVideo.Position.FORWARD, title="FWD video")

        response = self.client.get("/api/position-videos/?position=midfielder")
        results = response.json()["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "MF video")

    def test_no_position_filter_returns_all_positions(self):
        make_video(position=PositionVideo.Position.FULLBACK)
        make_video(position=PositionVideo.Position.MIDFIELDER)
        make_video(position=PositionVideo.Position.FORWARD)
        response = self.client.get("/api/position-videos/")
        self.assertEqual(response.json()["count"], 3)

    def test_anonymous_cannot_list_position_videos(self):
        self.client.force_authenticate(user=None)
        make_video()
        response = self.client.get("/api/position-videos/")
        self.assertIn(response.status_code, (401, 403))
