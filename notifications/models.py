from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class Notification(models.Model):
    """
    Notification model tracks various notifications related to movie nights, such as
    invitations, reminders, responses, updates, and cancellations. Notifications are
    linked to a recipient and sender, and they can be associated with various content objects.
    """
    NOTIFICATION_TYPES = [
        ('INV', 'Invitation'),
        ('REM', 'Reminder'),
        ('RES', 'Response'),
        ('UPD', 'Update'),
        ('CAN', 'Cancellation'),
    ]
    recipient = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name="received_notifications")
    sender = models.ForeignKey(UserModel, null=True, blank=True, on_delete=models.SET_NULL, related_name="sent_notifications")
    notification_type = models.CharField(max_length=3, choices=NOTIFICATION_TYPES, db_index=True)  # Indexed for fast lookups
    is_read = models.BooleanField(default=False, db_index=True)  # Indexed for filtering unread notifications
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')  # Links notification to any model
    message = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now=True)  # Automatically updated with the current timestamp when changed
    is_seen = models.BooleanField(default=False, db_index=True)
