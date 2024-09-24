from django.contrib.auth.signals import user_logged_out
import traceback
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from knox.auth import TokenAuthentication

from triptracks.logger import logger
from triptracks.responses import bad_request, internal_server_error, success_updated


class LogoutAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user

            if user:
                request._auth.delete()
                user_logged_out.send(sender=user,
                                    request=request, user=user)

                return success_updated(custom_message="User logged out from current session")
            
            return bad_request(data={"errors": "Invalid user"})
        
        except Exception as e:
            trbk = traceback.format_exc()
            logger.error(f"{e}, traceback: {trbk}")
            return internal_server_error()
