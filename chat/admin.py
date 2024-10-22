from django.contrib import admin
from chat.models import ChatGroup, GroupMessage, Membership

class ChatGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'group_name', 'groupchat_name', 'is_private', 'created_at')

class GroupMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'group', 'author', 'body', 'created')

class MembershipAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'chat_group', 'role', 'last_read_at')

admin.site.register(ChatGroup, ChatGroupAdmin)
admin.site.register(GroupMessage, GroupMessageAdmin)
admin.site.register(Membership, MembershipAdmin)