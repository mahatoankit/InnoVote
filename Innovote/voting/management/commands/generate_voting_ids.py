from django.core.management.base import BaseCommand
from voting.models import VotingID


class Command(BaseCommand):
    help = "Generate unique voting IDs for the exhibition"

    def add_arguments(self, parser):
        parser.add_argument("count", type=int, help="Number of voting IDs to generate")
        parser.add_argument(
            "--export", action="store_true", help="Export generated IDs to CSV file"
        )

    def handle(self, *args, **options):
        count = options["count"]
        export = options["export"]

        if count <= 0:
            self.stdout.write(self.style.ERROR("Count must be a positive integer"))
            return

        if count > 1000:
            self.stdout.write(
                self.style.ERROR("Cannot generate more than 1000 IDs at once")
            )
            return

        generated_codes = []

        self.stdout.write(f"Generating {count} voting IDs...")

        for i in range(count):
            code = VotingID.generate_unique_code()
            voting_id = VotingID.objects.create(code=code)
            generated_codes.append(code)

            if (i + 1) % 100 == 0:
                self.stdout.write(f"Generated {i + 1} IDs...")

        self.stdout.write(
            self.style.SUCCESS(f"Successfully generated {count} voting IDs")
        )

        if export:
            import csv
            from datetime import datetime

            filename = f'voting_ids_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

            with open(filename, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Voting Code", "Status"])

                for code in generated_codes:
                    writer.writerow([code, "Unused"])

            self.stdout.write(self.style.SUCCESS(f"Exported voting IDs to {filename}"))

        # Display some sample codes
        self.stdout.write("\nSample generated codes:")
        for code in generated_codes[:10]:
            self.stdout.write(f"  {code}")

        if len(generated_codes) > 10:
            self.stdout.write(f"  ... and {len(generated_codes) - 10} more")

        self.stdout.write(
            f"\nTotal unused voting IDs in database: {VotingID.objects.filter(used=False).count()}"
        )
