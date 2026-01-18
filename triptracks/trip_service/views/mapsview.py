from rest_framework.views import APIView
from knox.auth import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from triptracks.logger import logger
from triptracks.responses import bad_request, success, service_unavailable
from geomaps_sdk import LocationClient, GeoapifyProvider, GeoPoint
from django.conf import settings


class MapsAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            address = request.query_params.get("address")

            auto_complete = request.query_params.get("auto_complete")

            source_lat = request.query_params.get("source_lat")
            source_long = request.query_params.get("source_long")

            dest_lat = request.query_params.get("dest_lat")
            dest_long = request.query_params.get("dest_long")

            if not (address or (source_lat and source_long and dest_lat and dest_long)):
                return bad_request(custom_message="Invalid parameters")

            if address:
                with LocationClient(
                    provider=GeoapifyProvider(api_key=settings.GEOAPIFY_API_KEY)
                ) as client:
                    if auto_complete == "1":
                        results = client.autocomplete(address)

                        return success({"results": [res.to_dict() for res in results]})
                    else:
                        results = client.geocode(address)

                        return success({"results": [res.to_dict() for res in results]})

            else:
                with LocationClient(
                    provider=GeoapifyProvider(api_key=settings.GEOAPIFY_API_KEY)
                ) as client:
                    source = GeoPoint(float(source_lat), float(source_long))
                    target = GeoPoint(float(dest_lat), float(dest_long))

                    route = client.route(source, target)

                    distance_km = route.distance_km
                    duration_minutes = route.duration_minutes

                    return success({"distance_km": distance_km, "duration_minutes": duration_minutes})

        except Exception as e:
            logger.exception(f"Error : {e}")
            return service_unavailable(custom_message="Maps SDK failed to respond properly")

