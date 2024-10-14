import pytest
import json
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from chat.consumers import ChatRoomConsumer
from chat.routing import websocket_urlpatterns
from tests.factories import UserFactory, ChatGroupFactory
from asgiref.sync import sync_to_async


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestChatRoomConsumer:

    def setup_method(self):
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.chat_group = ChatGroupFactory()

    async def test_websocket_connection(self):

        # Define the communicator for WebSocket testing
        communicator = WebsocketCommunicator(
            URLRouter(websocket_urlpatterns),
            f"/ws/chat/{self.chat_group.group_name}/"
        )

        # Simulate an authenticated user in the communicator's scope
        communicator.scope['user'] = self.user1

        # Connect to the WebSocket
        connected, subprotocol = await communicator.connect()
        assert connected

        # Send a message through the WebSocket
        message_content = "Hello, WebSocket!"
        await communicator.send_json_to({
            "body": message_content
        })

        # Receive the response from the consumer
        response = await communicator.receive_json_from()
        assert response['message']['body'] == message_content
        assert response['user']['email'] == self.user1.email

        # Clean up and disconnect
        await communicator.disconnect()

    async def test_message_broadcast(self):
        # Connect the first user
        communicator1 = WebsocketCommunicator(
            URLRouter(websocket_urlpatterns),
            f"/ws/chat/{self.chat_group.group_name}/"
        )
        communicator1.scope['user'] = self.user1
        connected, _ = await communicator1.connect()
        assert connected

        # Connect the second user
        communicator2 = WebsocketCommunicator(
            URLRouter(websocket_urlpatterns),
            f"/ws/chat/{self.chat_group.group_name}/"
        )
        communicator2.scope['user'] = self.user2
        connected, _ = await communicator2.connect()
        assert connected

        # User1 sends a message
        message_content = "Hello from user1!"
        await communicator1.send_json_to({
            "body": message_content
        })

        # Both users receive the broadcast message
        response1 = await communicator1.receive_json_from()
        response2 = await communicator2.receive_json_from()

        assert response1['message']['body'] == message_content
        assert response2['message']['body'] == message_content

        # Clean up and disconnect both communicators
        await communicator1.disconnect()
        await communicator2.disconnect()