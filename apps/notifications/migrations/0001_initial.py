# Generated by Django 4.2.16 on 2024-12-29 12:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(choices=[('INV', 'Invitation'), ('REM', 'Reminder'), ('RES', 'Response'), ('UPD', 'Update'), ('CAN', 'Cancellation')], db_index=True, max_length=3)),
                ('is_read', models.BooleanField(db_index=True, default=False)),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('message', models.TextField(blank=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('is_seen', models.BooleanField(db_index=True, default=False)),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.contenttype')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_notifications', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sent_notifications', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
