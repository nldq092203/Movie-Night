from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from asgiref.sync import async_to_sync
import json
from chat.models import ChatGroup, GroupMessage, Membership
from chat.serializers import MembershipSerializer
from django.conf import settings
from django.contrib.auth import get_user_model
import logging 

User = get_user_model()

logger = logging.getLogger(__name__)

class ChatRoomConsumer(WebsocketConsumer):
    def connect(self):

        self.chatroom_name = self.scope['url_route']['kwargs']['chatroom_name'] 
        self.chatroom = get_object_or_404(ChatGroup, group_name=self.chatroom_name)

        self.accept()

        if self.is_error_exists():
            error = {
                'error': str(self.scope['error'])
            }
            logger.error(f"Connection error: {str(self.scope['error'])}")
            self.send(text_data=json.dumps(error))
            self.close()   
        else:         
            async_to_sync(self.channel_layer.group_add)(
                self.chatroom_name, self.channel_name
            )
        
        
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.chatroom_name, self.channel_name
        )

    def receive(self, text_data):
        if self.scope.get('user_id') is not None:
            user_id = self.scope.get('user_id')
            try:
                self.user = User.objects.get(id=user_id)
            except Exception:
                self.close()
                return
            text_data_json = json.loads(text_data)
            body = text_data_json['body']
            
            message = GroupMessage.objects.create(
                body = body,
                author = self.user, 
                group = self.chatroom 
            )
            event = {
                'type': 'message_handler',
                'message_id': message.id,
            }
            
            # Broadcast a message to all WebSocket connections
            async_to_sync(self.channel_layer.group_send)(
                self.chatroom_name, event
            )                

    def message_handler(self, event):
        message_id = event['message_id']
        message = GroupMessage.objects.get(id=message_id)
        membership, created = Membership.objects.get_or_create(chat_group=self.chatroom, user=self.user)
        
        # Serialize the membership details
        membership_serializer = MembershipSerializer(membership)
        membership_data = membership_serializer.data 

        # Prepare file metadata
        file_data = None
        if message.file:
            file_data = {
                'url': f"{settings.MEDIA_URL}{message.file.name}",
                'filename': message.filename,
                'is_image': message.is_image,
            }

        payload = {
            'message': {
                "id": message.id,
                "body": message.body,
                "file": file_data,
                "created": message.created.isoformat()
            },
            'user': {
                'email': self.user.email,
                'nickname': membership_data.get('nickname'), 
                'last_read_at': membership_data.get('last_read_at') 
            }
        }
        
        # Send payload as a JSON string
        self.send(text_data=json.dumps(payload))
    
    def is_error_exists(self):
        """This checks if error exists during websockets"""

        return True if 'error' in self.scope else False        