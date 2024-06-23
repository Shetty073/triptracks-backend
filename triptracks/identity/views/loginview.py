from hashlib import sha256
import traceback
from rest_framework.views import APIView
from knox.models import AuthToken

from triptracks.identity.serializers import LoginSerializer
from triptracks.responses import internal_server_error, success


class LoginAPIView(APIView):
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = serializer.validated_data["user"]
            _, token = AuthToken.objects.create(user)

            return success({"token": token})
        
        except Exception as e:
            trbk = traceback.format_exc()
            print(e, trbk)
            return internal_server_error()
