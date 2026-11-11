from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from accounts.models import PlayerProfile, Team
from content.models import Video

User = get_user_model()


def make_video(**overrides):
    defaults = dict(
        title="Test Video",
        category="Defense",
        description="desc",
        video_url="https://www.youtube.com/watch?v=PLACEHOLDER",
        is_placeholder_video=True,
        status=Video.Status.PUBLISHED,
    )
    defaults.update(overrides)
    return Video.objects.create(**defaults)


def make_player(username, team=None):
    user = User.objects.create_user(username=username, password="x")
    profile = PlayerProfile.objects.get(user=user)
    if team is not None:
        profile.team = team
        profile.save()
    return profile


class AssignedVideoListTests(APITestCase):
    """
    Covers: the player-facing "assigned to me" list — additive only
    (never hides anything from the main /api/videos/ library), and
    correctly includes videos assigned to the player's team.
    """

    def test_video_assigned_directly_to_player_appears(self):
        player = make_player("player1")
        self.client.force_authenticate(user=player.user)
        video = make_video()
        video.assigned_players.add(player)

        response = self.client.get("/api/videos/assigned/")
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["id"], video.id)

    def test_video_assigned_to_players_team_appears(self):
        team = Team.objects.create(name="U12 Red")
        player = make_player("player1", team=team)
        self.client.force_authenticate(user=player.user)
        video = make_video()
        video.assigned_teams.add(team)

        response = self.client.get("/api/videos/assigned/")
        self.assertEqual(response.json()["count"], 1)

    def test_video_assigned_to_different_team_does_not_appear(self):
        team = Team.objects.create(name="U12 Red")
        other_team = Team.objects.create(name="U12 Blue")
        player = make_player("player1", team=team)
        self.client.force_authenticate(user=player.user)
        video = make_video()
        video.assigned_teams.add(other_team)

        response = self.client.get("/api/videos/assigned/")
        self.assertEqual(response.json()["count"], 0)

    def test_unassigned_video_does_not_appear_in_assigned_list(self):
        player = make_player("player1")
        self.client.force_authenticate(user=player.user)
        make_video()

        response = self.client.get("/api/videos/assigned/")
        self.assertEqual(response.json()["count"], 0)

    def test_unassigned_video_still_appears_in_global_library(self):
        """Assignment is additive — it never removes a video from the main library."""
        player = make_player("player1")
        self.client.force_authenticate(user=player.user)
        video = make_video()
        video.assigned_players.add(make_player("other-player"))

        response = self.client.get("/api/videos/")
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["id"], video.id)

    def test_draft_assigned_video_does_not_appear(self):
        player = make_player("player1")
        self.client.force_authenticate(user=player.user)
        video = make_video(status=Video.Status.DRAFT)
        video.assigned_players.add(player)

        response = self.client.get("/api/videos/assigned/")
        self.assertEqual(response.json()["count"], 0)
