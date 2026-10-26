from django.urls import path

from . import views

urlpatterns = [
    path("lessons/", views.PublishedLessonListView.as_view(), name="lesson-list"),
    path(
        "lessons/<int:pk>/",
        views.PublishedLessonDetailView.as_view(),
        name="lesson-detail",
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
