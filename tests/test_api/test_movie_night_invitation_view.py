"""
Tests for MovieNightInvitation views and functionality.

Includes:
1. Listing and filtering invitations for an authenticated user.
2. Creating invitations (restricted to MovieNight creators).
3. Ensuring proper access control and preventing duplicates.

Classes:
- TestMyMovieNightInvitation: Tests for listing and filtering invitations.
- TestMovieNightInvitationCreateView: Tests for creating invitations.
"""

import pytest
from django.urls import reverse
from rest_framework import status
from movies.models import MovieNightInvitation
from tests.factories import UserFactory, MovieNightFactory, MovieNightInvitationFactory
from django.utils import timezone
from datetime import timedelta
import logging
from django.db.models.signals import post_save
from movies.signals import send_invitation
logger = logging.getLogger(__name__)

@pytest.mark.django_db
class TestMyMovieNightInvitation:
    @pytest.fixture(autouse=True)
    def setup(self):
        # self.invitation = MovieNightInvitationFactory()
        post_save.disconnect(send_invitation, sender=MovieNightInvitation)

    def tearDown(self):
        # Reconnect the signal after tests
        post_save.connect(send_invitation, sender=MovieNightInvitation)

    def test_movie_night_invitations_list(self, authenticated_client, user):
        """
        Test that all movie night invitations for the authenticated user are listed, excluding those refused.
        """
        # Create movie night invitations for the authenticated user
        movie_night1 = MovieNightFactory()
        movie_night2 = MovieNightFactory()
        movie_night3 = MovieNightFactory()
        MovieNightInvitationFactory(invitee=user, movie_night=movie_night1, is_attending=True, attendance_confirmed=True)
        MovieNightInvitationFactory(invitee=user, movie_night=movie_night2, is_attending=False, attendance_confirmed=False)  # pending invite
        
        # Create a refused invitation (should be excluded from the list)
        MovieNightInvitationFactory(invitee=user, movie_night=movie_night3, is_attending=False, attendance_confirmed=True)

        # Create invitations for another user (should not be in the list)
        other_user = UserFactory()
        MovieNightInvitationFactory(invitee=other_user, movie_night=movie_night1)

        url = reverse('movienight_invitation_list')  # Make sure this is the correct URL name
        response = authenticated_client.get(url)

        # Assert that only the authenticated user's non-refused invitations are listed
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        assert len(results) == 2  # One accepted and one pending invitation
        for invitation in results:
            assert invitation['is_attending'] is not False or invitation['attendance_confirmed'] is False

    def test_filter_invitations_by_not_confirmed(self, authenticated_client, user):
        """
        Test filtering invitations by start time of the associated movie night.
        """
        movie_night1 = MovieNightFactory(start_time=timezone.now() + timedelta(days=1))
        movie_night2 = MovieNightFactory(start_time=timezone.now() + timedelta(days=5))
        MovieNightInvitationFactory(invitee=user, movie_night=movie_night1, attendance_confirmed=True)
        MovieNightInvitationFactory(invitee=user, movie_night=movie_night2, attendance_confirmed=False)

        # Filter invitations with movie night starting within 3 days from now
        url = reverse('movienight_invitation_list') + f"?attendance_confirmed=False"
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        assert len(results) == 1  # Only one invitation should match the filter
        assert results[0]['movie_night']== movie_night2.id

    def test_exclude_refused_invitations(self, authenticated_client, user):
        """
        Test that invitations where the user explicitly refused are excluded.
        """
        movie_night1 = MovieNightFactory()
        movie_night2 = MovieNightFactory()
        # Create an invitation that the user accepted
        MovieNightInvitationFactory(invitee=user, movie_night=movie_night1, is_attending=True, attendance_confirmed=True)
        # Create an invitation that the user refused
        MovieNightInvitationFactory(invitee=user, movie_night=movie_night2, is_attending=False, attendance_confirmed=True)

        url = reverse('movienight_invitation_list')
        response = authenticated_client.get(url)

        # Assert that only the accepted invitation is listed
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['is_attending'] is True

    def test_unauthenticated_user_cannot_access(self, any_client):
        """
        Test that an unauthenticated user cannot access the movie night invitation list.
        """
        url = reverse('movienight_invitation_list')
        response = any_client.get(url)

        # Assert that unauthenticated users are denied access
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
class TestMovieNightInvitationCreateView:
    @pytest.fixture(autouse=True)
    def setup(self):
        # self.invitation = MovieNightInvitationFactory()
        post_save.disconnect(send_invitation, sender=MovieNightInvitation)

    def tearDown(self):
        # Reconnect the signal after tests
        post_save.connect(send_invitation, sender=MovieNightInvitation)

    def test_create_invitation_as_creator(self, authenticated_client, user):
        """
        Test that the creator of the MovieNight can create an invitation.
        """
        movie_night = MovieNightFactory(creator=user)
        invitee = UserFactory(email="invitee@example.com")
    
        # Note the movie_night.pk in the URL and kwargs
        url = reverse('movienight_invitation_create', kwargs={'pk': movie_night.pk})
        data = {
            "movie_night": movie_night.id, # movie_night is required
            "invitee": invitee.email,
        }
        response = authenticated_client.post(url, data, format='json')
    
        # Assert: Ensure the invitation was created
        assert response.status_code == status.HTTP_201_CREATED
        assert MovieNightInvitation.objects.filter(movie_night=movie_night, invitee=invitee).exists()

    def test_create_invitation_as_non_creator(self, authenticated_client, user):
        """
        Test that a user who is not the creator of the MovieNight cannot create an invitation.
        """
        other_user = UserFactory()
        movie_night = MovieNightFactory(creator=other_user)
        invitee = UserFactory(email="invitee@example.com")
        
        url = reverse('movienight_invitation_create', kwargs={'pk': movie_night.pk})
        data = {
            "movie_night": movie_night.id, 
            "invitee": invitee.email,
        }
        response = authenticated_client.post(url, data, format='json')
        
        # Assert: Ensure the user is denied access
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_invitation_unauthenticated(self, any_client):
        """
        Test that unauthenticated users cannot create invitations.
        """
        movie_night = MovieNightFactory()
        invitee = UserFactory(email="invitee@example.com")
        
        url = reverse('movienight_invitation_create', kwargs={'pk': movie_night.pk})
        data = {
            "movie_night": movie_night.id, 
            "invitee": invitee.email,
        }
        response = any_client.post(url, data, format='json')
        
        # Assert: Ensure the user is denied access
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_duplicate_invitation(self, authenticated_client, user):
        """
        Test that the system prevents duplicate invitations to the same invitee for the same MovieNight.
        """
        movie_night = MovieNightFactory(creator=user)
        invitee = UserFactory(email="invitee@example.com")
        MovieNightInvitation.objects.create(movie_night=movie_night, invitee=invitee)

        url = reverse('movienight_invitation_create', kwargs={'pk': movie_night.pk})
        data = {
            "movie_night": movie_night.id, 
            "invitee": invitee.email,
        }
        response = authenticated_client.post(url, data, format='json')

        # Assert: Ensure the duplicate invitation is not created
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "non_field_errors" in response.data
        assert "must make a unique set" in str(response.data["non_field_errors"])

@pytest.mark.django_db
class TestMovieNightInvitationDetailView:
    @pytest.fixture(autouse=True)
    def setup(self):
        # self.invitation = MovieNightInvitationFactory()
        post_save.disconnect(send_invitation, sender=MovieNightInvitation)

    def tearDown(self):
        # Reconnect the signal after tests
        post_save.connect(send_invitation, sender=MovieNightInvitation)
            
    def test_retrieve_invitation_as_invitee(self, authenticated_client, user):
        """
        Test that the invitee can retrieve their own invitation details.
        """
        movie_night = MovieNightFactory()
        invitation = MovieNightInvitationFactory(invitee=user, movie_night=movie_night)
        
        url = reverse('movienight_invitation_detail', kwargs={'pk': invitation.pk})
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == invitation.pk
        assert response.data['invitee'] == user.email
        assert response.data['movie_night'] == movie_night.id

    def test_update_invitation_accept(self, authenticated_client, user):
        """
        Test that the invitee accept the invitation. Thus, is_attending is updated to True and 
        attendance_confirmed to True
        """
        movie_night = MovieNightFactory()
        invitation = MovieNightInvitationFactory(invitee=user, movie_night=movie_night, is_attending=False)
        
        url = reverse('movienight_invitation_detail', kwargs={'pk': invitation.pk})
        data = {
            "is_attending": True,
            "attendance_confirmed": True
            }
        response = authenticated_client.patch(url, data, format='json')

        # Assert the update was successful
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_attending'] is True
        assert response.data['attendance_confirmed'] is True
        
        # Assert the data was saved correctly
        invitation.refresh_from_db()
        assert invitation.is_attending is True
        assert invitation.attendance_confirmed is True
    
    """
    Same for refused case
    """

    def test_delete_invitation_as_invitee(self, authenticated_client, user):
        """
        Test that the invitee can delete their own invitation.
        """
        movie_night = MovieNightFactory()
        invitation = MovieNightInvitationFactory(invitee=user, movie_night=movie_night)
        
        url = reverse('movienight_invitation_detail', kwargs={'pk': invitation.pk})
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Assert the invitation was deleted
        assert not MovieNightInvitation.objects.filter(pk=invitation.pk).exists()

    def test_access_denied_for_non_invitee(self, authenticated_client, user):
        """
        Test that users who are not the invitee cannot access or modify the invitation.
        """
        other_user = UserFactory()
        movie_night = MovieNightFactory()
        invitation = MovieNightInvitationFactory(invitee=other_user, movie_night=movie_night)
        
        url = reverse('movienight_invitation_detail', kwargs={'pk': invitation.pk})
        
        # Attempt to retrieve the invitation
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Attempt to update the invitation
        data = {"is_attending": True}
        response = authenticated_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Attempt to delete the invitation
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_user_cannot_access(self, any_client):
        """
        Test that unauthenticated users cannot access the movie night invitation detail view.
        """
        movie_night = MovieNightFactory()
        invitation = MovieNightInvitationFactory(movie_night=movie_night)
        
        url = reverse('movienight_invitation_detail', kwargs={'pk': invitation.pk})
        
        # Attempt to retrieve the invitation
        response = any_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Attempt to update the invitation
        data = {"is_attending": True}
        response = any_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Attempt to delete the invitation
        response = any_client.delete(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""