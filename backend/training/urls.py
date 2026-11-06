from django.urls import path

from . import views

urlpatterns = [
    path(
        "training/today/",
        views.TodayTrainingView.as_view(),
        name="training-today",
    ),
    path("training/", views.TrainingHistoryView.as_view(), name="training-history"),
    path(
        "training/calendar/",
        views.TrainingCalendarView.as_view(),
        name="training-calendar",
    ),
    path(
        "training/<str:date>/",
        views.DayTrainingView.as_view(),
        name="training-day",
    ),
]
