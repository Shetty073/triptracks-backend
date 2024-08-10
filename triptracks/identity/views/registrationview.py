# users/views.py
import traceback
from rest_framework.views import APIView
from triptracks.logger import logger
from triptracks.identity.serializers import RegistrationSerializer
from triptracks.responses import bad_request, internal_server_error, success_created

class RegistrationAPIView(APIView):
    def post(self, request):
        try:
            serializer = RegistrationSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return success_created(custom_message="User created successfully!")
            
            return bad_request(data={"errors": serializer.errors})
    
        except Exception as e:
            trbk = traceback.format_exc()
            logger.error(f"{e}, {trbk}")
            return internal_server_error()
