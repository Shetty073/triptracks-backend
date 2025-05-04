import traceback
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from knox.auth import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from triptracks.logger import logger
from triptracks.trip_service.models import Trip
from triptracks.trip_service.serializers import TripDetailsSerializer
from triptracks.responses import bad_request, internal_server_error, success, success_created, success_updated

class TripDetailsAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        try:
            if id:
                trip = Trip.objects.filter(id=id).first()  # Ensure it's filtered by the current user
                if trip:
                    serializer = TripDetailsSerializer(trip)
                    return success(data=serializer.data)
                else:
                    return bad_request(custom_message="Trip with that ID does not exist.")
                
            else:
                trips = Trip.objects.filter(organizer=request.user)
                if request.GET.get('page', 1):
                    paginator = PageNumberPagination()
                    try:
                        paged_trips = paginator.paginate_queryset(trips, request)
                        serializer = TripDetailsSerializer(paged_trips, many=True)

                        paginated_response = paginator.get_paginated_response(serializer.data)
                        return success(data=paginated_response.data, custom_message="Trip details fetched successfully.")
                    
                    except NotFound:
                        return bad_request(custom_message='Invalid page number')
                    
                else:
                    return bad_request(custom_message='Invalid page number')

        except Exception as e:
            logger.exception(f"Error fetching trip(s): {e}")
            return internal_server_error()

    def post(self, request):
        try:
            serializer = TripDetailsSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(organizer=request.user)  # Associate the trip with the current user
                return success_created(custom_message="Trip saved successfully!", data=serializer.data)
            return bad_request(data={"errors": serializer.errors})
        except Exception as e:
            logger.exception(f"Error creating trip: {e}")
            return internal_server_error()

    def patch(self, request, id=None):
        try:
            if id:
                trip = Trip.objects.filter(id=id, organizer=request.user).first()
                if trip:
                    serializer = TripDetailsSerializer(trip, data=request.data, partial=True, context={'request': request})
                    if serializer.is_valid():
                        serializer.update(instance=trip, validated_data=request.data)
                        return success_updated(custom_message="Trip updated successfully!", data=serializer.data)
                    return bad_request(data={"errors": serializer.errors})
                return bad_request(custom_message="Trip with that ID does not exist.")
        except Exception as e:
            logger.exception(f"Error updating trip: {e}")
            return internal_server_error()

    def delete(self, request, id=None):
        try:
            if id:
                trip = Trip.objects.filter(id=id, organizer=request.user).first()
                if trip:
                    trip.delete()
                    return success_created(custom_message="Trip deleted successfully!")
                return bad_request(custom_message="Trip with that ID does not exist.")
        except Exception as e:
            logger.exception(f"Error deleting trip: {e}")
            return internal_server_error()
