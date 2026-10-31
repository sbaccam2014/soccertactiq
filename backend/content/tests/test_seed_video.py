from django.core.management import call_command
from django.test import TestCase

from content.models import Question, Video


class SeedDemoVideoCommandTests(TestCase):
    def test_creates_one_draft_video_with_three_questions(self):
        call_command("seed_demo_video")
        video = Video.objects.get(title="Create a Passing Option")
        self.assertEqual(video.status, Video.Status.DRAFT)
        self.assertTrue(video.is_placeholder_video)
        self.assertEqual(video.questions.count(), 3)
        for question in video.questions.all():
            self.assertEqual(question.choices.filter(is_correct=True).count(), 1)

    def test_running_twice_does_not_duplicate(self):
        call_command("seed_demo_video")
        call_command("seed_demo_video")
        self.assertEqual(
            Video.objects.filter(title="Create a Passing Option").count(), 1
        )
        video = Video.objects.get(title="Create a Passing Option")
        self.assertEqual(Question.objects.filter(video=video).count(), 3)
