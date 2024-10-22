from django.urls import path
from movienight_profile.views import ProfileView

urlpatterns = [
    path('profiles/<str:email>/', ProfileView.as_view(), name='profile_detail'),
]