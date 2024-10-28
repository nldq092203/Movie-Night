from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.conf import settings
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class GoogleLoginAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=None,
        parameters=[
            OpenApiParameter(
                name='id_token',
                type=str,
                location=OpenApiParameter.QUERY,
                description='The ID token received from Google',
                required=True
            )
        ],
        responses={
            200: OpenApiResponse(description='Successful authentication'),
            400: OpenApiResponse(description='ID token is required'),
            401: OpenApiResponse(description='Unauthorized')
        }
    )
    def post(self, request):
        token = request.data.get('id_token')
        if not token:
            return Response({'error': 'ID token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Specify the CLIENT_ID of the app that accesses the backend
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), settings.GOOGLE_CLIENT_ID)

            # ID token is valid. Get the user's Google Account information
            email = idinfo['email']
            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')

            # Check if user exists; if not, create one
            user, created = User.objects.get_or_create(email=email, defaults={
                'first_name': first_name,
                'last_name': last_name,
            })

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            # Invalid token
            logger.warning(f"Token verification failed: {e}")
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error during Google login: {e}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
