# import pytest
# from channels.testing import WebsocketCommunicator
# from channels.routing import URLRouter
# from django.contrib.auth import get_user_model
# from chat.routing import websocket_urlpatterns  # Import your websocket patterns here
# from asgiref.sync import sync_to_async
# from chat.models import ChatGroup


# @pytest.mark.asyncio
# @pytest.mark.django_db
# class TestChatRoomConsumer:
#     async def setup(self):
#         # Create user and chat group for testing
#         self.user = await sync_to_async(get_user_model().objects.create_user)(
#             email='testuser@example.com', password='password'
#         )
#         self.chat_group = await sync_to_async(ChatGroup.objects.create)(
#             group_name="testgroup"
#         )

#     async def test_connect(self):
#         await self.setup()

#         # Initialize WebSocket communicator with the exact URL pattern
#         communicator = WebsocketCommunicator(
#             URLRouter(websocket_urlpatterns), f"/ws/chat/{self.chat_group.group_name}/"
#         )
        
#         # Set the authenticated user in scope
#         communicator.scope["user"] = self.user  # Simulate the user in the WebSocket scope

#         # Establish the WebSocket connection
#         connected, _ = await communicator.connect()
#         assert connected is True  # Ensure connection succeeds

#         await communicator.disconnect()