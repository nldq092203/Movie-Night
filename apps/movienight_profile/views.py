from apps.movienight_profile.serializers import UserProfileSerializer
from apps.movienight_profile.models import UserProfile
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from apps.movies.permissions import IsOwnerOrReadOnly
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from utils.firebase import upload_to_firebase, delete_from_firebase
from rest_framework.views import APIView
from rest_framework import status

from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

User = get_user_model()


class ProfileView(RetrieveUpdateAPIView):
    """
    API view for retrieving a user's profile by email.
    Only authenticated users can access this view.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self):
        """
        Retrieve the profile based on the email provided in the URL.
        If the profile does not exist, create an empty profile.
        """
        email = self.kwargs.get('email')
        user = get_object_or_404(User, email=email)

        # Check if the user already has a profile
        profile, created = UserProfile.objects.get_or_create(user=user)

        return profile

    def update(self, request, *args, **kwargs):
        """
        Override the update method to ensure user email cannot be updated
        and profile is linked properly.
        """
        # Retrieve the profile to be updated
        profile = self.get_object()

        # Validate the data using the serializer
        serializer = self.get_serializer(profile, data=request.data, partial=True)

        # Check if the serializer data is valid
        if serializer.is_valid():
            # Save the profile after validation
            self.perform_update(serializer)
            return Response(serializer.data)
        else:
            # If validation fails, return the errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        """
        Perform the profile update after validation. This method is automatically
        called when calling `serializer.save()` but can be overridden to perform
        extra operations.
        """
        email = self.kwargs.get('email')
        user = get_object_or_404(User, email=email)
        serializer.save(user=user)  # Save the profile

class UploadAvatarView(APIView):
    parser_classes = [MultiPartParser]  # Allow multipart form data for file uploads

    def post(self, request, format=None):
        """
        Upload a new avatar for the user.

        If the user already has an avatar, delete the previous one from Firebase Storage.
        Then, upload the new avatar and save its URL to the user's profile.

        Request:
            - file (avatar): The avatar image to upload.

        Response:
            - 200 OK: Successfully uploaded the new avatar.
            - 400 Bad Request: No file provided in the request.
            - 500 Internal Server Error: Failed to delete the previous avatar from Firebase.
        """
        file = request.FILES.get('avatar')  # Get the uploaded file from the request

        if file:
            # Get the user's profile
            user_profile = UserProfile.objects.get(user=request.user)

            # resized_image = self.resize_image(file, size=(300, 300)) 
            resized_image = file

            # Check if the user already has an avatar URL
            if user_profile.avatar_url:
                # Extract the file path from the avatar URL
                full_url = user_profile.avatar_url
                file_path = full_url.split('appspot.com/')[1]

                # Delete the old avatar from Firebase Storage
                success = delete_from_firebase(file_path)
                
                if not success:
                    return Response({'error': 'Failed to delete previous avatar'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Upload the new avatar to Firebase Storage and get the URL
            avatar_url = upload_to_firebase(resized_image, folder='avatars')

            # Save the new avatar URL to the user's profile
            user_profile.avatar_url = avatar_url
            user_profile.save()

            return Response({'avatar_url': avatar_url}, status=status.HTTP_200_OK)

        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, format=None):
        """
        Delete the user's current avatar.

        The avatar is removed from Firebase Storage and the avatar URL is deleted from the user's profile.

        Response:
            - 200 OK: Successfully deleted the avatar.
            - 400 Bad Request: No avatar found to delete.
            - 404 Not Found: User profile not found.
            - 500 Internal Server Error: Failed to delete the avatar from Firebase.
        """
        try:
            # Get the user profile
            user_profile = UserProfile.objects.get(user=request.user)

            # Check if the user has an avatar set
            if user_profile.avatar_url:
                # Extract the file path from the avatar URL
                full_url = user_profile.avatar_url
                file_path = full_url.split('appspot.com/')[1]

                # Call the function to delete the file from Firebase Storage
                success = delete_from_firebase(file_path)
                # success =True

                if success:
                    # If the file was successfully deleted, remove the URL from the profile
                    user_profile.avatar_url = None
                    user_profile.save()
                    return Response({'message': 'Avatar deleted successfully'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Failed to delete avatar from Firebase'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({'error': 'No avatar to delete'}, status=status.HTTP_400_BAD_REQUEST)

        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

    def resize_image(self, image, size=(300, 300)):
        """
        Resize the given image to the specified size.
        
        Args:
            image (UploadedFile): The image file uploaded by the user.
            size (tuple): The target size as (width, height).
        
        Returns:
            InMemoryUploadedFile: The resized image ready for uploading.
        """
        img = Image.open(image)

        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Resize the image
        img = img.resize(size)

        # Save the image to an in-memory file
        output = BytesIO()
        img.save(output, format='JPEG')  # Save as JPEG format to reduce size

        # Create a new InMemoryUploadedFile to be used in place of the original image
        resized_image = InMemoryUploadedFile(output, 'ImageField', f"{image.name.split('.')[0]}.jpg", 'image/jpeg', sys.getsizeof(output), None)

        output.seek(0)  # Reset the pointer in the in-memory file

        return resized_image
"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""