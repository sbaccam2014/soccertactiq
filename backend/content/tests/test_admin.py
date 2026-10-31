from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from content.models import AnswerChoice, Question, Video

User = get_user_model()


class VideoAdminPublishTests(TestCase):
    """
    Covers: "Admins can create drafts ... publish, and unpublish
    videos" and the exactly-one-correct-choice guard.
    """

    def setUp(self):
        self.staff = User.objects.create_superuser(username="staffuser", password="x")
        self.client.force_login(self.staff)

    def _make_video(self, correct_choices=1, choice_count=2):
        video = Video.objects.create(
            title="Admin Test Video",
            description="d",
            video_url="https://www.youtube.com/watch?v=PLACEHOLDER",
            is_placeholder_video=True,
            status=Video.Status.DRAFT,
        )
        question = Question.objects.create(
            video=video, prompt="Q?", explanation="E", display_order=1
        )
        for i in range(choice_count):
            AnswerChoice.objects.create(
                question=question,
                text=f"Choice {i}",
                is_correct=(i < correct_choices),
                display_order=i,
            )
        return video

    def test_admin_index_reachable(self):
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)

    def test_publish_action_publishes_valid_video(self):
        video = self._make_video(correct_choices=1, choice_count=2)
        changelist_url = reverse("admin:content_video_changelist")
        self.client.post(
            changelist_url,
            {
                "action": "publish_videos",
                "_selected_action": [str(video.pk)],
            },
        )
        video.refresh_from_db()
        self.assertEqual(video.status, Video.Status.PUBLISHED)

    def test_publish_action_rejects_video_with_no_correct_choice(self):
        video = self._make_video(correct_choices=0, choice_count=2)
        changelist_url = reverse("admin:content_video_changelist")
        self.client.post(
            changelist_url,
            {
                "action": "publish_videos",
                "_selected_action": [str(video.pk)],
            },
        )
        video.refresh_from_db()
        self.assertEqual(video.status, Video.Status.DRAFT)

    def test_publish_action_rejects_video_with_two_correct_choices(self):
        video = self._make_video(correct_choices=2, choice_count=2)
        changelist_url = reverse("admin:content_video_changelist")
        self.client.post(
            changelist_url,
            {
                "action": "publish_videos",
                "_selected_action": [str(video.pk)],
            },
        )
        video.refresh_from_db()
        self.assertEqual(video.status, Video.Status.DRAFT)

    def test_unpublish_action(self):
        video = self._make_video()
        video.status = Video.Status.PUBLISHED
        video.save()
        changelist_url = reverse("admin:content_video_changelist")
        self.client.post(
            changelist_url,
            {
                "action": "unpublish_videos",
                "_selected_action": [str(video.pk)],
            },
        )
        video.refresh_from_db()
        self.assertEqual(video.status, Video.Status.DRAFT)

    def test_non_staff_cannot_access_admin(self):
        User.objects.create_user(username="regular", password="x")
        self.client.logout()
        self.client.login(username="regular", password="x")
        response = self.client.get("/admin/", follow=True)
        self.assertNotContains(response, "Site administration")


class CategoryVideoAdminPublishTests(TestCase):
    """Covers the category-video library's admin publish/unpublish actions."""

    def setUp(self):
        self.staff = User.objects.create_superuser(username="cvstaffuser", password="x")
        self.client.force_login(self.staff)

    def _make_video(self):
        from content.models import CategoryVideo

        return CategoryVideo.objects.create(
            title="Admin Test Video",
            category="Forward",
            video_url="https://www.youtube.com/watch?v=PLACEHOLDER",
            is_placeholder_video=True,
            status=CategoryVideo.Status.DRAFT,
        )

    def test_publish_action_publishes_video(self):
        from content.models import CategoryVideo

        video = self._make_video()
        changelist_url = reverse("admin:content_categoryvideo_changelist")
        self.client.post(
            changelist_url,
            {"action": "publish_videos", "_selected_action": [str(video.pk)]},
        )
        video.refresh_from_db()
        self.assertEqual(video.status, CategoryVideo.Status.PUBLISHED)

    def test_unpublish_action(self):
        from content.models import CategoryVideo

        video = self._make_video()
        video.status = CategoryVideo.Status.PUBLISHED
        video.save()
        changelist_url = reverse("admin:content_categoryvideo_changelist")
        self.client.post(
            changelist_url,
            {"action": "unpublish_videos", "_selected_action": [str(video.pk)]},
        )
        video.refresh_from_db()
        self.assertEqual(video.status, CategoryVideo.Status.DRAFT)
