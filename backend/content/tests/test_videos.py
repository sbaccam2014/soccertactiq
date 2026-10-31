from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from content.models import AnswerChoice, Question, Video

User = get_user_model()


def make_video(status=Video.Status.PUBLISHED, title="Test Video"):
    video = Video.objects.create(
        title=title,
        description="desc",
        video_url="https://www.youtube.com/watch?v=PLACEHOLDER",
        is_placeholder_video=True,
        status=status,
    )
    q = Question.objects.create(
        video=video, prompt="Q1?", explanation="Because reasons.", display_order=1
    )
    AnswerChoice.objects.create(question=q, text="Right", is_correct=True, display_order=1)
    AnswerChoice.objects.create(question=q, text="Wrong", is_correct=False, display_order=2)
    return video, q


class VideoVisibilityTests(APITestCase):
    """Covers: "Hidden answer keys and unpublished videos."""

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
        video, _ = make_video(status=Video.Status.DRAFT)
        response = self.client.get(f"/api/videos/{video.id}/")
        self.assertEqual(response.status_code, 404)

    def test_published_video_detail_hides_answer_key(self):
        video, _ = make_video(status=Video.Status.PUBLISHED)
        response = self.client.get(f"/api/videos/{video.id}/")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        question = body["questions"][0]
        self.assertNotIn("explanation", question)
        for choice in question["choices"]:
            self.assertNotIn("is_correct", choice)

    def test_anonymous_cannot_list_videos(self):
        self.client.force_authenticate(user=None)
        make_video(status=Video.Status.PUBLISHED)
        response = self.client.get("/api/videos/")
        self.assertIn(response.status_code, (401, 403))

    def test_anonymous_cannot_read_video_detail(self):
        self.client.force_authenticate(user=None)
        video, _ = make_video(status=Video.Status.PUBLISHED)
        response = self.client.get(f"/api/videos/{video.id}/")
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
