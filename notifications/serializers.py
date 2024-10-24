from rest_framework import serializers
from notifications.models import Notification
from movies.models import MovieNight, MovieNightInvitation
from movies.serializers import MovieNightInvitationSerializer, MovieNightSerializer

class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Notification model. Serializes notification data including sender, recipient,
    and related content object.
    """
    recipient_email = serializers.EmailField(source='recipient.email', read_only=True)
    sender_email = serializers.EmailField(source='sender.email', read_only=True, allow_null=True)
    content_object = serializers.SerializerMethodField()
    class Meta:
        model = Notification
        fields = [
            'id', 
            'recipient_email', 
            'sender_email', 
            'notification_type', 
            'is_read', 
            'content_type', 
            'object_id', 
            'content_object', 
            'message', 
            'timestamp',
            'is_seen'
        ]
        read_only_fields = ['timestamp']
    def validate_notification_type(self, value):
        """
        Validate that the notification type is one of the allowed types.
        """
        allowed_types = [choice[0] for choice in Notification.NOTIFICATION_TYPES]
        if value not in allowed_types:
            raise serializers.ValidationError(f"Invalid notification type: {value}. Allowed types are: {', '.join(allowed_types)}")
        return value
    def get_content_object(self, obj):
        """
        Customize how the related object (content_object) is serialized based on its type.
        """
        content_object = obj.content_object
        
        # If the content object is a MovieNight
        if isinstance(content_object, MovieNight):
            return MovieNightSerializer(content_object).data
        
        # If the content object is a MovieNightInvitation
        elif isinstance(content_object, MovieNightInvitation):
            # Get the serialized data and include the movie_night.id field
            invitation_data = MovieNightInvitationSerializer(content_object).data
            invitation_data['movie_night_id'] = content_object.movie_night.id
            return invitation_data
        
        # Default behavior for other content types
        return str(content_object)