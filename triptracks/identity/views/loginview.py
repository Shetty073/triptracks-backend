import traceback
from django.contrib.auth.signals import user_logged_in
from rest_framework.views import APIView
from knox.models import AuthToken

from triptracks.logger import logger
from triptracks.identity.serializers import LoginSerializer
from triptracks.responses import internal_server_error, success


class LoginAPIView(APIView):
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = serializer.validated_data["user"]
            _, token = AuthToken.objects.create(user)

            user_logged_in.send(sender=user.__class__,
                            request=request, user=user)

            return success({"token": token})
        
        except Exception as e:
            trbk = traceback.format_exc()
            logger.error(f"{e}, {trbk}")
            return internal_server_error()
