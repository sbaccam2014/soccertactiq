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
        "position-videos/",
        views.PositionVideoListView.as_view(),
        name="position-video-list",
    ),
]
