# """
# Test cases for API throttling in the movies app.

# This file contains tests for both anonymous users and authenticated users
# to ensure that the throttling mechanisms for burst and sustained requests 
# are functioning correctly as defined in the settings.

# """
# import pytest
# from rest_framework import status
# from django.urls import reverse
# from django.core.cache import cache
# import time

# @pytest.mark.django_db
# class TestThrottleAnonUser:
#     """Test throttling for anonymous users."""
    
#     def setup_method(self):
#         self.url = reverse('movie_list')  # Use an endpoint that is throttled
#         cache.clear()

#     def test_anon_burst_throttle(self, any_client):
#         """Test that anonymous users hit burst throttle after 10 requests per minute."""
#         # Send 10 requests within a minute, which should be allowed
#         for _ in range(10):
#             response = any_client.get(self.url)
#             assert response.status_code == status.HTTP_200_OK
        
#         # The 11th request should be throttled
#         response = any_client.get(self.url)
#         assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS  # Throttled

#     # def test_anon_sustained_throttle(self, any_client):
#     #     """Test that anonymous users hit sustained throttle after 500 requests per day."""
#     #     # Send 500 requests, which should be allowed
#     #     for _ in range(500):
#     #         response = any_client.get(self.url)
#     #         assert response.status_code == status.HTTP_200_OK
        
#     #     # The 501st request should be throttled
#     #     response = any_client.get(self.url)
#     #     assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS  # Throttled


# @pytest.mark.django_db
# class TestThrottleAuthenticatedUser:
#     """Test throttling for authenticated users."""
    
#     def setup_method(self):
#         self.url = reverse('movie_list')  # Use an endpoint that is throttled
#         cache.clear()

#     def test_user_burst_throttle(self, authenticated_client):
#         """Test that authenticated users hit burst throttle after 100 requests per minute."""
#         # Send 100 requests within a minute, which should be allowed
#         for _ in range(100):
#             response = authenticated_client.get(self.url)
#             assert response.status_code == status.HTTP_200_OK
        
#         # The 101st request should be throttled
#         response = authenticated_client.get(self.url)
#         assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS  # Throttled

#     # def test_user_sustained_throttle(self, authenticated_client):
#     #     """Test that authenticated users hit sustained throttle after 5000 requests per day."""
#     #     # Send 5000 requests, which should be allowed
#     #     for _ in range(5000):
#     #         response = authenticated_client.get(self.url)
#     #         assert response.status_code == status.HTTP_200_OK
        
#     #     # The 5001st request should be throttled
#     #     response = authenticated_client.get(self.url)
#     #     assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS  # Throttled

# """
# NGUYEN Le Diem Quynh lnguye220903@gmail.com
# """