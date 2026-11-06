from django.urls import path

from . import views

urlpatterns = [
    path(
        "parent/children/",
        views.LinkedChildListView.as_view(),
        name="parent-child-list",
    ),
    path(
        "parent/children/<int:player_profile_id>/",
        views.LinkedChildDetailView.as_view(),
        name="parent-child-detail",
    ),
]
