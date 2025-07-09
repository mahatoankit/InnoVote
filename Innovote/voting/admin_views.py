from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test
import json
import csv
from datetime import datetime

from voting.models import (
    Project,
    VotingID,
    Vote,
    Feedback,
    VotingSession,
    AdminLog,
    Member,
)
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


# Custom decorator for admin access that requires fresh authentication
def admin_required(view_func):
    """
    Decorator for views that require admin access with fresh authentication.
    Always redirects to login page to verify credentials.
    """

    def wrapper(request, *args, **kwargs):
        # Check if user has fresh admin session
        if not request.session.get("admin_authenticated", False):
            return redirect("voting:admin_login")

        # Check if user is still staff
        if not (request.user.is_authenticated and request.user.is_staff):
            # Clear admin session if user is no longer staff
            request.session.pop("admin_authenticated", None)
            return redirect("voting:admin_login")

        return view_func(request, *args, **kwargs)

    return wrapper


def admin_login(request):
    """Custom admin login - always requires fresh credentials"""
    # Always show login form, never skip
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            messages.error(request, "Please provide both username and password.")
            return render(request, "admin/login.html")

        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)

            # Set admin session flag
            request.session["admin_authenticated"] = True
            request.session["admin_login_time"] = timezone.now().isoformat()

            messages.success(
                request, f"Welcome back, {user.first_name or user.username}!"
            )

            # Log the login action
            AdminLog.objects.create(
                user=user,
                action="login",
                description=f"Admin logged in: {username}",
                ip_address=get_client_ip(request),
            )

            return redirect("voting:admin_dashboard")
        else:
            messages.error(
                request,
                "Invalid credentials or insufficient permissions. Only staff members can access the admin dashboard.",
            )

    return render(request, "admin/login.html")


def admin_logout(request):
    """Admin logout view - clears admin session"""
    if request.user.is_authenticated:
        # Log the logout action
        AdminLog.objects.create(
            user=request.user,
            action="logout",
            description=f"Admin logged out: {request.user.username}",
            ip_address=get_client_ip(request),
        )

    # Clear admin session
    request.session.pop("admin_authenticated", None)
    request.session.pop("admin_login_time", None)

    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("voting:home")


@admin_required
def admin_dashboard(request):
    """Custom admin dashboard - Requires staff authentication"""
    # Get statistics
    total_projects = Project.objects.count()
    total_votes = Vote.objects.count()
    total_participants = VotingID.objects.filter(used=True).count()
    total_feedback = Feedback.objects.count()

    # Get voting session
    voting_session = VotingSession.objects.first()
    if not voting_session:
        voting_session = VotingSession.objects.create()

    # Get all projects with vote counts
    projects = Project.objects.all().order_by("-id")

    # Get recent admin logs
    recent_logs = AdminLog.objects.select_related("user").order_by("-timestamp")[:10]

    context = {
        "total_projects": total_projects,
        "total_votes": total_votes,
        "total_participants": total_participants,
        "total_feedback": total_feedback,
        "voting_session": voting_session,
        "projects": projects,
        "recent_logs": recent_logs,
    }

    return render(request, "admin/dashboard.html", context)


@require_http_methods(["POST"])
def toggle_voting(request):
    """Toggle voting status"""
    try:
        data = json.loads(request.body)
        is_active = data.get("is_active", False)

        voting_session = VotingSession.objects.first()
        if not voting_session:
            voting_session = VotingSession.objects.create()

        voting_session.is_active = is_active
        voting_session.save()

        # Log the action (create a default user entry for demo)
        AdminLog.objects.create(
            user=None,  # Allow null user for demo
            action="stop_voting" if not is_active else "start_voting",
            description=f"Voting status changed to {'active' if is_active else 'inactive'}",
        )

        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@require_http_methods(["POST"])
def toggle_results(request):
    """Toggle results visibility"""
    try:
        data = json.loads(request.body)
        show_results = data.get("show_results", False)

        voting_session = VotingSession.objects.first()
        if not voting_session:
            voting_session = VotingSession.objects.create()

        voting_session.show_results = show_results
        voting_session.save()

        # Log the action
        AdminLog.objects.create(
            user=None,  # Allow null user for demo
            action="show_results" if show_results else "hide_results",
            description=f"Results visibility changed to {'visible' if show_results else 'hidden'}",
        )

        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@require_http_methods(["POST"])
def add_project(request):
    """Add new project"""
    try:
        title = request.POST.get("title")
        category = request.POST.get("category")
        description = request.POST.get("description")
        image = request.FILES.get("image")
        team_members_json = request.POST.get("team_members", "[]")

        if not all([title, category, description]):
            return JsonResponse(
                {"success": False, "message": "All fields are required"}
            )

        # Create project
        project = Project.objects.create(
            title=title, category=category, description=description, image=image
        )

        # Add team members
        try:
            team_members = json.loads(team_members_json)
            for member_data in team_members:
                if member_data.get("name"):
                    Member.objects.create(
                        project=project,
                        name=member_data["name"],
                        role=member_data.get("role", ""),
                        email="",  # Can be added later
                    )
        except json.JSONDecodeError:
            pass

        # Log the action (create a default admin log entry for demo)
        AdminLog.objects.create(
            user=None,  # Allow null user for demo
            action="project_created",
            description=f"Added project: {title}",
        )

        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


@require_http_methods(["DELETE"])
def delete_project(request, project_id):
    """Delete project"""
    try:
        project = get_object_or_404(Project, id=project_id)
        project_title = project.title

        # Delete associated votes and feedback
        Vote.objects.filter(project=project).delete()
        Feedback.objects.filter(project=project).delete()

        # Delete the project
        project.delete()

        # Log the action
        AdminLog.objects.create(
            user=None,  # Allow null user for demo
            action="project_deleted",
            description=f"Deleted project: {project_title}",
        )

        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@require_http_methods(["POST"])
def reset_votes(request):
    """Reset all votes"""
    try:
        vote_count = Vote.objects.count()

        # Delete all votes
        Vote.objects.all().delete()

        # Reset voting IDs to unused
        VotingID.objects.update(used=False, used_at=None)

        # Log the action
        AdminLog.objects.create(
            user=request.user,
            action="All votes reset",
            details=f"Reset {vote_count} votes",
        )

        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@require_http_methods(["POST"])
def generate_codes(request):
    """Generate voting codes"""
    try:
        data = json.loads(request.body)
        count = data.get("count", 50)

        if count > 1000:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Cannot generate more than 1000 codes at once",
                }
            )

        codes_generated = 0
        for _ in range(count):
            try:
                VotingID.objects.create()
                codes_generated += 1
            except:
                continue  # Skip if code already exists

        # Log the action
        AdminLog.objects.create(
            user=request.user,
            action="Voting codes generated",
            details=f"Generated {codes_generated} new voting codes",
        )

        return JsonResponse({"success": True, "generated": codes_generated})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


def export_results(request):
    """Export results as CSV"""
    try:
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="voting_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        )

        writer = csv.writer(response)
        writer.writerow(
            ["Project Title", "Category", "Description", "Vote Count", "Team Members"]
        )

        projects = Project.objects.all().order_by("-id")
        for project in projects:
            team_members = ", ".join(
                [f"{member.name} ({member.role})" for member in project.members.all()]
            )
            writer.writerow(
                [
                    project.title,
                    project.get_category_display(),
                    project.description,
                    project.get_vote_count(),
                    team_members,
                ]
            )

        # Log the action
        AdminLog.objects.create(
            user=request.user,
            action="Results exported",
            details="Exported voting results as CSV",
        )

        return response
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@admin_required
@require_http_methods(["POST"])
def clear_cache(request):
    """Clear application cache"""
    try:
        cache.clear()

        # Log the action
        AdminLog.objects.create(
            user=request.user,
            action="Cache cleared",
            details="Application cache cleared",
        )

        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@admin_required
def project_management(request):
    """Project management page"""
    projects = Project.objects.all().order_by("-id")
    return render(request, "admin/projects.html", {"projects": projects})


@admin_required
def voting_codes_management(request):
    """Voting codes management page"""
    voting_ids = VotingID.objects.all().order_by("-created_at")
    total_codes = voting_ids.count()
    used_codes = voting_ids.filter(used=True).count()
    unused_codes = total_codes - used_codes

    context = {
        "voting_ids": voting_ids,
        "total_codes": total_codes,
        "used_codes": used_codes,
        "unused_codes": unused_codes,
    }

    return render(request, "admin/voting_codes.html", context)


@admin_required
def analytics_dashboard(request):
    """Analytics dashboard"""
    # Voting statistics
    vote_stats = (
        Vote.objects.values("project__title")
        .annotate(vote_count=Count("id"))
        .order_by("-vote_count")
    )

    # Daily vote counts (last 7 days)
    from datetime import timedelta

    daily_votes = []
    for i in range(7):
        date = timezone.now().date() - timedelta(days=i)
        count = Vote.objects.filter(timestamp__date=date).count()
        daily_votes.append({"date": date.strftime("%Y-%m-%d"), "count": count})

    # Category statistics
    category_stats = Project.objects.values("category").annotate(
        project_count=Count("id")
    )

    context = {
        "vote_stats": vote_stats,
        "daily_votes": list(reversed(daily_votes)),
        "category_stats": category_stats,
    }

    return render(request, "admin/analytics.html", context)


@require_http_methods(["GET", "POST"])
def admin_login_old(request):
    """Old admin login - deprecated"""
    return redirect("voting:admin_login")


@admin_required
def create_project(request):
    """Create a new project"""
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        category = request.POST.get("category", "other")

        # Validate required fields
        if not title:
            messages.error(request, "Project title is required.")
            return render(
                request,
                "admin/create_project.html",
                {"categories": Project.CATEGORY_CHOICES, "form_data": request.POST},
            )

        if not description:
            messages.error(request, "Project description is required.")
            return render(
                request,
                "admin/create_project.html",
                {"categories": Project.CATEGORY_CHOICES, "form_data": request.POST},
            )

        # Create the project
        project = Project.objects.create(
            title=title, description=description, category=category
        )

        # Handle team members
        member_names = request.POST.getlist("member_names[]")
        member_roles = request.POST.getlist("member_roles[]")

        for name, role in zip(member_names, member_roles):
            if name.strip():
                Member.objects.create(
                    project=project,
                    name=name.strip(),
                    role=role.strip() if role.strip() else "Team Member",
                )

        # Log the action
        AdminLog.objects.create(
            user=request.user,
            action="create_project",
            description=f"Created project: {title}",
            ip_address=get_client_ip(request),
        )

        messages.success(request, f"Project '{title}' created successfully!")
        return redirect("voting:admin_dashboard")

    context = {"categories": Project.CATEGORY_CHOICES}
    return render(request, "admin/create_project.html", context)


@admin_required
def edit_project(request, project_id):
    """Edit an existing project"""
    project = get_object_or_404(Project, id=project_id)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        category = request.POST.get("category", "other")

        # Validate required fields
        if not title:
            messages.error(request, "Project title is required.")
            return render(
                request,
                "admin/edit_project.html",
                {
                    "project": project,
                    "categories": Project.CATEGORY_CHOICES,
                    "form_data": request.POST,
                },
            )

        if not description:
            messages.error(request, "Project description is required.")
            return render(
                request,
                "admin/edit_project.html",
                {
                    "project": project,
                    "categories": Project.CATEGORY_CHOICES,
                    "form_data": request.POST,
                },
            )

        # Update the project
        project.title = title
        project.description = description
        project.category = category
        project.save()

        # Handle team members - remove existing and add new ones
        project.members.all().delete()
        member_names = request.POST.getlist("member_names[]")
        member_roles = request.POST.getlist("member_roles[]")

        for name, role in zip(member_names, member_roles):
            if name.strip():
                Member.objects.create(
                    project=project,
                    name=name.strip(),
                    role=role.strip() if role.strip() else "Team Member",
                )

        # Log the action
        AdminLog.objects.create(
            user=request.user,
            action="edit_project",
            description=f"Updated project: {title}",
            ip_address=get_client_ip(request),
        )

        messages.success(request, f"Project '{title}' updated successfully!")
        return redirect("voting:admin_dashboard")

    context = {
        "project": project,
        "categories": Project.CATEGORY_CHOICES,
        "members": project.members.all(),
    }
    return render(request, "admin/edit_project.html", context)


@admin_required
def delete_project_view(request, project_id):
    """Delete a project"""
    project = get_object_or_404(Project, id=project_id)

    if request.method == "POST":
        project_title = project.title

        # Delete the project (cascade will handle votes, feedback, and members)
        project.delete()

        # Log the action
        AdminLog.objects.create(
            user=request.user,
            action="delete_project",
            description=f"Deleted project: {project_title}",
            ip_address=get_client_ip(request),
        )

        messages.success(request, f"Project '{project_title}' deleted successfully!")
        return redirect("voting:admin_dashboard")

    return render(request, "admin/delete_project.html", {"project": project})


def clear_admin_session(request):
    """Clear admin session when navigating away from admin"""
    if "admin_authenticated" in request.session:
        request.session.pop("admin_authenticated", None)
        request.session.pop("admin_login_time", None)
    return JsonResponse({"success": True})


# Add this to views that should clear admin session
def public_view_wrapper(view_func):
    """Wrapper for public views that clears admin session"""

    def wrapper(request, *args, **kwargs):
        # Clear admin session when accessing public views
        if "admin_authenticated" in request.session:
            request.session.pop("admin_authenticated", None)
            request.session.pop("admin_login_time", None)
        return view_func(request, *args, **kwargs)

    return wrapper


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
