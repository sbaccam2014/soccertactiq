from django.urls import path

from . import views

urlpatterns = [
    path(
        "lessons/<int:lesson_id>/attempts/",
        views.SubmitAttemptView.as_view(),
        name="attempt-submit",
    ),
    path(
        "attempts/<int:pk>/",
        views.AttemptDetailView.as_view(),
        name="attempt-detail",
    ),
    path("progress/", views.MyProgressView.as_view(), name="my-progress"),
]
