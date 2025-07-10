from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import string
import random


class VotingSession(models.Model):
    """Model to control voting session state"""

    name = models.CharField(max_length=100, default="College Exhibition Voting")
    is_active = models.BooleanField(
        default=False, help_text="Whether voting is currently active"
    )
    show_results = models.BooleanField(
        default=False, help_text="Whether results are visible to public"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Voting Session"
        verbose_name_plural = "Voting Sessions"

    def __str__(self):
        return f"{self.name} - {'Active' if self.is_active else 'Inactive'}"


class Project(models.Model):
    """Model for exhibition projects"""

    CATEGORY_CHOICES = [
        ("education_learning", "Education & Learning Technology"),
        ("agriculture", "Agriculture Technology"),
        ("sports", "Sports Technology"),
        ("legal_cybersecurity", "Legal & Cybersecurity AI"),
        ("health_wellness", "Health & Wellness AI"),
        ("financial_business", "Financial & Business Innovations"),
        ("public_services", "Public Services & Information"),
        ("human_resources", "Human Resources and Career Development"),
        ("smart_living", "Smart Living and Sustainability"),
        ("language_ai", "Language and Advanced AI Research"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(
        max_length=30, choices=CATEGORY_CHOICES, default="education_learning"
    )
    # image = models.ImageField(upload_to="project_images/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return self.title

    def get_vote_count(self):
        """Get total number of votes for this project"""
        return self.votes.count()

    def get_feedback_count(self):
        """Get total number of feedback submissions for this project"""
        return self.feedbacks.count()


class Member(models.Model):
    """Model for project team members"""

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="members"
    )
    name = models.CharField(max_length=100)
    role = models.CharField(
        max_length=100, blank=True, help_text="e.g., Team Leader, Developer, Designer"
    )
    email = models.EmailField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"

    def __str__(self):
        return f"{self.name} ({self.project.title})"


class VotingID(models.Model):
    """Model for unique voting IDs"""

    code = models.CharField(
        max_length=5, unique=True, help_text="5-character unique voting code"
    )
    used = models.BooleanField(default=False, help_text="Whether this ID has been used")
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["code"]
        verbose_name = "Voting ID"
        verbose_name_plural = "Voting IDs"

    def __str__(self):
        return f"{self.code} - {'Used' if self.used else 'Available'}"

    @classmethod
    def generate_unique_code(cls):
        """Generate a unique 5-character code using only uppercase letters A-Z"""
        chars = string.ascii_uppercase  # Only A-Z
        while True:
            code = "".join(random.choices(chars, k=5))
            if not cls.objects.filter(code=code).exists():
                return code

    def mark_as_used(self):
        """Mark this voting ID as used"""
        self.used = True
        self.used_at = timezone.now()
        self.save()


class Vote(models.Model):
    """Model for storing votes"""

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="votes")
    voting_id = models.ForeignKey(
        VotingID, on_delete=models.CASCADE, related_name="vote"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Vote"
        verbose_name_plural = "Votes"

    def __str__(self):
        return f"Vote for {self.project.title} by {self.voting_id.code}"


class Feedback(models.Model):
    """Model for feedback submissions"""

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="feedbacks"
    )
    feedback_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    is_anonymous = models.BooleanField(default=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Feedback"
        verbose_name_plural = "Feedbacks"

    def __str__(self):
        return f"Feedback for {self.project.title}"


class AdminLog(models.Model):
    """Model for logging admin activities"""

    ACTION_CHOICES = [
        ("start_voting", "Started Voting"),
        ("stop_voting", "Stopped Voting"),
        ("show_results", "Showed Results"),
        ("hide_results", "Hid Results"),
        ("generate_ids", "Generated Voting IDs"),
        ("create_project", "Created Project"),
        ("edit_project", "Updated Project"),
        ("delete_project", "Deleted Project"),
        ("login", "Admin Login"),
        ("logout", "Admin Logout"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="admin_logs", null=True, blank=True
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Admin Log"
        verbose_name_plural = "Admin Logs"

    def __str__(self):
        username = self.user.username if self.user else "System"
        return f"{username} - {self.action} at {self.timestamp}"
