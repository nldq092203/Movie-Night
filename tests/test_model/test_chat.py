import pytest
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from chat.consumers import ChatRoomConsumer
from chat.routing import websocket_urlpatterns
from asgiref.testing import ApplicationCommunicator
from django.test import override_settings
from tests.factories import UserFactory, GroupMessage, ChatGroup
from chat.models import Membership
User = get_user_model()

@pytest.mark.asyncio
@override_settings(CHANNEL_LAYERS={
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
})
async def test_chatroom_consumer():
    # Setup test user
    user = UserFactory()
    message = GroupMessage()
    chatroom = ChatGroup()
    membership = Membership.objects.get_or_create(chat_group=chatroom, user=user)

    # Define the room name to test
    room_name = 'testroom'
    
    # Initialize a communicator for testing the consumer
    communicator = WebsocketCommunicator(ChatRoomConsumer.as_asgi(), f"/ws/chat/{room_name}/")
    
    # Simulate a user in scope for authentication
    communicator.scope['user'] = user
    
    # Connect to the WebSocket
    connected, subprotocol = await communicator.connect()
    assert connected

    # Send a message through the WebSocket
    payload = {
        'message': {
            "id": message.id,
            "body": message.body,
            # "file": file_data,
            "created": message.created
        },
        'user': {
            'email': user.email,
            'nickname': membership.nickname,
            'last_read_at': membership.last_read_at,
        },
    }
    await communicator.send_json_to(message)

    # Receive the echoed message back from the consumer
    response = await communicator.receive_json_from()
    assert response['message']['body'] == 'Hello, World!'
    assert response['user']['nickname'] == membership.nickname
    assert response['user']['email'] == user.email

    # Close the WebSocket connection
    await communicator.disconnect()