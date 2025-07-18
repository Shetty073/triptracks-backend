from django.contrib.auth.signals import user_logged_in
from rest_framework.views import APIView
from knox.models import AuthToken

from triptracks.crew_service.serializers.crewdetailserializer import AppUserSerializer
from triptracks.logger import logger
from triptracks.identity.serializers import LoginSerializer
from triptracks.responses import forbidden, internal_server_error, success


class LoginAPIView(APIView):
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            if not serializer.is_valid():
                return forbidden(data={"errors": serializer.errors})

            user = serializer.validated_data["user"]
            _, token = AuthToken.objects.create(user)

            user_logged_in.send(sender=user.__class__,
                            request=request, user=user)
            
            app_serializer = AppUserSerializer(user)

            return success({"user": app_serializer.data, "token": token})
        
        except Exception as e:
            logger.exception(f"Exception in LoginAPIView: {e}")
            return internal_server_error()
