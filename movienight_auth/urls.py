from django.urls import path
from .views import GoogleLoginAPIView

urlpatterns = [
    path('google/', GoogleLoginAPIView.as_view(), name='google_login'),
]
