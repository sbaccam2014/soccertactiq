from django.urls import path

from . import views

urlpatterns = [
    path("videos/", views.PublishedVideoListView.as_view(), name="video-list"),
    path(
        "videos/<int:pk>/",
        views.PublishedVideoDetailView.as_view(),
        name="video-detail",
    ),
    path(
        "category-videos/",
        views.CategoryVideoListView.as_view(),
        name="category-video-list",
    ),
    path(
        "video-categories/",
        views.VideoCategoryListView.as_view(),
        name="video-category-list",
    ),
]
