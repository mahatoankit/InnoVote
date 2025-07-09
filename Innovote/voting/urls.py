from django.urls import path
from . import views
from . import admin_views

app_name = "voting"

urlpatterns = [
    path("", views.home, name="home"),
    path("project/<int:project_id>/", views.project_detail, name="project_detail"),
    path("vote/", views.vote, name="vote"),
    path("feedback/", views.submit_feedback, name="submit_feedback"),
    path("results/", views.results, name="results"),
    path("analytics/", views.analytics_api, name="analytics_api"),
    path("public-analytics/", views.public_analytics_api, name="public_analytics_api"),
    path("status/", views.check_voting_status, name="voting_status"),
    path("generate-ids/", views.generate_voting_ids, name="generate_voting_ids"),
    # Admin authentication
    path("admin-login/", admin_views.admin_login, name="admin_login"),
    path("admin-logout/", admin_views.admin_logout, name="admin_logout"),
    path(
        "clear-admin-session/",
        admin_views.clear_admin_session,
        name="clear_admin_session",
    ),
    # Admin dashboard URLs
    path("dashboard/", admin_views.admin_dashboard, name="admin_dashboard"),
    path("create-project/", admin_views.create_project, name="create_project"),
    path(
        "edit-project/<int:project_id>/", admin_views.edit_project, name="edit_project"
    ),
    path(
        "delete-project/<int:project_id>/",
        admin_views.delete_project_view,
        name="delete_project",
    ),
    path("toggle-voting/", admin_views.toggle_voting, name="toggle_voting"),
    path("toggle-results/", admin_views.toggle_results, name="toggle_results"),
]
