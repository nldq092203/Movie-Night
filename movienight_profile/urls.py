from django.urls import path
from movienight_profile.views import ProfileView, UploadAvatarView

urlpatterns = [
    path('profiles/upload-avt/', UploadAvatarView.as_view(), name='upload_avt'),
    path('profiles/<str:email>/', ProfileView.as_view(), name='profile_detail'),
]