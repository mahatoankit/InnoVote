from django.core.management.base import BaseCommand
from voting.models import Project, Member, VotingSession, VotingID
import random


class Command(BaseCommand):
    help = "Create sample data for testing the voting system"

    def add_arguments(self, parser):
        parser.add_argument(
            "--projects",
            type=int,
            default=5,
            help="Number of sample projects to create",
        )
        parser.add_argument(
            "--voting-ids",
            type=int,
            default=20,
            help="Number of voting IDs to generate",
        )

    def handle(self, *args, **options):
        # Create voting session
        voting_session, created = VotingSession.objects.get_or_create(
            defaults={
                "name": "College Exhibition Voting 2025",
                "is_active": True,
                "show_results": False,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Created voting session"))
        else:
            self.stdout.write("Voting session already exists")

        # Sample project data
        sample_projects = [
            {
                "title": "Smart Campus Management System",
                "description": "An AI-powered system to manage campus facilities, track resources, and optimize energy consumption using IoT sensors and machine learning algorithms.",
                "category": "tech",
            },
            {
                "title": "Eco-Friendly Water Purification",
                "description": "A sustainable water purification system using solar energy and natural filtration methods to provide clean drinking water for rural communities.",
                "category": "environment",
            },
            {
                "title": "Mental Health Support App",
                "description": "A mobile application providing 24/7 mental health support through AI chatbots, peer connections, and professional counseling services.",
                "category": "health",
            },
            {
                "title": "Interactive Learning Platform",
                "description": "An immersive educational platform using AR/VR technology to make learning more engaging and accessible for students with different learning styles.",
                "category": "education",
            },
            {
                "title": "Community Food Sharing Network",
                "description": "A blockchain-based platform connecting food donors with those in need, reducing food waste and addressing hunger in local communities.",
                "category": "social",
            },
            {
                "title": "Automated Farming Assistant",
                "description": "A robotic system that monitors crop health, optimizes irrigation, and predicts harvest times using computer vision and weather data.",
                "category": "tech",
            },
            {
                "title": "Renewable Energy Grid",
                "description": "A smart grid system that efficiently distributes renewable energy from multiple sources to residential and commercial areas.",
                "category": "environment",
            },
            {
                "title": "Personalized Medicine Portal",
                "description": "A web platform that analyzes genetic data to provide personalized treatment recommendations and medication dosages.",
                "category": "health",
            },
        ]

        # Sample team members
        sample_members = [
            {"name": "Alex Johnson", "role": "Team Leader"},
            {"name": "Sarah Chen", "role": "Software Developer"},
            {"name": "Michael Brown", "role": "UI/UX Designer"},
            {"name": "Emily Davis", "role": "Data Scientist"},
            {"name": "David Wilson", "role": "Hardware Engineer"},
            {"name": "Jessica Lee", "role": "Project Manager"},
            {"name": "Kevin Martinez", "role": "Backend Developer"},
            {"name": "Ashley Taylor", "role": "Frontend Developer"},
            {"name": "Ryan Anderson", "role": "Research Analyst"},
            {"name": "Megan Thompson", "role": "Quality Assurance"},
        ]

        # Create projects
        projects_to_create = min(options["projects"], len(sample_projects))
        created_projects = 0

        for i in range(projects_to_create):
            project_data = sample_projects[i]
            project, created = Project.objects.get_or_create(
                title=project_data["title"],
                defaults={
                    "description": project_data["description"],
                    "category": project_data["category"],
                },
            )

            if created:
                created_projects += 1
                # Add 2-4 random team members to each project
                num_members = random.randint(2, 4)
                selected_members = random.sample(sample_members, num_members)

                for member_data in selected_members:
                    Member.objects.create(
                        project=project,
                        name=member_data["name"],
                        role=member_data["role"],
                        email=f"{member_data['name'].lower().replace(' ', '.')}@example.com",
                    )

        self.stdout.write(
            self.style.SUCCESS(f"Created {created_projects} new projects")
        )

        # Generate voting IDs
        existing_ids = VotingID.objects.count()
        ids_to_generate = options["voting_ids"]

        generated_count = 0
        for _ in range(ids_to_generate):
            code = VotingID.generate_unique_code()
            voting_id, created = VotingID.objects.get_or_create(code=code)
            if created:
                generated_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Generated {generated_count} new voting IDs")
        )
        self.stdout.write(
            self.style.SUCCESS(f"Total voting IDs: {VotingID.objects.count()}")
        )

        self.stdout.write(self.style.SUCCESS("\nSample data creation completed!"))
        self.stdout.write("You can now:")
        self.stdout.write("1. Start the development server: python manage.py runserver")
        self.stdout.write("2. Access admin panel: http://localhost:8000/admin/")
        self.stdout.write("3. View the voting interface: http://localhost:8000/")
