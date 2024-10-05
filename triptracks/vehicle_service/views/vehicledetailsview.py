import traceback
from django.forms.models import model_to_dict
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from knox.auth import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from triptracks.identity.models.user import AppUser
from triptracks.logger import logger
from triptracks.vehicle_service.models.vehicle import Vehicle
from triptracks.vehicle_service.serializers import VehicleDetailsSerializer
from triptracks.responses import bad_request, internal_server_error, success, success_created, success_updated

class VehicleDetailsAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        try:
            if id:
                vehicle = Vehicle.objects.filter(id=id, owner=request.user).first()
                if vehicle:
                    return success(data=model_to_dict(vehicle))
                
                else:
                    return bad_request(custom_message="Vehicle with that id does not exist")
            
            else:
                if request.GET.get('user_id'):
                    vehicles = Vehicle.objects.filter(owner=AppUser.objects.filter(id=request.GET.get('user_id')).first())
                else:
                    vehicles = Vehicle.objects.filter(owner=request.user)
                
                if not vehicles.exists():
                    return bad_request(custom_message="No vehicle exists for the given user.")

                if request.GET.get('page', 1):
                    paginator = PageNumberPagination()
                    try:
                        paged_vehicles = paginator.paginate_queryset(vehicles, request)
                        vehicle_serializer = VehicleDetailsSerializer(paged_vehicles, many=True)

                        paginated_response = paginator.get_paginated_response(vehicle_serializer.data)
                        return success(data=paginated_response.data, custom_message="Vehicle details fetched successfully.")
            
                    except NotFound:
                        return bad_request(custom_message='Invalid page number')
                
                else:
                    return bad_request(custom_message='Invalid page number')
        
        except Exception as e:
            trbk = traceback.format_exc()
            logger.error(f"{e}, traceback: {trbk}")
            return internal_server_error()

    def post(self, request):
        try:
            serializer = VehicleDetailsSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return success_created(custom_message="Vehicle saved successfully!")
            
            return bad_request(data={"errors": serializer.errors})
    
        except Exception as e:
            trbk = traceback.format_exc()
            logger.error(f"{e}, traceback: {trbk}")
            return internal_server_error()
        
    def patch(self, request, id=None):
        try:
            if id:
                req_data = request.data
                req_data["method"] = "PATCH"
                serializer = VehicleDetailsSerializer(data=req_data, context={'request': request})
                if serializer.is_valid():
                    vehicle = Vehicle.objects.filter(id=id, owner=request.user).first()
                    serializer.update(instance=vehicle, validated_data=req_data)

                    return success_updated(custom_message="Vehicle updated successfully!")
                
                else:
                    return bad_request(data={"errors": serializer.errors})
            
            return bad_request(custom_message="Vehicle with that id does not exist")
        
        except Exception as e:
            trbk = traceback.format_exc()
            logger.error(f"{e}, traceback: {trbk}")
            return internal_server_error()

    def delete(self, request, id=None):
        try:
            if id:
                vehicle = Vehicle.objects.filter(id=id, owner=request.user).first()
                if vehicle:
                    vehicle.delete()

                    return success_created(custom_message="Vehicle deleted successfully!")
            
            return bad_request(custom_message="Vehicle with that id does not exist")
        
        except Exception as e:
            trbk = traceback.format_exc()
            logger.error(f"{e}, traceback: {trbk}")
            return internal_server_error()
