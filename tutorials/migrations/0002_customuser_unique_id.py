# Generated by Django 4.2 on 2025-03-23 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutorials', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='unique_id',
            field=models.CharField(blank=True, max_length=8, null=True, unique=True),
        ),
    ]
