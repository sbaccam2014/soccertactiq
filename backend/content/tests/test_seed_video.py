from django.core.management import call_command
from django.test import TestCase

from content.models import Video


class SeedDemoVideoCommandTests(TestCase):
    def test_creates_one_draft_video(self):
        call_command("seed_demo_video")
        video = Video.objects.get(title="Create a Passing Option")
        self.assertEqual(video.status, Video.Status.DRAFT)
        self.assertTrue(video.is_placeholder_video)

    def test_running_twice_does_not_duplicate(self):
        call_command("seed_demo_video")
        call_command("seed_demo_video")
        self.assertEqual(
            Video.objects.filter(title="Create a Passing Option").count(), 1
        )
