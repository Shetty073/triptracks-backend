from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from knox.auth import TokenAuthentication
from triptracks.logger import logger
from triptracks.responses import bad_request, internal_server_error, success
from django.core.exceptions import ValidationError


class ProfilePhotoAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            photo = request.FILES.get("profile_photo")

            if not photo:
                return bad_request(data={"error": "No profile photo uploaded."})

            # Optional: validate file size/type here

            user.profile_photo = photo
            user.save()

            return success(custom_message="Profile photo updated successfully!")

        except ValidationError as ve:
            return bad_request(data={"error": str(ve)})

        except Exception as e:
            logger.exception(f"Exception in ProfilePhotoAPIView: {e}")
            return internal_server_error()
