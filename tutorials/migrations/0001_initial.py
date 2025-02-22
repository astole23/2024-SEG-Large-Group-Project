<<<<<<< Updated upstream
# Generated by Django 4.2 on 2025-01-31 00:14
=======
# Generated by Django 4.2 on 2025-02-22 18:15
>>>>>>> Stashed changes

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('industry', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=20)),
<<<<<<< Updated upstream
=======
                ('location', models.CharField(blank=True, help_text="Optional: Enter the company's location (up to 100 characters).", max_length=100, null=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='company_logos/')),
                ('description', models.TextField(blank=True, null=True)),
                ('unique_id', models.CharField(blank=True, max_length=5, null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='JobPosting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_title', models.CharField(help_text='The title of the job posting.', max_length=255)),
                ('company_name', models.CharField(help_text='The name of the company offering the job.', max_length=255)),
                ('child_company_name', models.CharField(blank=True, help_text='Child or subsidiary company name, if applicable.', max_length=255, null=True)),
                ('location', models.CharField(help_text='Location of the job (e.g., city, country, or remote).', max_length=255)),
                ('work_type', models.CharField(blank=True, choices=[('remote', 'Remote'), ('hybrid', 'Hybrid'), ('on_site', 'On-site')], help_text='Type of work (e.g., remote, hybrid, on-site).', max_length=50, null=True)),
                ('salary_range', models.CharField(blank=True, help_text='Salary offered for the job.', max_length=100, null=True)),
                ('contract_type', models.CharField(help_text='Type of contract for the job.', max_length=50)),
                ('job_overview', models.TextField(help_text='A brief overview of the job responsibilities and expectations.')),
                ('roles_responsibilities', models.TextField(help_text='Detailed list of job responsibilities and duties.')),
                ('required_skills', models.TextField(help_text='List of skills required for the job (comma-separated).')),
                ('preferred_skills', models.TextField(blank=True, help_text='List of preferred skills for the job (comma-separated).', null=True)),
                ('education_required', models.CharField(help_text='Minimum education level required for the job.', max_length=255)),
                ('perks', models.TextField(help_text='List of benefits and perks provided by the employer.')),
                ('application_deadline', models.CharField(help_text='Deadline for submitting job applications.', max_length=255)),
                ('required_documents', models.TextField(blank=True, help_text='Documents required for application.', null=True)),
                ('company_overview', models.TextField(blank=True, help_text='Brief information about the company.', null=True)),
                ('why_join_us', models.TextField(blank=True, help_text='Reasons why candidates should apply for this job.', null=True)),
                ('company_reviews', models.FloatField(blank=True, help_text='Average review rating of the company.', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Date and time when the job was posted.')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Date and time when the job details were last updated.')),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(max_length=2000)),
                ('rating', models.PositiveIntegerField(default=1)),
>>>>>>> Stashed changes
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(max_length=20)),
                ('password', models.CharField(max_length=255)),
            ],
        ),
    ]
