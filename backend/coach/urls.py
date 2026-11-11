from django.urls import path

from . import views

urlpatterns = [
    path(
        "coach/players/",
        views.AssignedPlayerListView.as_view(),
        name="coach-player-list",
    ),
    path(
        "coach/players/<int:player_profile_id>/",
        views.AssignedPlayerDetailView.as_view(),
        name="coach-player-detail",
    ),
    path(
        "coach/videos/",
        views.CoachVideoListCreateView.as_view(),
        name="coach-video-list-create",
    ),
    path(
        "coach/videos/<int:pk>/",
        views.CoachVideoDetailView.as_view(),
        name="coach-video-detail",
    ),
    path(
        "coach/teams/",
        views.CoachTeamListView.as_view(),
        name="coach-team-list",
    ),
]
