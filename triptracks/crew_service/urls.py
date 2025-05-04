from django.urls import path

from .views import *

urlpatterns = [
    path('api/crew/', CrewDetailsAPIView.as_view(), name='crew'),
    path('api/crew/<int:id>/', CrewDetailsAPIView.as_view(), name='crew_by_id'),
]