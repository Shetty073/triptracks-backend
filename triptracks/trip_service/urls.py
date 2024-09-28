from django.urls import path

from .views import *

urlpatterns = [
    path('api/trip/', TripDetailsAPIView.as_view(), name='trip'),
    path('api/trip/<int:id>/', TripDetailsAPIView.as_view(), name='trip_by_id'),
]
