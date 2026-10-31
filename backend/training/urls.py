from django.urls import path

from . import views

urlpatterns = [
    path(
        "training/today/",
        views.TodayTrainingView.as_view(),
        name="training-today",
    ),
    path("training/", views.TrainingHistoryView.as_view(), name="training-history"),
]
