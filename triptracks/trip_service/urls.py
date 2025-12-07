from django.urls import path

from .views import *

urlpatterns = [
    path('api/trip/', TripDetailsAPIView.as_view(), name='trip'),
    path('api/trip/<int:id>/', TripDetailsAPIView.as_view(), name='trip_by_id'),
    path('api/trip/messages/', TripMessagesAPIView.as_view(), name='trip_messages'),
    path('api/trip/messages/<int:id>/', TripMessagesAPIView.as_view(), name='trip_messages_by_id'),
]
