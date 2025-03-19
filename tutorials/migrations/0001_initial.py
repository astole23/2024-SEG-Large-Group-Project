# Generated by Django 5.0.1 on 2025-03-19 14:29

import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
import tutorials.auto_fill
import tutorials.models.standard_cv
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CV',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('pdf_file', models.FileField(upload_to='uploads/cvs/', validators=[django.core.validators.FileExtensionValidator(['pdf']), tutorials.auto_fill.validate_file_size])),
                ('structured_data', models.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(max_length=2000)),
                ('rating', models.PositiveIntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='UploadedCV',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='uploads/raw_cvs/')),
                ('uploaded_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserCV',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('personal_info', models.JSONField(default=dict)),
                ('key_skills', models.TextField(blank=True)),
                ('technical_skills', models.TextField(blank=True)),
                ('languages', models.TextField(blank=True)),
                ('interest', models.TextField(blank=True)),
                ('fit_for_role', models.TextField(blank=True)),
                ('aspirations', models.TextField(blank=True)),
                ('education', models.JSONField(blank=True, default=list)),
                ('work_experience', models.JSONField(blank=True, default=list)),
            ],
        ),
        migrations.CreateModel(
            name='UserDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='user_documents/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
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
                ('user_industry', models.JSONField(blank=True, default=list, null=True)),
                ('user_location', models.JSONField(blank=True, default=list, null=True)),
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
            name='CVApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(max_length=20)),
                ('address', models.TextField()),
                ('postcode', models.CharField(max_length=20)),
                ('right_to_work', models.BooleanField(null=True)),
                ('visa_details', models.TextField(blank=True, null=True)),
                ('institution', models.CharField(max_length=255)),
                ('degree_type', models.CharField(max_length=255)),
                ('field_of_study', models.CharField(max_length=255)),
                ('expected_grade', models.CharField(max_length=50)),
                ('start_date', models.DateField(null=True)),
                ('end_date', models.DateField(null=True)),
                ('relevant_modules', models.TextField(blank=True, null=True)),
                ('employer_name', models.CharField(max_length=255)),
                ('job_title', models.CharField(max_length=255)),
                ('work_start_date', models.DateField(null=True)),
                ('work_end_date', models.DateField(null=True)),
                ('responsibilities', models.TextField()),
                ('key_skills', models.TextField()),
                ('technical_skills', models.TextField()),
                ('languages', models.TextField()),
                ('motivation_statement', models.TextField(validators=[django.core.validators.MinLengthValidator(250), django.core.validators.MaxLengthValidator(500)])),
                ('fit_for_role', models.TextField()),
                ('career_aspirations', models.TextField()),
                ('preferred_start_date', models.DateField(null=True)),
                ('internship_duration', models.CharField(max_length=50)),
                ('willingness_to_relocate', models.BooleanField(null=True)),
                ('reference_1_name', models.CharField(max_length=255)),
                ('reference_1_position', models.CharField(max_length=255)),
                ('reference_1_company', models.CharField(max_length=255)),
                ('reference_1_contact', models.CharField(max_length=255)),
                ('reference_2_name', models.CharField(blank=True, max_length=255, null=True)),
                ('reference_2_position', models.CharField(blank=True, max_length=255, null=True)),
                ('reference_2_company', models.CharField(blank=True, max_length=255, null=True)),
                ('reference_2_contact', models.CharField(blank=True, max_length=255, null=True)),
                ('equal_opportunities_monitoring', models.TextField(blank=True, null=True)),
                ('cv_file', models.FileField(upload_to='uploads/cvs/', validators=[django.core.validators.FileExtensionValidator(['pdf']), tutorials.models.standard_cv.validate_file_size])),
                ('structured_experience_education', models.TextField(blank=True, null=True)),
                ('structured_skills', models.TextField(blank=True, null=True)),
                ('structured_projects', models.TextField(blank=True, null=True)),
                ('structured_languages', models.TextField(blank=True, null=True)),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='JobPosting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_title', models.CharField(help_text='The title of the job posting.', max_length=255)),
                ('child_company_name', models.CharField(blank=True, help_text='Name of the child company.', max_length=255, null=True)),
                ('location', models.CharField(help_text='Location of the job (e.g., city, country, or remote).', max_length=255)),
                ('work_type', models.CharField(blank=True, choices=[('remote', 'Remote'), ('hybrid', 'Hybrid'), ('on_site', 'On-site')], help_text='Type of work (e.g., remote, hybrid, on-site).', max_length=50, null=True)),
                ('salary_range', models.PositiveIntegerField(blank=True, help_text='Salary offered for the job.', null=True)),
                ('contract_type', models.CharField(help_text='Type of contract for the job.', max_length=50)),
                ('job_overview', models.TextField(help_text='A brief overview of the job responsibilities and expectations.')),
                ('roles_responsibilities', models.TextField(help_text='Detailed list of job responsibilities and duties.')),
                ('required_skills', models.TextField(help_text='List of skills required for the job (comma-separated).')),
                ('preferred_skills', models.TextField(blank=True, help_text='List of preferred skills for the job (comma-separated).', null=True)),
                ('education_required', models.CharField(help_text='Minimum education level required for the job.', max_length=255)),
                ('perks', models.TextField(help_text='List of benefits and perks provided by the employer.')),
                ('application_deadline', models.CharField(help_text='Deadline for submitting job applications.', max_length=255)),
                ('required_documents', models.TextField(default='Updated CV', help_text='List of documents required for the job application.')),
                ('company_overview', models.TextField(blank=True, help_text='Brief information about the company.', null=True)),
                ('why_join_us', models.TextField(blank=True, help_text='Reasons why candidates should apply for this job.', null=True)),
                ('company_reviews', models.FloatField(blank=True, help_text='Average review rating of the company.', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Date and time when the job was posted.')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Date and time when the job details were last updated.')),
                ('company', models.ForeignKey(blank=True, help_text='The company posting the job (must be a company account).', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='job_postings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='JobApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cover_letter', models.TextField(blank=True, null=True)),
                ('job_answers', models.JSONField(blank=True, null=True)),
                ('application_id', models.CharField(blank=True, max_length=12, null=True, unique=True)),
                ('status', models.CharField(choices=[('submitted', 'Submitted'), ('under_review', 'Under Review'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='submitted', max_length=20)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('applicant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to=settings.AUTH_USER_MODEL)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_applications', to=settings.AUTH_USER_MODEL)),
                ('job_posting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='tutorials.jobposting')),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('notification_type', models.CharField(choices=[('application', 'Application'), ('job_update', 'Job Update'), ('general', 'General')], default='general', max_length=50)),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='review',
            constraint=models.CheckConstraint(check=models.Q(('rating__gte', 1), ('rating__lte', 5)), name='rating_range'),
        ),
        migrations.AddField(
            model_name='uploadedcv',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='usercv',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='userdocument',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to=settings.AUTH_USER_MODEL),
        ),
    ]
