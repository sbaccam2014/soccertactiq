from django.urls import path

from . import views

urlpatterns = [
    path(
        "videos/<int:video_id>/watch/",
        views.MarkVideoWatchedView.as_view(),
        name="video-watch",
    ),
    path("progress/", views.MyProgressView.as_view(), name="my-progress"),
]
