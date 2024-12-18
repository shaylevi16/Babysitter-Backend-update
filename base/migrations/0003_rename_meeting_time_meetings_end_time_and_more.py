# Generated by Django 5.1.3 on 2024-12-18 14:33

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_remove_timewindow_availability_alter_kids_age_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='meetings',
            old_name='meeting_time',
            new_name='end_time',
        ),
        migrations.AddField(
            model_name='meetings',
            name='start_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]