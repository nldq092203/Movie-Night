# Generated by Django 4.2.16 on 2024-11-03 05:00

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imdb_id', models.SlugField(unique=True)),
                ('title', models.TextField()),
                ('year', models.PositiveIntegerField()),
                ('runtime_minutes', models.PositiveIntegerField(null=True)),
                ('plot', models.TextField()),
                ('country', models.TextField()),
                ('imdb_rating', models.FloatField(default=0)),
                ('url_poster', models.URLField()),
                ('is_full_record', models.BooleanField(default=False)),
                ('genres', models.ManyToManyField(related_name='movies', to='movies.genre')),
            ],
            options={
                'ordering': ['title', 'year'],
            },
        ),
        migrations.CreateModel(
            name='MovieNight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('start_notification_sent', models.BooleanField(default=False)),
                ('start_notification_before', models.DurationField(default=datetime.timedelta(0))),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='movies.movie')),
            ],
            options={
                'ordering': ['creator', 'start_time'],
            },
        ),
        migrations.CreateModel(
            name='SearchTerm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('term', models.TextField(unique=True)),
                ('last_search', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['term'],
            },
        ),
        migrations.CreateModel(
            name='MovieNightInvitation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attendance_confirmed', models.BooleanField(default=False)),
                ('is_attending', models.BooleanField(default=False)),
                ('invitee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('movie_night', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invites', to='movies.movienight')),
            ],
            options={
                'unique_together': {('invitee', 'movie_night')},
            },
        ),
    ]
