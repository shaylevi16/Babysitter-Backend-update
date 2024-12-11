# Generated by Django 5.1.2 on 2024-11-18 13:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Babysitter',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('age', models.IntegerField()),
                ('address', models.CharField(max_length=255)),
                ('hourly_rate', models.DecimalField(decimal_places=2, max_digits=6)),
                ('description', models.TextField()),
                ('profile_picture', models.ImageField(default='static/default_image.jpg', upload_to='babysitters_profile_pics/')),
                ('phone_number', models.CharField(max_length=15, unique=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Babysitter', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Availability',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('babysitter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='availability', to='base.babysitter')),
            ],
        ),
        migrations.CreateModel(
            name='Parents',
            fields=[
                ('family_id', models.AutoField(primary_key=True, serialize=False)),
                ('dad_name', models.CharField(max_length=255)),
                ('mom_name', models.CharField(max_length=255)),
                ('address', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('profile_picture', models.ImageField(default='static/default_image.jpg', upload_to='parents_profile_pics/')),
                ('phone_number', models.CharField(max_length=15, unique=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Parent', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Meetings',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('meeting_time', models.DateTimeField()),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('babysitter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meetings', to='base.babysitter')),
                ('family', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meetings', to='base.parents')),
            ],
        ),
        migrations.CreateModel(
            name='Kids',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('age', models.IntegerField(blank=True, null=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('family', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='kids', to='base.parents')),
            ],
        ),
        migrations.CreateModel(
            name='Requests',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('declined', 'Declined')], default='pending', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('babysitter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='base.babysitter')),
                ('family', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='base.parents')),
            ],
        ),
        migrations.CreateModel(
            name='Reviews',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('review_text', models.TextField(blank=True, null=True)),
                ('rating', models.IntegerField(blank=True, null=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('babysitter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='base.babysitter')),
                ('family', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='base.parents')),
            ],
        ),
        migrations.CreateModel(
            name='TimeWindow',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('availability', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='availability', to='base.availability')),
            ],
        ),
    ]
