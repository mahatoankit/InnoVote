from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.utils import timezone
from .models import Project, VotingID, Vote, Feedback, VotingSession, AdminLog
import json


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def home(request):
    """Home page showing all projects"""
    # Get voting session status
    voting_session = VotingSession.objects.first()
    if not voting_session:
        voting_session = VotingSession.objects.create()

    projects = Project.objects.all().order_by("title")

    context = {
        "projects": projects,
        "voting_session": voting_session,
        "total_projects": projects.count(),
    }

    return render(request, "voting/home.html", context)


def project_detail(request, project_id):
    """Project detail page"""
    project = get_object_or_404(Project, id=project_id)
    voting_session = VotingSession.objects.first()

    context = {
        "project": project,
        "voting_session": voting_session,
    }

    return render(request, "voting/project_detail.html", context)


@require_http_methods(["POST"])
def vote(request):
    """Handle voting"""
    data = json.loads(request.body)
    voting_code = data.get("voting_code", "").strip().upper()
    project_id = data.get("project_id")

    # Check if voting is active
    voting_session = VotingSession.objects.first()
    if not voting_session or not voting_session.is_active:
        return JsonResponse(
            {"success": False, "message": "Voting is currently not active."}
        )

    # Validate voting code
    try:
        voting_id = VotingID.objects.get(code=voting_code)
    except VotingID.DoesNotExist:
        return JsonResponse({"success": False, "message": "Invalid voting code."})

    # Check if already used
    if voting_id.used:
        return JsonResponse(
            {"success": False, "message": "This voting code has already been used."}
        )

    # Validate project
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return JsonResponse({"success": False, "message": "Invalid project."})

    # Create vote and mark voting ID as used
    vote = Vote.objects.create(
        project=project, voting_id=voting_id, ip_address=get_client_ip(request)
    )

    voting_id.mark_as_used()

    return JsonResponse(
        {
            "success": True,
            "message": f'Your vote for "{project.title}" has been recorded successfully!',
        }
    )


@require_http_methods(["POST"])
def submit_feedback(request):
    """Handle feedback submission"""
    data = json.loads(request.body)
    project_id = data.get("project_id")
    feedback_text = data.get("feedback_text", "").strip()

    if not feedback_text:
        return JsonResponse({"success": False, "message": "Feedback text is required."})

    # Validate project
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return JsonResponse({"success": False, "message": "Invalid project."})

    # Create feedback
    feedback = Feedback.objects.create(
        project=project, feedback_text=feedback_text, ip_address=get_client_ip(request)
    )

    return JsonResponse(
        {
            "success": True,
            "message": f'Your feedback for "{project.title}" has been submitted successfully!',
        }
    )


def results(request):
    """Show voting results if enabled"""
    voting_session = VotingSession.objects.first()

    if not voting_session or not voting_session.show_results:
        return render(request, "voting/results_hidden.html")

    # Get projects with vote counts
    projects_with_votes = Project.objects.annotate(vote_count=Count("votes")).order_by(
        "-vote_count", "title"
    )

    # Calculate total votes
    total_votes = Vote.objects.count()

    context = {
        "projects": projects_with_votes,
        "total_votes": total_votes,
        "voting_session": voting_session,
    }

    return render(request, "voting/results.html", context)


@staff_member_required
def generate_voting_ids(request):
    """Admin view to generate voting IDs"""
    if request.method == "POST":
        try:
            count = int(request.POST.get("count", 0))
            if count <= 0 or count > 1000:
                messages.error(request, "Please enter a number between 1 and 1000.")
                return redirect("admin:voting_votingid_changelist")

            # Generate voting IDs
            generated_codes = []
            for _ in range(count):
                code = VotingID.generate_unique_code()
                voting_id = VotingID.objects.create(code=code)
                generated_codes.append(code)

            # Log the action
            AdminLog.objects.create(
                user=request.user,
                action="generate_ids",
                description=f"Generated {count} voting IDs",
                ip_address=get_client_ip(request),
            )

            messages.success(request, f"Successfully generated {count} voting IDs.")
            return redirect("admin:voting_votingid_changelist")

        except ValueError:
            messages.error(request, "Invalid number format.")
            return redirect("admin:voting_votingid_changelist")

    return render(request, "admin/generate_voting_ids.html")


def analytics_api(request):
    """API endpoint for real-time analytics"""
    if not request.user.is_staff:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    # Get voting statistics
    total_votes = Vote.objects.count()
    total_feedbacks = Feedback.objects.count()
    total_projects = Project.objects.count()
    total_voting_ids = VotingID.objects.count()
    used_voting_ids = VotingID.objects.filter(used=True).count()

    # Get votes per project
    projects_data = []
    for project in Project.objects.all():
        projects_data.append(
            {
                "name": project.title,
                "votes": project.get_vote_count(),
                "feedbacks": project.get_feedback_count(),
            }
        )

    # Get recent votes (last 10)
    recent_votes = []
    for vote in Vote.objects.select_related("project", "voting_id").order_by(
        "-timestamp"
    )[:10]:
        recent_votes.append(
            {
                "project": vote.project.title,
                "voting_code": vote.voting_id.code,
                "timestamp": vote.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    return JsonResponse(
        {
            "total_votes": total_votes,
            "total_feedbacks": total_feedbacks,
            "total_projects": total_projects,
            "total_voting_ids": total_voting_ids,
            "used_voting_ids": used_voting_ids,
            "projects": projects_data,
            "recent_votes": recent_votes,
        }
    )


def check_voting_status(request):
    """API endpoint to check voting status"""
    voting_session = VotingSession.objects.first()

    return JsonResponse(
        {
            "is_active": voting_session.is_active if voting_session else False,
            "show_results": voting_session.show_results if voting_session else False,
        }
    )
