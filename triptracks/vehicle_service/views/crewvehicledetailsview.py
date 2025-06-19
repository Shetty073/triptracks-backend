from rest_framework.views import APIView
from knox.auth import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound
from triptracks.logger import logger
from django.db.models import Q, F, Case, When
from triptracks.responses import bad_request, internal_server_error, success
from triptracks.crew_service.models.crew import CrewRelationship
from triptracks.vehicle_service.models.vehicle import Vehicle
from triptracks.vehicle_service.serializers.vehicledetailsserializer import VehicleDetailsSerializer

class CrewVehicleDetailsAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user

            # Efficiently get all crew member IDs excluding the current user
            crew_member_ids = CrewRelationship.objects.filter(
                Q(user1=user) | Q(user2=user)
            ).annotate(
                crew_member=Case(
                    When(user1=user, then=F('user2')),
                    default=F('user1')
                )
            ).values_list('crew_member', flat=True).distinct()

            if not crew_member_ids:
                return bad_request(custom_message="No crew members found for current user.")

            # Efficiently filter vehicles
            vehicles = Vehicle.objects.filter(owner__in=crew_member_ids)

            paginator = PageNumberPagination()
            try:
                paged_vehicles = paginator.paginate_queryset(vehicles, request)
                vehicle_serializer = VehicleDetailsSerializer(paged_vehicles, many=True)
                paginated_response = paginator.get_paginated_response(vehicle_serializer.data)
                return success(
                    data=paginated_response.data,
                    custom_message="Vehicle details fetched successfully."
                )

            except NotFound:
                return bad_request(custom_message="Invalid page number")

        except Exception as e:
            logger.exception(f"Exception in CrewVehicleDetailsAPIView: {e}")
            return internal_server_error()
