from rest_framework import permissions
from movies.models import MovieNightInvitation, MovieNight
from django.db.models import Q

class MovieNightDetailPermission(permissions.BasePermission):
    """
    Custom permission class to allow only the creator of the movie night
    or the invited participants (confirmed attendance or pending invitees) to view the movie night details.
    """
    
    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS are read-only methods (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            # Allow access if the user is the creator of the movie night
            if obj.creator == request.user:
                return True

            # Check if the user is a confirmed participant or a pending invitee
            is_invited = MovieNightInvitation.objects.filter(
                movie_night=obj, 
                invitee=request.user
            ).filter(
                Q(attendance_confirmed=True, is_attending=True) | Q(attendance_confirmed=False)
            ).exists()

            if is_invited:
                return True

        # For other methods, such as POST, PUT, DELETE, only the creator is allowed
        return obj.creator == request.user

class MovieNightInvitationPermission(permissions.BasePermission):
    """
    Custom permission class to ensure that only the creator of the MovieNight
    can send invitations for that MovieNight.
    """
    def has_permission(self, request, view):
        movie_night_id = request.data.get('movie_night')
        if not movie_night_id:
            return False
        movie_night = MovieNight.objects.get(pk=movie_night_id)
        return movie_night.creator == request.user

class IsInvitee(permissions.BasePermission):
    """
    Custom permission to only allow the invitee of the MovieNightInvitation to view or edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Only allow the invitee of the invitation to access it
        return obj.invitee == request.user
    
"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""