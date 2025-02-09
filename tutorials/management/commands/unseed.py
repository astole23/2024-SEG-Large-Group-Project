from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tutorials.models.jobposting import JobPosting
from tutorials.models.accounts import Company

User = get_user_model()

class Command(BaseCommand):
    """Command to delete all non-staff users, job postings, and companies from the database."""
    
    help = 'Removes all non-staff users, job postings, and companies from the database.'

    def handle(self, *args, **options):
        """Execute the unseeding operation."""

        # Delete non-staff users
        deleted_users, _ = User.objects.filter(is_staff=False).delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_users} non-staff users.'))

        # Delete job postings
        deleted_jobs, _ = JobPosting.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_jobs} job postings.'))

        # Delete companies
        deleted_companies, _ = Company.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_companies} companies.'))
