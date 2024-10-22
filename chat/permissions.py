from rest_framework import permissions
from .models import ChatGroup

class IsChatGroupMember(permissions.BasePermission):
    """
    Custom permission to only allow members of a chat group to read its content.
    """
    
    def has_object_permission(self, request, view, obj):
        # Ensure the object is a ChatGroup
        if not isinstance(obj, ChatGroup):
            return False
        
        # Check if the user is authenticated and is a member of the chat group
        return request.user.is_authenticated and obj.members.filter(id=request.user.id).exists()

    def has_permission(self, request, view):
        # Check if it's a read-only action, such as a GET request
        if request.method == 'GET':
            # Retrieve the chat group and check if the user is a member
            group_name = view.kwargs.get('group_name')
            try:
                chat_group = ChatGroup.objects.get(group_name=group_name)
                return chat_group.members.filter(id=request.user.id).exists()
            except ChatGroup.DoesNotExist:
                return False
        return False