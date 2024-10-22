"""
This module defines the serializers for the chat application, including the serialization of 
chat groups, memberships, and messages. These serializers help in transforming model instances 
to JSON and validating the input data before saving to the database.

Key serializers:
1. **MembershipSerializer**: Handles serialization of `Membership` objects, which represent 
   a user's membership in a chat group, including fields like role and nickname.
2. **ChatGroupSerializer**: Serializes chat group data, including details of the last message 
   and the members of the group.
3. **ChatGroupDetailSerializer**: Extends the `ChatGroupSerializer` to include additional 
   details, such as the member count, when retrieving a chat group in detail views.
4. **GroupMessageSerializer**: Serializes individual chat messages, including validation 
   logic to ensure a message body or file is provided.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ChatGroup, Membership, GroupMessage

UserModel = get_user_model()

class MembershipSerializer(serializers.ModelSerializer):
    """
    Serializer for the `Membership` model. It handles the serialization of membership data,
    including the role, user email, chat group, nickname, and the last time the user read the messages.
    It also includes a custom field to retrieve the user's name from the related profile.
    """
    user = serializers.EmailField()  # User's email address
    chat_group = serializers.StringRelatedField()  # String representation of the chat group
    role = serializers.ChoiceField(choices=Membership.ROLE_CHOICES)  # User's role in the chat group
    name = serializers.SerializerMethodField()  # Custom field to retrieve the user's name

    class Meta:
        model = Membership
        fields = ['role', 'user', 'chat_group', 'nickname', 'last_read_at', 'name']  # Include the 'name' field

    def get_name(self, obj):
        """
        Method to retrieve the user's name from their profile if it exists.
        """
        return obj.user.profile.name if hasattr(obj.user, 'profile') else None

class ChatGroupSerializer(serializers.ModelSerializer):
    """
    Serializer for the `ChatGroup` model. This serializer includes additional fields
    for the last message content, the time the last message was sent, and the sender of the last message.
    It also includes a list of the members in the group using the `MembershipSerializer`.
    """
    last_message_content = serializers.SerializerMethodField(read_only=True)  # Last message content in the group
    last_message_time = serializers.SerializerMethodField(read_only=True)  # Time the last message was sent
    last_message_sender = serializers.SerializerMethodField(read_only=True)  # Email of the last message sender
    members = MembershipSerializer(source='membership_set', many=True, read_only=True)  # List of members in the group

    class Meta:
        model = ChatGroup
        fields = [
            'group_name', 
            'groupchat_name', 
            'is_private', 
            'last_message_content', 
            'last_message_time', 
            'last_message_sender',
            'members'
        ]

    def get_last_message_content(self, obj):
        """
        Method to retrieve the content of the last message in the chat group.
        """
        return getattr(obj, 'last_message_content', None)

    def get_last_message_time(self, obj):
        """
        Method to retrieve the time the last message was sent, formatted as needed.
        """
        return getattr(obj, 'last_message_time', None)

    def get_last_message_sender(self, obj):
        """
        Method to retrieve the email of the sender of the last message.
        """
        return getattr(obj, 'last_message_sender', None)
    
class ChatGroupDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed view of the `ChatGroup` model. This serializer includes
    additional fields like the member count and a detailed list of members in the group.
    """
    members = MembershipSerializer(source='membership_set', many=True, read_only=True)  # List of members in the group
    member_count = serializers.SerializerMethodField()  # Total number of members in the group

    class Meta:
        model = ChatGroup
        fields = ['group_name', 'groupchat_name', 'is_private', 'created_at', 'members', 'member_count']
        read_only_fields = ['group_name', 'created_at', 'is_private', 'members', 'member_count']

    def get_member_count(self, obj):
        """
        Method to retrieve the total number of members in the chat group.
        """
        return obj.members.count()

class GroupMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the `GroupMessage` model. This serializer handles the serialization
    of individual messages in a chat group, including the author of the message and 
    optional file attachments.
    
    It also includes validation to ensure that either a message body or file is provided.
    """
    author = serializers.EmailField()  # Email of the message author
    filename = serializers.ReadOnlyField()  # Filename if a file is attached to the message
    is_image = serializers.ReadOnlyField()  # Boolean flag indicating if the file is an image

    class Meta:
        model = GroupMessage
        fields = ['id', 'group', 'author', 'body', 'file', 'filename', 'is_image', 'created']
        read_only_fields = ['filename', 'is_image', 'created']

    def validate(self, data):
        """
        Custom validation to ensure that either the message body or file is provided.
        If both are empty, a validation error is raised.
        """
        if not data.get('body') and not data.get('file'):
            raise serializers.ValidationError("Either body text or file must be provided.")
        return data
    

"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""