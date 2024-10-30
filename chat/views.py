"""
This module contains views for handling chat-related functionality, including managing chat groups,
memberships, and messages. It also includes integration with the Ably service for real-time messaging.

Key Views:
1. **AblyAuth**: Provides an endpoint to generate an Ably token request for client-side authentication.
2. **ChatGroupView**: Handles listing and creating chat groups. Supports private and public groups, 
   with logic for ensuring unique private groups between specific members.
3. **ChatGroupDetailView**: Retrieves and updates details of a specific chat group by its name.
4. **MembershipView**: Adds users to chat groups and creates memberships for the authenticated user.
5. **MembershipDetailView**: Retrieves and updates membership details, including roles and nicknames, 
   for a user within a specific chat group.
6. **GroupMessageView**: Lists messages in a chat group with pagination and filtering.
7. **AblyWebhookMessageView**: Listens to Ably webhook events and processes incoming messages 
   from the Ably system, storing them in the database.

The views implement:
- **GET** for retrieving data (e.g., chat groups, messages).
- **POST** for creating new data (e.g., memberships, chat groups).
- **PUT** for updating membership or chat group details.
- **Ably Webhook Integration**: Handles incoming messages from Ably and processes them into the system.
  
Permissions:
- **IsAuthenticated**: Ensures only logged-in users can access these views.
- **IsChatGroupMember**: Restricts access to chat group details to group members only.
  
This module also handles real-time communication by integrating with the Ably service for WebSocket 
messaging, allowing updates to be pushed to the clients without page reloads.
"""


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
from django.db.models import Case, When, Value, CharField, OuterRef, Subquery
from django.db.models.functions import Coalesce

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
    """
    This view handles both listing and creating chat groups for authenticated users.

    - GET: Retrieves the chat groups that the authenticated user is a member of.
      It includes additional information such as the last message content, the time of the last message,
      and the sender of the last message for each group.
    
    - POST: Allows creating a new chat group. It supports both private and public chat groups. 
      - For private groups, it ensures that the group has at least two members and checks if a private 
        group between the same members already exists before creating a new one.
      - For public groups, it uses the provided group name or generates a random name if none is provided.
      - Members are added to the group based on their emails.
      - If a user with the given email does not exist, the request will fail.
    """
    
    serializer_class = ChatGroupSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ChatGroupFilter  # Allows filtering on certain fields

    def get_queryset(self):
        """
        Retrieves the list of chat groups the authenticated user is a member of.
        This also fetches and includes details of the last message in each group, such as the message content, 
        the timestamp of the last message, and the sender's email. The results are ordered by the last message time.
        """
        last_message = GroupMessage.objects.filter(group=OuterRef('pk')).order_by('-created').annotate(
            content=Case(
                When(body__isnull=False, then='body'),    
                default=Value('Attachment sent'),                      
                output_field=CharField()
            )
        )
        
        return ChatGroup.objects.filter(membership__user=self.request.user)\
            .annotate(
                last_message_content=Coalesce(Subquery(last_message.values('content')[:1]), Value('No Content')),
                last_message_time=Subquery(last_message.values('created')[:1]),
                last_message_sender=Subquery(last_message.values('author__email')[:1])
            ).order_by('-last_message_time')

    def create(self, request, *args, **kwargs):
        """
        Creates a new chat group (private or public).
        
        For private groups:
        - At least two members must be provided.
        - The system checks if a group between these members already exists.
        - If a group exists, it returns the existing group instead of creating a new one.
        - If not, it creates a new group with a unique name.

        For public groups:
        - The group name is taken from the request or generated if none is provided.

        Members are added to the group based on the emails provided in the request.
        If any member email does not match an existing user, the request fails.
        """
        is_private = request.data.get('is_private', False)
        member_emails = request.data.get('member_emails', [])  # List of member emails

        if len(member_emails) < 2:
            return Response({'message': 'At least two members are required for a private chat.'}, 
                            status=status.HTTP_400_BAD_REQUEST)


        if is_private and len(member_emails) == 2:
            member_emails.sort()  # Ensure emails are in a consistent order to match the same group

            existing_group = ChatGroup.objects.filter(
                membership__user__email__in=member_emails,
                membership__chat_group__is_private=True
            ).distinct().first()

            if existing_group:
                # If such a group exists, return its data
                serializer = self.get_serializer(existing_group)
                return Response(serializer.data, status=status.HTTP_200_OK)

            # Generate a unique name for the private group
            group_name = f'private-group-{uuid.uuid4()}'
        else:
            # For public groups, use the name from the request or generate a random name
            group_name = request.data.get('group_name', f'public-group-{get_random_string(10)}')
        serializer = self.get_serializer(data={**request.data, 'group_name': group_name})
        serializer.is_valid(raise_exception=True)
        chat_group = serializer.save()

        for email in member_emails:
            try:
                user = UserModel.objects.get(email=email)
                Membership.objects.create(user=user, chat_group=chat_group, role='member', last_read_at=timezone.now())
            except UserModel.DoesNotExist:
                return Response({'message': f'User with email {email} does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        logger.warning(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        

class ChatGroupDetailView(RetrieveUpdateAPIView):
    """
    API view for retrieving and updating details of a specific chat group by its group name.
    
    This view supports:
    - **Retrieve**: Get the details of a chat group based on its `group_name`.
    - **Update**: Update the details of a chat group, which is only allowed for members of the group.

    Permission:
    - Only authenticated users who are members of the chat group can access or modify the group.
    
    Raises:
    - `NotFound`: If the chat group with the specified `group_name` does not exist.
    """
    serializer_class = ChatGroupDetailSerializer
    permission_classes = [IsAuthenticated, IsChatGroupMember]  # Ensures that the user is a member of the group
    queryset = ChatGroup.objects.all()

    def get_object(self):
        """
        Retrieve the chat group based on the `group_name` provided in the URL.
        
        If the chat group does not exist, a `NotFound` error will be raised.

        Returns:
            ChatGroup: The chat group instance matching the `group_name`.

        Raises:
            NotFound: If no chat group with the specified `group_name` exists.
        """
        group_name = self.kwargs.get('group_name')
        try:
            return ChatGroup.objects.get(group_name=group_name)
        except ChatGroup.DoesNotExist:
            raise NotFound(f"ChatGroup with name '{group_name}' does not exist.")
        
class MembershipView(CreateAPIView):
    """
    API view for adding a user as a member to a specific chat group.

    This view supports:
    - **Create**: Allows an authenticated user to join a chat group by creating a new membership.
    
    Permission:
    - The user must be authenticated to join a chat group.

    Request Data:
    - `role`: (Optional) The role of the user in the chat group. Defaults to "member".
    
    URL Parameters:
    - `group_name`: The name of the chat group to join.

    Responses:
    - **201 Created**: If the membership is successfully created.
    - **400 Bad Request**: If the user is already a member of the chat group.

    Raises:
    - `NotFound`: If the specified chat group does not exist.
    """
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """
        Creates a membership for the authenticated user in the specified chat group.
        
        The method checks if the user is already a member of the group before creating the membership.
        
        Request:
        - URL parameter: `group_name` (The name of the chat group).
        - Request body: Contains an optional `role` field for assigning a role to the user in the group.

        Returns:
            - **201 Created**: When the membership is successfully created.
            - **400 Bad Request**: If the user is already a member of the group.

        Raises:
            - `NotFound`: If the chat group does not exist.
        """
        user = request.user
        chat_group_name = self.kwargs.get('group_name')

        # Check if chat group exists
        chat_group = get_object_or_404(ChatGroup, group_name=chat_group_name)

        # Check if the user is already a member
        if Membership.objects.filter(user=user, chat_group=chat_group).exists():
            return Response({'message': 'User is already a member of this group.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create membership
        membership_data = {
            'user': user.id, 
            'chat_group': chat_group_name, 
            'role': request.data.get('role', 'member'), 
            'last_read_at': timezone.now()
        }
        serializer = self.get_serializer(data=membership_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    


class MembershipDetailView(RetrieveUpdateAPIView):
    """
    API view for retrieving and updating membership details in a chat group.

    This view supports:
    - **Retrieve**: Fetches the membership details for a specific user in a chat group.
    - **Update**: Allows updating fields such as nickname and role in the membership.

    Permissions:
    - The user must be authenticated to access and update membership details.

    URL Parameters:
    - `group_name`: The name of the chat group.
    
    Request Data (for Update):
    - `member_email`: The email of the member whose membership details are being retrieved or updated.
    - `nickname`: (Optional) New nickname for the user in the chat group.
    
    Responses:
    - **200 OK**: Membership details retrieved or updated successfully.
    - **400 Bad Request**: Invalid request data.
    - **404 Not Found**: If the specified chat group or member does not exist.
    """
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Retrieves the membership object based on the group name and member email.
        
        URL Parameter:
        - `group_name`: The name of the chat group.
        
        Request Data:
        - `member_email`: Email of the user whose membership details are being retrieved or updated.

        Raises:
            - `NotFound`: If the user, chat group, or membership is not found.
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
        Updates the membership details such as nickname or role.
        
        Request Data:
        - `nickname`: (Optional) New nickname for the user in the chat group.

        Raises:
            - `400 Bad Request`: If invalid request data is provided.
            - `404 Not Found`: If the membership does not exist.

        Returns:
            - **200 OK**: Membership details updated successfully.
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
    """
    View for handling Ably webhook messages. This view listens for webhook 
    events triggered by Ably and processes incoming messages, storing them 
    in the database.
    
    Methods:
        - post: Handles incoming POST requests from the Ably webhook.
        - process_new_message: Stores the message details in the database.
    
    Request:
        - The webhook payload is expected to be in JSON format and contains 
          messages with event data (e.g., 'new-message').
    
    Responses:
        - **200 OK**: Successfully processed the webhook and stored messages.
        - **400 Bad Request**: Invalid JSON payload or bad request.
        - **500 Internal Server Error**: Any other internal error.
    """
    def post(self, request, *args, **kwargs):
        """
        Handles incoming POST requests from Ably webhook.

        The request body is expected to be JSON formatted and contain a list of 
        messages. Each message is processed to extract the event name, channel, 
        author email, and message content.

        If the event name matches 'new-message', the message is stored in the 
        associated chat group with the corresponding author.

        Returns:
            - **200 OK**: If messages are successfully processed and stored.
            - **400 Bad Request**: If the JSON payload is invalid.
            - **500 Internal Server Error**: If an error occurs during processing.
        """
        try:
            # Parse incoming JSON payload from Ably
            data = json.loads(request.body)
            logger.info("Received webhook payload: %s", data)

            # Process each message in the webhook
            for message in data.get("messages", []):
                event_name = message.get('name')
                group_name = data.get('channel')
                author_email = message.get('clientId')
                created_at = message.get('timestamp')  # Expecting ISO format

                if event_name == 'new-message':
                    body = message.get('data')
                    self.process_new_message(
                        group_name, author_email, body, created_at
                    )
                elif event_name == 'new-file':
                    file_data = message.get('data')
                    logger.warning(file_data)
                    self.process_file_message(
                        group_name, author_email, file_data, created_at
                    )

            return JsonResponse({'status': 'success'}, status=status.HTTP_200_OK)

        except json.JSONDecodeError:
            logger.error("Invalid JSON received.")
            return JsonResponse(
                {'error': 'Invalid JSON'},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return JsonResponse(
                {'error': 'Internal Server Error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def process_new_message(self, group_name, author_email, body, created_at):
        """
        Helper method to process and store a new message in the chat group.

        Parameters:
            - group_name: The name of the chat group where the message is sent.
            - author_email: The email of the user who authored the message.
            - body: The content of the message.
            - created_at: The timestamp when the message was created.

        Steps:
            1. Retrieve the chat group and the author based on the provided data.
            2. Store the message in the database using the `GroupMessage` model.
            3. Handle cases where the chat group or user does not exist, logging a warning.

        Raises:
            - ChatGroup.DoesNotExist: If the chat group is not found.
            - UserModel.DoesNotExist: If the user is not found.
        """
        try:
            chat_group = ChatGroup.objects.get(group_name=group_name)
            author = UserModel.objects.get(email=author_email)

            # Store the message in the GroupMessage table
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

    def process_file_message(self, group_name, author_email, file_data, created_at):
        """
        Processes and stores a new file message.
        """
        try:
            chat_group = ChatGroup.objects.get(group_name=group_name)
            author = UserModel.objects.get(email=author_email)

            file_data = json.loads(file_data)

            # Extract file details from file_data
            file_name = file_data[0]
            file_type = file_data[1]
            file_url = file_data[2]
            logger.warning(f"file name: {file_name}")
            logger.warning(f"file name: {file_type}")
            logger.warning(f"file name: {file_url}")


            # Store the message with file details
            GroupMessage.objects.create(
                group=chat_group,
                author=author,
                file_url=file_url,
                file_name=file_name,
                file_type=file_type,
                created=created_at
            )
            logger.info(
                f"Stored new file message in group '{group_name}' from '{author_email}'."
            )

        except ChatGroup.DoesNotExist:
            logger.warning(f"ChatGroup '{group_name}' does not exist.")
        except UserModel.DoesNotExist:
            logger.warning(f"User '{author_email}' does not exist.")
        except Exception as e:
            logger.error(f"Error processing file message: {str(e)}")
"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""