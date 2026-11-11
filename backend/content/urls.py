from django.urls import path

from . import views

urlpatterns = [
    path("videos/", views.PublishedVideoListView.as_view(), name="video-list"),
    path(
        "videos/assigned/",
        views.AssignedVideoListView.as_view(),
        name="video-assigned-list",
    ),
    path(
        "videos/<int:pk>/",
        views.PublishedVideoDetailView.as_view(),
        name="video-detail",
    ),
    path(
        "video-categories/",
        views.VideoCategoryListView.as_view(),
        name="video-category-list",
    ),
]
