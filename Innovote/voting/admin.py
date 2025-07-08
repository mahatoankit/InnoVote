from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.html import format_html
from .models import Project, Member, VotingID, Vote, Feedback, AdminLog, VotingSession
import csv


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def log_admin_action(user, action, description="", ip_address=""):
    """Helper function to log admin actions"""
    AdminLog.objects.create(
        user=user, action=action, description=description, ip_address=ip_address
    )


class MemberInline(admin.TabularInline):
    model = Member
    extra = 1


@admin.register(VotingSession)
class VotingSessionAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", "show_results", "created_at", "updated_at"]
    list_filter = ["is_active", "show_results"]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Log the action
        action = "show_results" if obj.show_results else "hide_results"
        if obj.is_active:
            action = "start_voting"
        else:
            action = "stop_voting"

        log_admin_action(
            user=request.user,
            action=action,
            description=f"Updated voting session: {obj.name}",
            ip_address=get_client_ip(request),
        )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "category",
        "get_vote_count",
        "get_feedback_count",
        "created_at",
    ]
    list_filter = ["category", "created_at"]
    search_fields = ["title", "description"]
    inlines = [MemberInline]

    def get_vote_count(self, obj):
        return obj.get_vote_count()

    get_vote_count.short_description = "Votes"

    def get_feedback_count(self, obj):
        return obj.get_feedback_count()

    get_feedback_count.short_description = "Feedbacks"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        action = "project_updated" if change else "project_created"
        log_admin_action(
            user=request.user,
            action=action,
            description=f"Project: {obj.title}",
            ip_address=get_client_ip(request),
        )

    def delete_model(self, request, obj):
        log_admin_action(
            user=request.user,
            action="project_deleted",
            description=f"Project: {obj.title}",
            ip_address=get_client_ip(request),
        )
        super().delete_model(request, obj)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ["name", "project", "role", "email"]
    list_filter = ["project", "role"]
    search_fields = ["name", "email", "project__title"]


@admin.register(VotingID)
class VotingIDAdmin(admin.ModelAdmin):
    list_display = ["code", "used", "created_at", "used_at"]
    list_filter = ["used", "created_at"]
    search_fields = ["code"]
    readonly_fields = ["used_at"]

    actions = ["generate_voting_ids", "export_unused_ids"]

    def generate_voting_ids(self, request, queryset):
        """Admin action to generate voting IDs"""
        from django.http import HttpResponseRedirect
        from django.urls import reverse

        # Redirect to a custom view for generating IDs
        return HttpResponseRedirect(reverse("admin:generate_voting_ids"))

    generate_voting_ids.short_description = "Generate new voting IDs"

    def export_unused_ids(self, request, queryset):
        """Export unused voting IDs to CSV"""
        unused_ids = VotingID.objects.filter(used=False)

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="unused_voting_ids.csv"'

        writer = csv.writer(response)
        writer.writerow(["Voting Code", "Created At"])

        for voting_id in unused_ids:
            writer.writerow([voting_id.code, voting_id.created_at])

        return response

    export_unused_ids.short_description = "Export unused voting IDs to CSV"


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ["project", "voting_id", "timestamp", "ip_address"]
    list_filter = ["timestamp", "project"]
    search_fields = ["project__title", "voting_id__code"]
    readonly_fields = ["project", "voting_id", "timestamp", "ip_address"]

    def has_add_permission(self, request):
        # Prevent manual vote creation
        return False

    def has_change_permission(self, request, obj=None):
        # Prevent vote modification
        return False


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ["project", "feedback_preview", "timestamp", "is_anonymous"]
    list_filter = ["timestamp", "project", "is_anonymous"]
    search_fields = ["project__title", "feedback_text"]
    readonly_fields = ["project", "feedback_text", "timestamp", "ip_address"]

    def feedback_preview(self, obj):
        return (
            obj.feedback_text[:50] + "..."
            if len(obj.feedback_text) > 50
            else obj.feedback_text
        )

    feedback_preview.short_description = "Feedback Preview"

    def has_add_permission(self, request):
        # Prevent manual feedback creation
        return False

    def has_change_permission(self, request, obj=None):
        # Prevent feedback modification
        return False


@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = ["user", "action", "timestamp", "ip_address"]
    list_filter = ["action", "timestamp", "user"]
    search_fields = ["user__username", "description"]
    readonly_fields = ["user", "action", "description", "timestamp", "ip_address"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# Customize admin site
admin.site.site_header = "InnoVote Administration"
admin.site.site_title = "InnoVote Admin"
admin.site.index_title = "Welcome to InnoVote Administration"
