# Generated by Django 4.2 on 2025-03-15 19:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutorials', '0004_usercv_education_usercv_work_experience'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cvapplication',
            name='right_to_work',
            field=models.BooleanField(null=True),
        ),
    ]
