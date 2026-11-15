from django.urls import path

from . import views

urlpatterns = [
    path("health/", views.health, name="health"),
    path("posts/", views.PostListCreateView.as_view(), name="post-list-create"),
    path(
        "analyses/",
        views.PostAnalysisListCreateView.as_view(),
        name="post-analysis-list-create",
    ),
]
