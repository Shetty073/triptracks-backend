from django.urls import path

from .views import *

urlpatterns = [
    path('api/vehicle', VehicleDetailsAPIView.as_view(), name='vehicle'),
    path('api/vehicle/<int:id>', VehicleDetailsAPIView.as_view(), name='vehicle'),
]
