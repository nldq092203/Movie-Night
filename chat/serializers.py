from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ChatGroup, Membership, GroupMessage

UserModel = get_user_model()

class MembershipSerializer(serializers.ModelSerializer):
    user = serializers.EmailField()
    chat_group = serializers.StringRelatedField()  
    role = serializers.ChoiceField(choices=Membership.ROLE_CHOICES)
    name = serializers.SerializerMethodField()  # Add a method field for the name

    class Meta:
        model = Membership
        fields = ['role', 'user', 'chat_group', 'nickname', 'last_read_at', 'name']  # Include 'name' in the fields

    def get_name(self, obj):
        # Return the name from the associated UserProfile if it exists
        return obj.user.profile.name if hasattr(obj.user, 'profile') else None

class ChatGroupSerializer(serializers.ModelSerializer):
    last_message_content = serializers.SerializerMethodField(read_only=True)
    last_message_time = serializers.SerializerMethodField(read_only=True)
    last_message_sender = serializers.SerializerMethodField(read_only=True)
    members = MembershipSerializer(source='membership_set', many=True, read_only=True)

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
        return getattr(obj, 'last_message_content', None)

    def get_last_message_time(self, obj):
        # Customize the timestamp format for display, e.g., '2 mins ago'
        return getattr(obj, 'last_message_time', None)

    def get_last_message_sender(self, obj):
        return getattr(obj, 'last_message_sender', None)
    
class ChatGroupDetailSerializer(serializers.ModelSerializer):
    members = MembershipSerializer(source='membership_set', many=True, read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatGroup
        fields = ['group_name', 'groupchat_name', 'is_private', 'created_at', 'members', 'member_count']
        read_only_fields = ['group_name', 'created_at', 'is_private', 'members', 'member_count']

    def get_member_count(self, obj):
        return obj.members.count()

class GroupMessageSerializer(serializers.ModelSerializer):
    author = serializers.EmailField()
    filename = serializers.ReadOnlyField()
    is_image = serializers.ReadOnlyField()

    class Meta:
        model = GroupMessage
        fields = ['id', 'group', 'author', 'body', 'file', 'filename', 'is_image', 'created']
        read_only_fields = ['filename', 'is_image', 'created']

    def validate(self, data):
        """
        Ensure either body or file is provided, but not both empty.
        """
        if not data.get('body') and not data.get('file'):
            raise serializers.ValidationError("Either body text or file must be provided.")
        return data