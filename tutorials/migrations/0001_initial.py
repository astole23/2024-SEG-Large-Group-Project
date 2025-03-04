# Generated by Django 5.1.4 on 2025-03-04 13:30

import django.contrib.auth.models
import django.contrib.auth.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobPosting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_title', models.CharField(help_text='The title of the job posting.', max_length=255)),
                ('company_name', models.CharField(help_text='The name of the company offering the job.', max_length=255)),
                ('location', models.CharField(help_text='Location of the job (e.g., city, country, or remote).', max_length=255)),
                ('salary_range', models.PositiveIntegerField(blank=True, help_text='Salary offered for the job.', null=True)),
                ('contract_type', models.CharField(help_text='Type of contract for the job.', max_length=50)),
                ('job_overview', models.TextField(help_text='A brief overview of the job responsibilities and expectations.')),
                ('roles_responsibilities', models.TextField(help_text='Detailed list of job responsibilities and duties.')),
                ('required_skills', models.TextField(help_text='List of skills required for the job (comma-separated).')),
                ('preferred_skills', models.TextField(blank=True, help_text='List of preferred skills for the job (comma-separated).', null=True)),
                ('education_required', models.CharField(help_text='Minimum education level required for the job.', max_length=255)),
                ('perks', models.TextField(help_text='List of benefits and perks provided by the employer.')),
                ('application_deadline', models.CharField(help_text='Deadline for submitting job applications.', max_length=255)),
                ('company_overview', models.TextField(blank=True, help_text='Brief information about the company.', null=True)),
                ('why_join_us', models.TextField(blank=True, help_text='Reasons why candidates should apply for this job.', null=True)),
                ('company_reviews', models.FloatField(blank=True, help_text='Average review rating of the company.', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Date and time when the job was posted.')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Date and time when the job details were last updated.')),
                ('work_type', models.CharField(help_text='Type of work flexibility offered by the employer.', max_length=255)),
                ('child_company_name', models.CharField(blank=True, help_text='Name of the child company.', max_length=255, null=True)),
                ('required_documents', models.TextField(default='Updated CV', help_text='List of documents required for the job application.')),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('is_company', models.BooleanField(default=False)),
                ('company_name', models.CharField(blank=True, max_length=255, null=True)),
                ('industry', models.CharField(blank=True, max_length=255, null=True)),
                ('location', models.CharField(blank=True, max_length=100, null=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='company_logos/')),
                ('description', models.TextField(blank=True, null=True)),
                ('unique_id', models.CharField(blank=True, max_length=8, null=True, unique=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='CompanyUser',
            fields=[
            ],
            options={
                'verbose_name': 'Company',
                'verbose_name_plural': 'Companies',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('tutorials.customuser',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='NormalUser',
            fields=[
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('tutorials.customuser',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(max_length=2000)),
                ('rating', models.PositiveIntegerField(default=1)),
            ],
            options={
                'constraints': [models.CheckConstraint(condition=models.Q(('rating__gte', 1), ('rating__lte', 5)), name='rating_range')],
            },
        ),
    ]
