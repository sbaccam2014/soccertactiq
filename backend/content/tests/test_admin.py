from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from content.models import AnswerChoice, Lesson, Question

User = get_user_model()


class LessonAdminPublishTests(TestCase):
    """
    Covers: "Admins can create drafts ... preview, publish, and unpublish
    lessons" and the exactly-one-correct-choice guard.
    """

    def setUp(self):
        self.staff = User.objects.create_superuser(username="staffuser", password="x")
        self.client.force_login(self.staff)

    def _make_lesson(self, correct_choices=1, choice_count=2):
        lesson = Lesson.objects.create(
            title="Admin Test Lesson",
            description="d",
            learning_objective="o",
            video_url="https://www.youtube.com/watch?v=PLACEHOLDER",
            is_placeholder_video=True,
            status=Lesson.Status.DRAFT,
        )
        question = Question.objects.create(
            lesson=lesson, prompt="Q?", explanation="E", display_order=1
        )
        for i in range(choice_count):
            AnswerChoice.objects.create(
                question=question,
                text=f"Choice {i}",
                is_correct=(i < correct_choices),
                display_order=i,
            )
        return lesson

    def test_admin_index_reachable(self):
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)

    def test_publish_action_publishes_valid_lesson(self):
        lesson = self._make_lesson(correct_choices=1, choice_count=2)
        changelist_url = reverse("admin:content_lesson_changelist")
        self.client.post(
            changelist_url,
            {
                "action": "publish_lessons",
                "_selected_action": [str(lesson.pk)],
            },
        )
        lesson.refresh_from_db()
        self.assertEqual(lesson.status, Lesson.Status.PUBLISHED)

    def test_publish_action_rejects_lesson_with_no_correct_choice(self):
        lesson = self._make_lesson(correct_choices=0, choice_count=2)
        changelist_url = reverse("admin:content_lesson_changelist")
        self.client.post(
            changelist_url,
            {
                "action": "publish_lessons",
                "_selected_action": [str(lesson.pk)],
            },
        )
        lesson.refresh_from_db()
        self.assertEqual(lesson.status, Lesson.Status.DRAFT)

    def test_publish_action_rejects_lesson_with_two_correct_choices(self):
        lesson = self._make_lesson(correct_choices=2, choice_count=2)
        changelist_url = reverse("admin:content_lesson_changelist")
        self.client.post(
            changelist_url,
            {
                "action": "publish_lessons",
                "_selected_action": [str(lesson.pk)],
            },
        )
        lesson.refresh_from_db()
        self.assertEqual(lesson.status, Lesson.Status.DRAFT)

    def test_unpublish_action(self):
        lesson = self._make_lesson()
        lesson.status = Lesson.Status.PUBLISHED
        lesson.save()
        changelist_url = reverse("admin:content_lesson_changelist")
        self.client.post(
            changelist_url,
            {
                "action": "unpublish_lessons",
                "_selected_action": [str(lesson.pk)],
            },
        )
        lesson.refresh_from_db()
        self.assertEqual(lesson.status, Lesson.Status.DRAFT)

    def test_non_staff_cannot_access_admin(self):
        User.objects.create_user(username="regular", password="x")
        self.client.logout()
        self.client.login(username="regular", password="x")
        response = self.client.get("/admin/", follow=True)
        self.assertNotContains(response, "Site administration")


class PositionVideoAdminPublishTests(TestCase):
    """Covers the position-video library's admin publish/unpublish actions."""

    def setUp(self):
        self.staff = User.objects.create_superuser(username="pvstaffuser", password="x")
        self.client.force_login(self.staff)

    def _make_video(self):
        from content.models import PositionVideo

        return PositionVideo.objects.create(
            title="Admin Test Video",
            position=PositionVideo.Position.FORWARD,
            video_url="https://www.youtube.com/watch?v=PLACEHOLDER",
            is_placeholder_video=True,
            status=PositionVideo.Status.DRAFT,
        )

    def test_publish_action_publishes_video(self):
        from content.models import PositionVideo

        video = self._make_video()
        changelist_url = reverse("admin:content_positionvideo_changelist")
        self.client.post(
            changelist_url,
            {"action": "publish_videos", "_selected_action": [str(video.pk)]},
        )
        video.refresh_from_db()
        self.assertEqual(video.status, PositionVideo.Status.PUBLISHED)

    def test_unpublish_action(self):
        from content.models import PositionVideo

        video = self._make_video()
        video.status = PositionVideo.Status.PUBLISHED
        video.save()
        changelist_url = reverse("admin:content_positionvideo_changelist")
        self.client.post(
            changelist_url,
            {"action": "unpublish_videos", "_selected_action": [str(video.pk)]},
        )
        video.refresh_from_db()
        self.assertEqual(video.status, PositionVideo.Status.DRAFT)
