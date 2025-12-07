import traceback
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from knox.auth import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from triptracks.logger import logger
from triptracks.trip_service.models import Message, Message
from triptracks.trip_service.serializers import TripMessagesSerializer
from triptracks.responses import bad_request, internal_server_error, success, success_created, success_updated

class TripMessagesAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        try:
            if id:
                messages = Message.objects.filter(trip_id=id).order_by('-created_at')
                if request.GET.get('page', 1):
                    paginator = PageNumberPagination()
                    try:
                        paged_messages = paginator.paginate_queryset(messages, request)
                        serializer = TripMessagesSerializer(paged_messages, many=True)

                        paginated_response = paginator.get_paginated_response(serializer.data)
                        return success(data=paginated_response.data, custom_message="Message details fetched successfully.")
                    
                    except NotFound:
                        return bad_request(custom_message='Invalid page number')
                    
                else:
                    return bad_request(custom_message='Invalid page number')
                
            else:
                messages = Message.objects.filter(author=request.user).order_by('-created_at')
                if request.GET.get('page', 1):
                    paginator = PageNumberPagination()
                    try:
                        paged_messages = paginator.paginate_queryset(messages, request)
                        serializer = TripMessagesSerializer(paged_messages, many=True)

                        paginated_response = paginator.get_paginated_response(serializer.data)
                        return success(data=paginated_response.data, custom_message="Message details fetched successfully.")
                    
                    except NotFound:
                        return bad_request(custom_message='Invalid page number')
                    
                else:
                    return bad_request(custom_message='Invalid page number')

        except Exception as e:
            logger.exception(f"Error fetching message(s): {e}")
            return internal_server_error()

    def post(self, request):
        try:
            serializer = TripMessagesSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(author=request.user)  # Associate the message with the current user
                return success_created(custom_message="Message saved successfully!", data=serializer.data)
            return bad_request(data={"errors": serializer.errors})
        except Exception as e:
            logger.exception(f"Error creating message: {e}")
            return internal_server_error()

    def patch(self, request, id=None):
        try:
            if id:
                message = Message.objects.filter(id=id, author=request.user).first()
                if message:
                    serializer = TripMessagesSerializer(message, data=request.data, partial=True, context={'request': request})
                    if serializer.is_valid():
                        serializer.update(instance=message, validated_data=request.data)
                        return success_updated(custom_message="Message updated successfully!", data=serializer.data)
                    return bad_request(data={"errors": serializer.errors})
                return bad_request(custom_message="Message with that ID does not exist.")
        except Exception as e:
            logger.exception(f"Error updating message: {e}")
            return internal_server_error()

    def delete(self, request, id=None):
        try:
            if id:
                message = Message.objects.filter(id=id, author=request.user).first()
                if message:
                    message.delete()
                    return success_created(custom_message="Message deleted successfully!")
                return bad_request(custom_message="Message with that ID does not exist.")
        except Exception as e:
            logger.exception(f"Error deleting message: {e}")
            return internal_server_error()
