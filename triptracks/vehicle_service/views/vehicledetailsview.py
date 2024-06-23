# users/views.py
import traceback
from rest_framework.views import APIView
from knox.auth import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from triptracks.vehicle_service.serializers import VehicleDetailsSerializer
from triptracks.responses import bad_request, internal_server_error, success_created

class VehicleDetailsAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = VehicleDetailsSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return success_created(custom_message="Vehicle saved successfully!")
            
            return bad_request(data={"errors": serializer.errors})
    
        except Exception as e:
            trbk = traceback.format_exc()
            print(e, trbk)
            return internal_server_error()
