from django.urls import path
from . import views

app_name = "voting"

urlpatterns = [
    path("", views.home, name="home"),
    path("project/<int:project_id>/", views.project_detail, name="project_detail"),
    path("vote/", views.vote, name="vote"),
    path("feedback/", views.submit_feedback, name="submit_feedback"),
    path("results/", views.results, name="results"),
    path("analytics/", views.analytics_api, name="analytics_api"),
    path("status/", views.check_voting_status, name="voting_status"),
    path("admin/generate-ids/", views.generate_voting_ids, name="generate_voting_ids"),
]
