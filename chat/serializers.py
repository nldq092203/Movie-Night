from rest_framework import serializers
from .models import ChatGroup, Membership, GroupMessage


class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ['user', 'nickname', 'last_read_at']

class GroupMessageSerializer(serializers.ModelSerializer):
    author = serializers.EmailField()
    group = serializers.SlugRelatedField(
        slug_field='group_name',
        queryset=ChatGroup.objects.all()
    )

    class Meta:
        model = GroupMessage
        fields = ['id', 'group', 'author', 'body', 'file', 'filename', 'is_image', 'created']
        read_only = ["filename", "is_image"]

class ChatGroupSerializer(serializers.ModelSerializer):
    admin = serializers.ListField(
        child=serializers.EmailField(),
        source='admin.values_list', 
        read_only=True
    )
    members = MembershipSerializer(source='membership_set', read_only=True, many=True)

    class Meta:
        model = ChatGroup
        fields = ['id', 'group_name', 'groupchat_name', 'admin', 'members', 'is_private']