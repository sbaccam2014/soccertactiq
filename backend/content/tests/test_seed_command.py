from django.core.management import call_command
from django.test import TestCase

from content.models import Lesson, Question


class SeedDemoLessonCommandTests(TestCase):
    def test_creates_one_draft_lesson_with_three_questions(self):
        call_command("seed_demo_lesson")
        lesson = Lesson.objects.get(title="Create a Passing Option")
        self.assertEqual(lesson.status, Lesson.Status.DRAFT)
        self.assertTrue(lesson.is_placeholder_video)
        self.assertEqual(lesson.questions.count(), 3)
        for question in lesson.questions.all():
            self.assertEqual(question.choices.filter(is_correct=True).count(), 1)

    def test_running_twice_does_not_duplicate(self):
        call_command("seed_demo_lesson")
        call_command("seed_demo_lesson")
        self.assertEqual(
            Lesson.objects.filter(title="Create a Passing Option").count(), 1
        )
        lesson = Lesson.objects.get(title="Create a Passing Option")
        self.assertEqual(Question.objects.filter(lesson=lesson).count(), 3)
