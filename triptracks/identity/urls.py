from django.urls import path

from .views import *

urlpatterns = [
    path('api/register/', RegistrationAPIView.as_view(), name='register'),
    path('api/user/profile_photo', ProfilePhotoAPIView.as_view(), name='profile_photo'),
    path('api/login/', LoginAPIView.as_view(), name='login'),
    path('api/logout/', LogoutAPIView.as_view(), name='logout'),
    path('api/logout/all/', LogoutAllAPIView.as_view(), name='logoutall'),
]
