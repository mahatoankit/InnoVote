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
                "category": "education_learning",
            },
            {
                "title": "Precision Agriculture IoT Platform",
                "description": "A comprehensive IoT system that monitors soil conditions, weather patterns, and crop health to optimize farming operations and increase yield.",
                "category": "agriculture",
            },
            {
                "title": "Sports Performance Analytics App",
                "description": "A mobile application that uses AI and wearable sensors to analyze athletic performance, prevent injuries, and optimize training routines.",
                "category": "sports",
            },
            {
                "title": "Legal Document AI Assistant",
                "description": "An AI-powered platform that helps lawyers analyze legal documents, identify potential security vulnerabilities, and ensure compliance with cybersecurity regulations.",
                "category": "legal_cybersecurity",
            },
            {
                "title": "Personalized Wellness Companion",
                "description": "An AI health assistant that provides personalized wellness recommendations based on user health data, lifestyle patterns, and medical history.",
                "category": "health_wellness",
            },
            {
                "title": "Blockchain Invoice Management",
                "description": "A decentralized platform for businesses to manage invoices, payments, and financial transactions using blockchain technology for enhanced security and transparency.",
                "category": "financial_business",
            },
            {
                "title": "Public Service Information Hub",
                "description": "A comprehensive digital platform that provides citizens with easy access to government services, information, and real-time updates on public policies.",
                "category": "public_services",
            },
            {
                "title": "AI-Powered Career Development Platform",
                "description": "An intelligent platform that matches job seekers with opportunities, provides skill recommendations, and offers personalized career development paths.",
                "category": "human_resources",
            },
            {
                "title": "Smart Home Energy Optimization",
                "description": "An IoT-based system that monitors and optimizes home energy consumption, integrates renewable energy sources, and promotes sustainable living practices.",
                "category": "smart_living",
            },
            {
                "title": "Multilingual AI Translation Engine",
                "description": "An advanced natural language processing system that provides real-time, context-aware translations and supports emerging languages and dialects.",
                "category": "language_ai",
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
