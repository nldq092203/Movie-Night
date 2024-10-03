"""
Test cases for the MovieNight-related API views including:

1. **TestMyMovieNightView**:
   - Tests for listing and creating movie nights where the authenticated user is the creator.
   - Ensures that only the user's created movie nights are listed and movie nights can only be created by authenticated users.

2. **TestParticipatingMovieNightView**:
   - Tests for listing movie nights where the authenticated user is either the creator or an invited confirmed participant.
   - Ensures that only the relevant movie nights are displayed and users not invited are excluded from the list.

3. **TestMyMovieNightViewOrderingAndFiltering**:
   - Tests for ordering and filtering movie nights created by the authenticated user.
   - Checks if movie nights are ordered correctly by start time and filtered based on the start time range.

4. **TestParticipatingMovieNightViewOrderingAndFiltering**:
   - Tests for ordering and filtering movie nights where the authenticated user is a participant.
   - Ensures proper ordering by start time and filtering by creator.

These tests cover both authenticated and unauthenticated access, verifying that the API correctly handles permissions, filtering, and ordering.
"""

import pytest
from django.urls import reverse
from rest_framework import status
from movies.models import MovieNight, MovieNightInvitation
from tests.factories import UserFactory, MovieFactory, MovieNightFactory, MovieNightInvitationFactory
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)
@pytest.mark.django_db
class TestMyMovieNightView:
    def test_my_movie_night_list(self, authenticated_client, user):
        """
        Test that only movie nights created by the authenticated user are listed.
        """

        # Create movie nights for the authenticated user
        MovieNightFactory(creator=user, start_time=timezone.now())
        MovieNightFactory(creator=user, start_time=timezone.now())

        # Create movie nights for another user
        other_user = UserFactory()
        MovieNightFactory(creator=other_user, start_time=timezone.now())

        url = reverse('my_movienight_list')
        response = authenticated_client.get(url)
        
        logger.warning(response.data)

        # Assert that only the user's movie nights are listed
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2  # Only the two created by the user

    def test_my_movie_night_create_authenticated(self, authenticated_client, user):
        """
        Test that a new movie night can be created by the authenticated user.
        """
        movie = MovieFactory()

        url = reverse('my_movienight_list')
        data = {
            "movie": movie.id,
            "start_time": timezone.now() + timedelta(days=1),
            # "creator": user.email,
            "start_notification_sent": False
        }
        response = authenticated_client.post(url, data, format='json')

        # Assert that the movie night was successfully created
        assert response.status_code == status.HTTP_201_CREATED
        movie_night = MovieNight.objects.get(pk=response.data["id"])
        assert movie_night.creator == user
    
    def test_my_movie_night_create_unauthenticated(self, any_client):
        """
        Test that a new movie night cannot be created by the unauthenticated user.
        """ 
        movie = MovieFactory()

        url = reverse('my_movienight_list')
        data = {
            "movie": movie.id,
            "start_time": timezone.now(),
            "start_notification_sent": False
        }
        response = any_client.post(url, data, format='json')

        # Assert that Unauthorizated Error
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
       

@pytest.mark.django_db
class TestParticipatingMovieNightView:
    def test_participating_movie_nights(self, authenticated_client, user):
        """
        Test that the view lists movie nights where the authenticated user is either the creator or a confirmed invitee.
        """

        # Movie nights where the user is the creator
        movie_night1 = MovieNightFactory(creator=user, start_time=timezone.now())
        
        # Movie nights where the user is a confirmed invitee
        movie_night2 = MovieNightFactory(creator=UserFactory(), start_time=timezone.now())
        MovieNightInvitationFactory(movie_night=movie_night2, invitee=user, attendance_confirmed=True, is_attending=True)

        # Movie nights where the user is an unconfirmed invitee (should not be listed)
        movie_night3 = MovieNightFactory(creator=UserFactory(), start_time=timezone.now())
        MovieNightInvitationFactory(movie_night=movie_night3, invitee=user, attendance_confirmed=False, is_attending=False)

        # Movie nights created by someone else and the user is not invited
        MovieNightFactory(creator=UserFactory(), start_time=timezone.now())

        url = reverse('movienight_list') 
        response = authenticated_client.get(url)

        # Assert that only the movie nights where the user is the creator or a confirmed invitee are listed
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        assert any(movie["id"] == movie_night1.id for movie in response.data['results'])  # user is the creator
        assert any(movie["id"] == movie_night2.id for movie in response.data['results'])  # user is a confirmed invitee

    def test_participating_movie_nights_empty(self, authenticated_client):
        """
        Test that if the authenticated user is neither the creator nor an invitee, no movie nights are listed.
        """
        other_user = UserFactory()
        MovieNightFactory(creator=other_user, start_time=timezone.now())
        MovieNightFactory(creator=other_user, start_time=timezone.now())

        url = reverse('movienight_list')
        response = authenticated_client.get(url)

        # Assert that no movie nights are listed since the user is neither the creator nor a confirmed invitee
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 0


@pytest.mark.django_db
class TestMyMovieNightViewOrderingAndFiltering:

    def test_my_movie_night_order_by_start_time(self, authenticated_client, user):
        """
        Test ordering movie nights by 'start_time' for the current user.
        """
        # Create movie nights for the authenticated user
        movie1 = MovieFactory()
        movie2 = MovieFactory()
        MovieNightFactory(creator=user, start_time=timezone.now() + timedelta(days=2), movie=movie1)
        MovieNightFactory(creator=user, start_time=timezone.now() + timedelta(days=1), movie=movie2)

        # Access the list view with ordering by 'start_time'
        url = reverse('my_movienight_list') + "?ordering=start_time"
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        # Verify that the results are ordered by start_time
        results = response.data['results']
        assert len(results) == 2
        assert results[0]['start_time'] < results[1]['start_time']

    def test_my_movie_night_filter_by_start_time_range(self, authenticated_client, user):
        """
        Test filtering movie nights by 'start_time' range for the current user.
        """
        # Create movie nights
        movie1 = MovieFactory()
        movie2 = MovieFactory()
        MovieNightFactory(creator=user, start_time=timezone.now() + timedelta(days=1), movie=movie1)
        MovieNightFactory(creator=user, start_time=timezone.now() + timedelta(days=5), movie=movie2)

        # Filter movie nights within a start_time range
        url = reverse('my_movienight_list') + f"?start_from={timezone.now().date()}&start_to={(timezone.now() + timedelta(days=3)).date()}"
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        # Verify only one movie night is returned
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['start_time'] < (timezone.now() + timedelta(days=3)).isoformat()

@pytest.mark.django_db
class TestParticipatingMovieNightViewOrderingAndFiltering:

    def test_participating_movie_night_order_by_start_time(self, authenticated_client, user):
        """
        Test ordering movie nights by 'start_time' for participating movie nights.
        """
        # Create movie nights where the user is the creator or an invitee
        movie1 = MovieFactory()
        movie2 = MovieFactory()
        movie_night1 = MovieNightFactory(creator=user, start_time=timezone.now() + timedelta(days=2), movie=movie1)
        movie_night2 = MovieNightFactory(creator=UserFactory(), start_time=timezone.now() + timedelta(days=1), movie=movie2)

        # Add the authenticated user as an invitee
        MovieNightInvitation.objects.create(movie_night=movie_night2, invitee=user, attendance_confirmed=True, is_attending=True)

        # Access the list view with ordering by 'start_time'
        url = reverse('movienight_list') + "?ordering=start_time"
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        # Verify that the results are ordered by start_time
        results = response.data['results']
        assert len(results) == 2
        assert results[0]['start_time'] < results[1]['start_time']

    def test_participating_movie_night_filter_by_creator(self, authenticated_client, user):
        """
        Test filtering participating movie nights by creator.
        """
        # Create a movie night where the user is an invitee and the creator is another user
        movie = MovieFactory()
        other_user = UserFactory()
        movie_night1 = MovieNightFactory(creator=other_user, start_time=timezone.now(), movie=movie)
        movie_night2 = MovieNightFactory(creator=other_user, start_time=timezone.now(), movie=movie)
        # Invitee confirmed to attend
        MovieNightInvitation.objects.create(movie_night=movie_night1, invitee=user, attendance_confirmed=True, is_attending=True)
        # Invitee confirmed not to attend
        MovieNightInvitation.objects.create(movie_night=movie_night2, invitee=user, attendance_confirmed=True, is_attending=False)

        # Access the list view and filter by the creator
        url = reverse('movienight_list') + f"?creator={other_user.id}"
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        # Verify that only movie nights, where user confirmed to attend, created by the other_user are returned
        results = response.data['results']
        logger.warning (response.data)
        assert len(results) == 1
        assert results[0]['id'] == movie_night1.id
        assert results[0]['creator'] == other_user.email


@pytest.mark.django_db
class TestMovieNightDetailView:

    def test_movie_night_detail_view_creator(self, authenticated_client, user):
        """
        Test that a creator can access the details of his own movie night
        """
        movie_night = MovieNightFactory(creator=user)

        # Create the URL for the detail view using the movie night ID
        url = reverse('movienight_detail', kwargs={'pk': movie_night.pk})
        response = authenticated_client.get(url)

        # Assert that the response is successful and the data matches the movie night
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == movie_night.id
        assert response.data['creator'] == user.email

    def test_movie_night_detail_view_accepted_invitee(self, authenticated_client, user):
        """
        Test that an invited user who has accepted to attend can access the details of a movie night.
        """
        # Create another user (creator of the movie night)
        movie_creator = UserFactory()

        # Create a movie night by another user
        movie_night = MovieNightFactory(creator=movie_creator)

        # Invite the test user (authenticated_client user) to the movie night
        MovieNightInvitationFactory(
            movie_night=movie_night, 
            invitee=user, 
            attendance_confirmed=True,  # Confirmed attendance
            is_attending=True
        )

        # Create the URL for the detail view using the movie night ID
        url = reverse('movienight_detail', kwargs={'pk': movie_night.pk})
        response = authenticated_client.get(url)

        # Assert that the response is successful and the data matches the movie night
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == movie_night.id
        assert response.data['creator'] == movie_creator.email

    def test_movie_night_detail_view_unconfirmed_invitee(self, authenticated_client, user):
        """
        Test that an invited user who has not confirmed attendance can still access the movie night details.
        """
        # Create another user (creator of the movie night)
        movie_creator = UserFactory()

        # Create a movie night by another user
        movie_night = MovieNightFactory(creator=movie_creator)

        # Invite the test user (authenticated_client user) to the movie night but without confirmation
        MovieNightInvitationFactory(
            movie_night=movie_night, 
            invitee=user, 
            attendance_confirmed=False,  # Not yet confirmed
            is_attending=False
        )

        # Create the URL for the detail view using the movie night ID
        url = reverse('movienight_detail', kwargs={'pk': movie_night.pk})
        response = authenticated_client.get(url)

        # Assert that the response is successful and the data matches the movie night
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == movie_night.id
        assert response.data['creator'] == movie_creator.email

    def test_movie_night_detail_view_unauthenticated(self, any_client):
        """
        Test that an unauthenticated user cannot access the movie night detail view.
        """
        movie_night = MovieNightFactory()

        url = reverse('movienight_detail', kwargs={'pk': movie_night.pk})
        response = any_client.get(url)

        # Assert that the response is 401 Unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_movie_night_detail_view_no_permission(self, authenticated_client, user):
        """
        Test that a user who is not the creator or invitee cannot access the movie night detail.
        """
        other_user = UserFactory()  # A different user
        movie_night = MovieNightFactory(creator=other_user)

        url = reverse('movienight_detail', kwargs={'pk': movie_night.pk})
        response = authenticated_client.get(url)

        # Assert that the response is forbidden (403)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_movie_night_update_as_creator(self, authenticated_client, user):
        """
        Test that the creator of the movie night can update it.
        """
        movie_night = MovieNightFactory(creator=user)
        new_start_time = timezone.now() + timezone.timedelta(days=1)
        
        url = reverse('movienight_detail', kwargs={'pk': movie_night.pk})
        data = {
            "start_time": new_start_time.isoformat(),
            "movie": movie_night.movie.id # movie is required field
        }
        response = authenticated_client.put(url, data, format='json')
        logger.warning(response.data)

        # Assert the movie night was updated
        assert response.status_code == status.HTTP_200_OK
        movie_night.refresh_from_db()
        assert movie_night.start_time == new_start_time

    def test_movie_night_update_as_non_creator(self, authenticated_client):
        """
        Test that a non-creator cannot update the movie night.
        """
        other_user = UserFactory()
        movie_night = MovieNightFactory(creator=other_user)
        new_start_time = timezone.now() + timezone.timedelta(days=1)

        url = reverse('movienight_detail', kwargs={'pk': movie_night.pk})
        data = {
            "start_time": new_start_time.isoformat(),
        }
        response = authenticated_client.put(url, data, format='json')

        # Assert the update is forbidden
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_movie_night_destroy_as_creator(self, authenticated_client, user):
        """
        Test that the creator of the movie night can delete it.
        """
        movie_night = MovieNightFactory(creator=user)
        
        url = reverse('movienight_detail', kwargs={'pk': movie_night.pk})
        response = authenticated_client.delete(url)

        # Assert the movie night was deleted
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert MovieNight.objects.filter(pk=movie_night.pk).count() == 0

    def test_movie_night_destroy_as_non_creator(self, authenticated_client):
        """
        Test that a non-creator cannot delete the movie night.
        """
        other_user = UserFactory()
        movie_night = MovieNightFactory(creator=other_user)

        url = reverse('movienight_detail', kwargs={'pk': movie_night.pk})
        response = authenticated_client.delete(url)

        # Assert the delete is forbidden
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert MovieNight.objects.filter(pk=movie_night.pk).count() == 1

@pytest.mark.django_db
class TestInvitedMovieNightView:
    
    def test_list_invited_movie_nights(self, authenticated_client, user):
        """
        Test that the authenticated user can list movie nights they have been invited to.
        """
        # Movie nights where the user has been invited
        movie_night1 = MovieNightFactory()
        movie_night2 = MovieNightFactory()
        MovieNightInvitationFactory(invitee=user, movie_night=movie_night1)
        MovieNightInvitationFactory(invitee=user, movie_night=movie_night2)
        
        # Movie nights where the user is not invited
        other_user = UserFactory()
        movie_night3 = MovieNightFactory(creator=other_user)

        url = reverse('invited_movienight_list')  # Ensure this is the correct URL name
        response = authenticated_client.get(url)

        # Assert that only the movie nights the user was invited to are listed
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        assert len(results) == 2  # Two invitations for the user
        movie_night_ids = [movie['id'] for movie in results]
        assert movie_night1.id in movie_night_ids
        assert movie_night2.id in movie_night_ids
        assert movie_night3.id not in movie_night_ids

    def test_invited_movie_nights_empty(self, authenticated_client, user):
        """
        Test that if the authenticated user has no invitations, an empty list is returned.
        """
        other_user = UserFactory()
        MovieNightFactory(creator=other_user)  # Movie night where the user is not invited

        url = reverse('invited_movienight_list')
        response = authenticated_client.get(url)

        # Assert that no movie nights are listed since the user has no invitations
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 0

    def test_invited_movie_nights_filter_by_start_time(self, authenticated_client, user):
        """
        Test filtering invited movie nights by start time.
        """
        # Create movie nights with different start times
        movie_night1 = MovieNightFactory(start_time=timezone.now() + timezone.timedelta(days=1))
        movie_night2 = MovieNightFactory(start_time=timezone.now() + timezone.timedelta(days=5))
        MovieNightInvitationFactory(invitee=user, movie_night=movie_night1)
        MovieNightInvitationFactory(invitee=user, movie_night=movie_night2)

        # Filter movie nights starting within 3 days from now
        start_from = timezone.now().strftime('%Y-%m-%d')  # Date format
        start_to = (timezone.now() + timezone.timedelta(days=3)).strftime('%Y-%m-%d')
        # Filter movie nights starting within 3 days from now
        url = reverse('invited_movienight_list') + f"?start_from={start_from}&start_to={start_to}"
        response = authenticated_client.get(url)
        logger.warning(response.data)

        # Assert that only the correct movie night is listed
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        assert len(results) == 1  # Only one movie night should match the filter
        assert results[0]['id'] == movie_night1.id

    def test_unauthenticated_user_cannot_access(self, any_client):
        """
        Test that an unauthenticated user cannot access the invited movie nights list.
        """
        url = reverse('invited_movienight_list')
        response = any_client.get(url)

        # Assert that unauthenticated users are denied access
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
"""
NGUYEN Le Diem Quynh lnguye220903@gmail.com
"""