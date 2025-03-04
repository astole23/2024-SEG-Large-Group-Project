# Generated by Django 5.1.4 on 2025-03-04 13:41

import django.core.validators
import tutorials.models.standard_cv
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutorials', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CVApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(max_length=20)),
                ('address', models.TextField()),
                ('postcode', models.CharField(max_length=20)),
                ('right_to_work', models.BooleanField()),
                ('visa_details', models.TextField(blank=True, null=True)),
                ('institution', models.CharField(max_length=255)),
                ('degree_type', models.CharField(max_length=255)),
                ('field_of_study', models.CharField(max_length=255)),
                ('expected_grade', models.CharField(max_length=50)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('relevant_modules', models.TextField(blank=True, null=True)),
                ('employer_name', models.CharField(max_length=255)),
                ('job_title', models.CharField(max_length=255)),
                ('work_start_date', models.DateField()),
                ('work_end_date', models.DateField()),
                ('responsibilities', models.TextField()),
                ('key_skills', models.TextField()),
                ('technical_skills', models.TextField()),
                ('languages', models.TextField()),
                ('motivation_statement', models.TextField(validators=[django.core.validators.MinLengthValidator(250), django.core.validators.MaxLengthValidator(500)])),
                ('fit_for_role', models.TextField()),
                ('career_aspirations', models.TextField()),
                ('preferred_start_date', models.DateField()),
                ('internship_duration', models.CharField(max_length=50)),
                ('willingness_to_relocate', models.BooleanField()),
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
            ],
        ),
    ]
