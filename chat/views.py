from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateAPIView,
    CreateAPIView,
    ListAPIView
)
from django.utils import timezone
from chat.serializers import (
    MembershipSerializer,
    ChatGroupSerializer,
    GroupMessageSerializer,
    ChatGroupDetailSerializer,

)
from chat.models import (
    ChatGroup,
    GroupMessage,
    Membership,
    UserModel
)
from chat.filters import ChatGroupFilter, GroupMessageFilter  
from rest_framework.pagination import PageNumberPagination
from chat.permissions import IsChatGroupMember
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from rest_framework.exceptions import NotFound
from rest_framework import status
from asgiref.sync import async_to_sync
import ably
from django.conf import settings
from django.db.models import OuterRef, Subquery
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import uuid
import json
from django.utils.crypto import get_random_string
import logging

logger = logging.getLogger(__name__)

class AblyAuth(APIView):
    permission_classes = [IsAuthenticated]

    async def get_token(self, request):
        """
        Asynchronously generates a token request for Ably.
        
        This method uses the Ably REST client to create a token request.
        The token request is used by the Ably Realtime or REST library 
        to authenticate the user on the client side. The token is associated 
        with the user's email address, which is used as the client ID.
        """
        client_id = request.user.email
        ably_client = ably.AblyRest(settings.ABLY_API_KEY)

        token_params = {"client_id": client_id}

        try:
            # Requesting a token asynchronously
            token_request = await ably_client.auth.create_token_request(token_params)
            return token_request
        except ably.AblyException as e:
            return {"error": str(e)}
    
    def get(self, request):
        """
        Handles the GET request to obtain an Ably token request.
        
        This method uses Django's synchronous-to-asynchronous utility to 
        call the asynchronous get_token method. The returned token request 
        is converted into a dictionary format and sent as a JSON response.
        """
        # Convert the coroutine response to a dictionary suitable for JSON
        token_request = async_to_sync(self.get_token)(request)
        token_request_dict = {
            'clientId': token_request.client_id,
            'nonce': token_request.nonce,
            'mac': token_request.mac,
            'ttl': token_request.ttl,
            'capability': token_request.capability,
            'timestamp': token_request.timestamp,
            'keyName': token_request.key_name
        }
        logger.warning(token_request_dict)
        if isinstance(token_request_dict, dict) and "error" in token_request_dict:
            # Handling errors
            return Response(token_request, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # If no error, respond with token
        return Response({"token_request": token_request_dict}, status=status.HTTP_200_OK)
    
class ChatGroupView(ListCreateAPIView):
    serializer_class = ChatGroupSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ChatGroupFilter 

    def get_queryset(self):
        # Subquery to get the last message details for each group
        last_message = GroupMessage.objects.filter(group=OuterRef('pk')).order_by('-created')
        
        return ChatGroup.objects.filter(membership__user=self.request.user)\
            .annotate(
                last_message_content=Subquery(last_message.values('body')[:1]),
                last_message_time=Subquery(last_message.values('created')[:1]),
                last_message_sender=Subquery(last_message.values('author__email')[:1])
            ).order_by('-last_message_time')

    def create(self, request, *args, **kwargs):
        is_private = request.data.get('is_private', False)
        member_emails = request.data.get('member_emails', [])  # An array of members' emails

        # Step 1: Validate that at least two members are provided
        if len(member_emails) < 2:
            return Response({'message': 'At least two members are required for a private chat.'}, 
                            status=status.HTTP_400_BAD_REQUEST)

        # Step 2: Get or create a unique group name for private groups
        if is_private:
            # Sort member emails alphabetically to ensure consistent group matching
            member_emails.sort()

            # Check if a group between these members already exists
            existing_group = ChatGroup.objects.filter(
                membership__user__email__in=member_emails,
                membership__chat_group__is_private=True
            ).distinct().first()

            if existing_group:
                # If the group exists, return the existing group data
                serializer = self.get_serializer(existing_group)
                return Response(serializer.data, status=status.HTTP_200_OK)

            # Create a random unique group name
            group_name = f'private-group-{uuid.uuid4()}'
        else:
            # For public groups, use the group name from the request or generate one
            group_name = request.data.get('group_name', f'public-group-{get_random_string(10)}')

        # Step 3: Create a new chat group
        serializer = self.get_serializer(data={**request.data, 'group_name': group_name})
        serializer.is_valid(raise_exception=True)
        chat_group = serializer.save()

        # Step 4: Add members to the group (including the requesting user)
        for email in member_emails:
            try:
                user = UserModel.objects.get(email=email)
                Membership.objects.create(user=user, chat_group=chat_group, role='member', last_read_at=timezone.now())
            except UserModel.DoesNotExist:
                return Response({'message': f'User with email {email} does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
        

class ChatGroupDetailView(RetrieveUpdateAPIView):
    serializer_class = ChatGroupDetailSerializer
    permission_classes = [IsAuthenticated, IsChatGroupMember]
    queryset = ChatGroup.objects.all()

    def get_object(self):
        group_name = self.kwargs.get('group_name')
        try:
            return ChatGroup.objects.get(group_name=group_name)
        except ChatGroup.DoesNotExist:
            raise NotFound(f"ChatGroup with name '{group_name}' does not exist.")

class MembershipView(CreateAPIView):
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        user = request.user
        chat_group_name = self.kwargs.get('group_name') 

        # Check if chat group exists
        chat_group = get_object_or_404(ChatGroup, group_name=chat_group_name)

        # Check if the user is already a member
        if Membership.objects.filter(user=user, chat_group=chat_group).exists():
            return Response({'message': 'User is already a member of this group.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create membership
        membership_data = {'user': user.id, 'chat_group': chat_group_name, 'role': request.data.get('role', 'member'), 'last_read_at': timezone.now()}
        serializer = self.get_serializer(data=membership_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveUpdateAPIView
from django.shortcuts import get_object_or_404
from .models import Membership, ChatGroup, UserModel

class MembershipDetailView(RetrieveUpdateAPIView):
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Retrieve the membership object based on the group name and member email.
        """
        group_name = self.kwargs.get('group_name')
        member_email = self.request.data.get('member_email')

        # Ensure the user and chat group exist
        member = get_object_or_404(UserModel, email=member_email)
        chat_group = get_object_or_404(ChatGroup, group_name=group_name)

        # Get the membership for the specific user and chat group
        membership = get_object_or_404(Membership, user=member, chat_group=chat_group)
        return membership

    def update(self, request, *args, **kwargs):
        """
        Update the membership details like nickname or role.
        """
        instance = self.get_object()

        # Get nickname or other fields from request data and update the instance
        nickname = request.data.get('nickname', None)

        if nickname:
            instance.nickname = nickname

        # Save updated membership instance
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
class GroupMessageView(ListAPIView):
    serializer_class = GroupMessageSerializer
    permission_classes = [IsAuthenticated, IsChatGroupMember]
    pagination_class = PageNumberPagination
    filterset_class = GroupMessageFilter

    def get_queryset(self):
        # Retrieve the chat group by the provided group name and ensure the user is a member
        group_name = self.kwargs['group_name']
        chat_group = get_object_or_404(ChatGroup, group_name=group_name)

        # Return all messages for the chat group, ordered by creation time
        return GroupMessage.objects.filter(group=chat_group).order_by('-created')


@method_decorator(csrf_exempt, name='dispatch')
class AblyWebhookMessageView(View):
    def post(self, request, *args, **kwargs):
        try:
            # Parse incoming JSON payload from Ably
            data = json.loads(request.body)
            logger.info("Received webhook payload: %s", data)

            # Process each item in the webhook
            for message in data.get("messages", []):
                event_name = message.get('name')
                
                # Assuming the event name and data format, adjust as needed
                if event_name == 'new-message':  
                    group_name = data.get('channel')
                    author_email = message.get('clientId')
                    body = message.get('data')
                    created_at = message.get('timestamp')  # Expecting ISO format
                    
                    # Process incoming message by storing it in the database
                    self.process_new_message(group_name, author_email, body, created_at)

            return JsonResponse({'status': 'success'}, status=status.HTTP_200_OK)

        except json.JSONDecodeError:
            logger.error("Invalid JSON received.")
            return JsonResponse({'error': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return JsonResponse({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def process_new_message(self, group_name, author_email, body, created_at):
        # Convert string to datetime if needed and save it to your database
        try:
            chat_group = ChatGroup.objects.get(group_name=group_name)
            author = UserModel.objects.get(email=author_email)

            GroupMessage.objects.create(
                group=chat_group,
                author=author,
                body=body,
                created=created_at
            )
            logger.info(f"Stored new message in group '{group_name}' from '{author_email}'.")

        except ChatGroup.DoesNotExist:
            logger.warning(f"ChatGroup '{group_name}' does not exist.")
        except UserModel.DoesNotExist:
            logger.warning(f"User '{author_email}' does not exist.")
"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""