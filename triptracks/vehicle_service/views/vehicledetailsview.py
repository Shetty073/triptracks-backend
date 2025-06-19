from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from knox.auth import TokenAuthentication
from triptracks.vehicle_service.models.vehicle import Vehicle
from triptracks.vehicle_service.serializers import VehicleDetailsSerializer
from triptracks.identity.models.user import AppUser
from triptracks.logger import logger
from triptracks.responses import (
    bad_request, internal_server_error,
    success, success_created, success_updated
)

class VehicleDetailsAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self, user):
        return Vehicle.objects.select_related("owner").filter(owner=user)

    def get(self, request, id=None):
        try:
            if id:
                vehicle = Vehicle.objects.filter(id=id, owner=request.user).first()
                if not vehicle:
                    return bad_request(custom_message="Vehicle with that ID does not exist for the current user.")
                serializer = VehicleDetailsSerializer(vehicle)
                return success(data=serializer.data)

            user_id = request.GET.get("user_id")
            if user_id:
                owner = AppUser.objects.filter(id=user_id).first()
                if not owner:
                    return bad_request(custom_message="User with the given ID does not exist.")
            else:
                owner = request.user

            vehicles_qs = self.get_queryset(owner)
            if not vehicles_qs.exists():
                return bad_request(custom_message="No vehicles found for the given user.")

            paginator = PageNumberPagination()
            try:
                paged_vehicles = paginator.paginate_queryset(vehicles_qs, request)
                serializer = VehicleDetailsSerializer(paged_vehicles, many=True)
                return success(
                    data=paginator.get_paginated_response(serializer.data).data,
                    custom_message="Vehicle details fetched successfully."
                )
            except NotFound:
                return bad_request(custom_message="Invalid page number.")

        except Exception as e:
            logger.exception("Exception in VehicleDetailsAPIView [GET]: %s", str(e))
            return internal_server_error()

    def post(self, request):
        try:
            serializer = VehicleDetailsSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                serializer.save()
                return success_created(custom_message="Vehicle saved successfully!")
            return bad_request(data={"errors": serializer.errors})
        except Exception as e:
            logger.exception("Exception in VehicleDetailsAPIView [POST]: %s", str(e))
            return internal_server_error()

    def patch(self, request, id=None):
        try:
            if not id:
                return bad_request(custom_message="Vehicle ID is required for update.")

            vehicle = Vehicle.objects.filter(id=id, owner=request.user).first()
            if not vehicle:
                return bad_request(custom_message="Vehicle with that ID does not exist or you do not have permission.")

            serializer = VehicleDetailsSerializer(vehicle, data=request.data, partial=True, context={"request": request})
            if serializer.is_valid():
                serializer.save()
                return success_updated(custom_message="Vehicle updated successfully!")
            return bad_request(data={"errors": serializer.errors})
        except Exception as e:
            logger.exception("Exception in VehicleDetailsAPIView [PATCH]: %s", str(e))
            return internal_server_error()

    def delete(self, request, id=None):
        try:
            if not id:
                return bad_request(custom_message="Vehicle ID is required for deletion.")

            vehicle = Vehicle.objects.filter(id=id, owner=request.user).first()
            if not vehicle:
                return bad_request(custom_message="Vehicle with that ID does not exist or you do not have permission.")

            vehicle.delete()
            return success_created(custom_message="Vehicle deleted successfully!")
        except Exception as e:
            logger.exception("Exception in VehicleDetailsAPIView [DELETE]: %s", str(e))
            return internal_server_error()
