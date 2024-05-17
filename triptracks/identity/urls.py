from django.urls import path

from .views import *

urlpatterns = [
    path('api/login/', LoginAPIView.as_view(), name='login'),
    path('api/register/', RegistrationAPIView.as_view(), name='register'),
]
