from django.urls import path
from .views import AnalyzeTasksView, SuggestTasksView

urlpatterns = [
    path("tasks/analyze/", AnalyzeTasksView.as_view(), name="tasks-analyze"),
    path("tasks/suggest/", SuggestTasksView.as_view(), name="tasks-suggest"),
]
