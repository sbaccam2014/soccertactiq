from django.urls import include, path

from . import views

urlpatterns = [
    path("auth/me/", views.CurrentUserView.as_view(), name="current-user"),
    path("", include("content.urls")),
    path("", include("progress.urls")),
]
