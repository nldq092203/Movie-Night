from apps.notifications.serializers import NotificationSerializer
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from rest_framework.generics import (
    ListAPIView, 
    UpdateAPIView
    )     
from apps.notifications.models import Notification
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView


class MyNotificationView(ListAPIView):
    serializer_class = NotificationSerializer
    filter_fields = ["is_read", "notification_type"]
    ordering_fields = ["timestamp"]
    permission_classes = [IsAuthenticated]
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="is_read", 
                type=OpenApiTypes.BOOL, 
                location=OpenApiParameter.QUERY, 
                description="Filter notifications based on read status. Pass `true` for read notifications, `false` for unread."
            ),
            OpenApiParameter(
                name="notification_type", 
                type=OpenApiTypes.STR, 
                location=OpenApiParameter.QUERY, 
                description="Filter notifications based on the type (e.g., 'INV' for invitation, 'UPD' for update)."
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="List of notifications for the authenticated user.",
                response=NotificationSerializer(many=True),
            ),
            403: OpenApiResponse(
                description="Unauthorized. The user must be authenticated to access notifications.",
            ),
        },
        description="Retrieve a list of notifications for the authenticated user. The results can be filtered based on `is_read` and `notification_type` and ordered based on `timestamp` ."
    )
    def get_queryset(self):
        queryset = Notification.objects.filter(recipient=self.request.user)
        
        # Apply the 'is_read' filter if present in the query parameters
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            # Convert 'true'/'false' string to actual boolean value
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        
        # Apply the 'notification_type' filter if present in the query parameters
        notification_type = self.request.query_params.get('notification_type')
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)

        # Apply ordering based on 'timestamp' or '-timestamp'
        ordering = self.request.query_params.get('ordering')
        if ordering in ['timestamp', '-timestamp']:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('-timestamp')  # Default to descending order

        return queryset
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # Calculate unseen count
        unseen_count = Notification.objects.filter(recipient=request.user, is_seen=False).count()
        
        return Response({
            'results': serializer.data,
            'unseenCount': unseen_count
        })
class MarkReadNotificationView(UpdateAPIView):
    """
    API view to mark a specific notification as read.
    
    - PATCH: Marks the specified notification as `is_read=True` for the authenticated user.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.all()
    @extend_schema(
        responses={
            200: NotificationSerializer,
            403: OpenApiResponse(description="Forbidden. You are not allowed to update this notification."),
            404: OpenApiResponse(description="Notification not found."),
        },
        description="Mark a specific notification as read for the authenticated user.",
    )
    def patch(self, request, *args, **kwargs):
        """
        Mark the notification as read for the authenticated user.
        """
        notification = get_object_or_404(Notification, pk=self.kwargs['pk'], recipient=self.request.user)
        if notification.is_read:
            return Response({"message": "Notification already marked as read."}, status=status.HTTP_200_OK)
        notification.is_read = True
        notification.save()
        serializer = self.get_serializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)
class MarkAllAsSeenView(APIView):
    """
        Marks all notifications as seen for the authenticated user.
        This endpoint is restricted to authenticated users.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    @extend_schema(
        description="Marks all notifications as seen for the authenticated user",
        responses={
            200: {
                "description": "All notifications marked as seen",
                "examples": {
                    "application/json": {
                        "message": "All notifications marked as seen."
                    }
                },
            },
            204: {
                "description": "No unseen notifications found",
                "examples": {
                    "application/json": {
                        "message": "No unseen notifications found."
                    }
                },
            },
            401: {
                "description": "Unauthorized request",
                "examples": {
                    "application/json": {
                        "detail": "Authentication credentials were not provided."
                    }
                },
            },
        }
    )
    def patch(self, request, *args, **kwargs):
        """
        Marks all notifications as seen for the authenticated user.
        """
        # Fetch all unread notifications for the authenticated user
        notifications = Notification.objects.filter(recipient=request.user, is_seen=False)
        # Update the is_seen field for these notifications
        if notifications.exists():
            notifications.update(is_seen=True)
            return Response({"message": "All notifications marked as seen."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "No unseen notifications found."}, status=status.HTTP_204_NO_CONTENT)