from movienight_profile.serializers import UserProfileSerializer
from movienight_profile.models import UserProfile
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from movies.permissions import IsOwnerOrReadOnly
from rest_framework.response import Response

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