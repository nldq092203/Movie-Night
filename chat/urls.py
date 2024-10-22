from django.urls import path
from chat.views import (
     AblyAuth, 
     ChatGroupView, 
     ChatGroupDetailView, 
     MembershipView, 
     AblyWebhookMessageView,
     GroupMessageView,
     MembershipDetailView
)
urlpatterns = [
    path('ably/auth/', AblyAuth.as_view(), name='ably_auth'),
    path('chat-group/', ChatGroupView.as_view(), name='chat_group_list'),
    path('chat-group/<str:group_name>/', ChatGroupDetailView.as_view(), name='chat_group_detail'),
    path('chat-group/<str:group_name>/membership', MembershipView.as_view(), name='create_membership'),
    path('chat-group/<str:group_name>/messages/', GroupMessageView.as_view(), name="group_message_list"),
    path('ably-webhook-message/', AblyWebhookMessageView.as_view(), name='ably_webhook'),
    path('membership/<str:group_name>/', MembershipDetailView.as_view(), name='membership_detail'),
]