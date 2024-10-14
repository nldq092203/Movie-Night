from django.contrib import admin
from chat.models import (
    GroupMessage,
    ChatGroup,
    Membership
)
admin.site.register(GroupMessage)
admin.site.register(ChatGroup)
admin.site.register(Membership)

