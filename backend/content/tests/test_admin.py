from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from content.models import Video

User = get_user_model()


class VideoAdminPublishTests(TestCase):
    """Covers: admins can create drafts, publish, and unpublish videos."""

    def setUp(self):
        self.staff = User.objects.create_superuser(username="staffuser", password="x")
        self.client.force_login(self.staff)

    def _make_video(self):
        return Video.objects.create(
            title="Admin Test Video",
            category="Forward",
            description="d",
            video_url="https://www.youtube.com/watch?v=PLACEHOLDER",
            is_placeholder_video=True,
            status=Video.Status.DRAFT,
        )

    def test_admin_index_reachable(self):
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)

    def test_publish_action_publishes_video(self):
        video = self._make_video()
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
