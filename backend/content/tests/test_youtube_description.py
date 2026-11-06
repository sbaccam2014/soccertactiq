from unittest.mock import patch

from django.test import TestCase

from content.models import Video
from content.youtube import extract_video_id


class ExtractVideoIdTests(TestCase):
    def test_standard_watch_url(self):
        self.assertEqual(
            extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
            "dQw4w9WgXcQ",
        )

    def test_shorts_url(self):
        self.assertEqual(
            extract_video_id("https://www.youtube.com/shorts/yx2w10P3yjc"),
            "yx2w10P3yjc",
        )

    def test_short_url(self):
        self.assertEqual(
            extract_video_id("https://youtu.be/dQw4w9WgXcQ"), "dQw4w9WgXcQ"
        )

    def test_embed_url(self):
        self.assertEqual(
            extract_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ"),
            "dQw4w9WgXcQ",
        )

    def test_unrecognized_url_returns_none(self):
        self.assertIsNone(extract_video_id("https://example.com/video"))


class VideoSaveAutoFillTests(TestCase):
    """Covers: Video.save() auto-fetches description from YouTube on create/url-change."""

    @patch("content.models.fetch_description", return_value="Fetched description.")
    def test_description_fetched_on_create(self, mock_fetch):
        video = Video.objects.create(
            title="Test",
            category="Defense",
            video_url="https://www.youtube.com/watch?v=abc123",
        )
        mock_fetch.assert_called_once_with("https://www.youtube.com/watch?v=abc123")
        self.assertEqual(video.description, "Fetched description.")

    @patch("content.models.fetch_description", return_value="Ignored.")
    def test_placeholder_video_skips_fetch(self, mock_fetch):
        video = Video.objects.create(
            title="Seed",
            category="Midfield",
            video_url="https://www.youtube.com/watch?v=PLACEHOLDER",
            is_placeholder_video=True,
            description="Hand-written seed description.",
        )
        mock_fetch.assert_not_called()
        self.assertEqual(video.description, "Hand-written seed description.")

    @patch("content.models.fetch_description", return_value="Second fetch.")
    def test_description_refetched_when_url_changes(self, mock_fetch):
        video = Video.objects.create(
            title="Test",
            category="Defense",
            video_url="https://www.youtube.com/watch?v=abc123",
        )
        mock_fetch.reset_mock()
        video.video_url = "https://www.youtube.com/watch?v=xyz789"
        video.save()
        mock_fetch.assert_called_once_with("https://www.youtube.com/watch?v=xyz789")
        self.assertEqual(video.description, "Second fetch.")

    @patch("content.models.fetch_description", return_value="First fetch.")
    def test_description_not_refetched_on_unrelated_save(self, mock_fetch):
        video = Video.objects.create(
            title="Test",
            category="Defense",
            video_url="https://www.youtube.com/watch?v=abc123",
        )
        mock_fetch.reset_mock()
        video.title = "Renamed"
        video.save()
        mock_fetch.assert_not_called()
