import traceback
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from knox.auth import TokenAuthentication
from triptracks.crew_service.serializers.crewdetailserializer import CrewRelationshipSerializer, CrewRequestSerializer
from triptracks.identity.models.user import AppUser
from triptracks.logger import logger
from django.db.models import Q
from triptracks.responses import bad_request, internal_server_error, success, success_created, success_updated
from triptracks.crew_service.models.crew import CrewRelationship, CrewRequest

class CrewDetailsAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        try:
            # Listing crew members of the user with provided id
            if id:
                crew_user = AppUser.objects.filter(id=id).first()
                if not crew_user:
                    return bad_request(custom_message="User with that ID does not exist.")

                crew_members = CrewRelationship.objects.filter(
                    Q(user1=crew_user) | Q(user2=crew_user)
                )

                if crew_members.exists():
                    serializer = CrewRelationshipSerializer(crew_members, many=True, context={'current_user_id': id})
                    return success(data=serializer.data)
                
                return bad_request(custom_message=f"No crew members found for user {crew_user.email}.")
            
            else:
                if request.GET.get('open_requests'):
                    crew_requests = CrewRequest.objects.filter(accepted=False, to_user=request.user)
                    if crew_requests.exists():
                        open_crew_requests = crew_requests.all()
                        crew_request_serializer = CrewRequestSerializer(open_crew_requests, many=True)
                        return success(data=crew_request_serializer.data, custom_message="New crew requests open")
                    
                    return success(custom_message="No new request found")
                else:
                    # List all crew members for the authenticated user
                    crew_members = CrewRelationship.objects.filter(
                        Q(user1=request.user) | Q(user2=request.user)
                    )

                    if crew_members.exists():
                        serializer = CrewRelationshipSerializer(crew_members, many=True, context={'current_user_id': request.user.id})
                        return success(data=serializer.data)
                    
                    return bad_request(custom_message="No crew members found.")
        except Exception as e:
            trbk = traceback.format_exc()
            logger.error(f"Error fetching crew: {e}, traceback: {trbk}")
            return internal_server_error()

    def post(self, request):
        try:
            serializer = CrewRequestSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                from_user = request.user
                to_user = serializer.validated_data.get('to_user')

                if CrewRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
                    return bad_request(custom_message="Crew request already sent.")

                serializer.save(from_user=from_user)
                return success_created(custom_message="Crew request sent successfully!", data=serializer.data)
            
            return bad_request(data={"errors": serializer.errors})
        
        except Exception as e:
            trbk = traceback.format_exc()
            logger.error(f"Error creating crew request: {e}, traceback: {trbk}")
            return internal_server_error()

    def patch(self, request, id=None):
        try:
            if id:
                crew_request = CrewRequest.objects.filter(id=id, to_user=request.user, accepted=False).first()
                if not crew_request:
                    return bad_request(custom_message="Crew request from that ID does not exist or is already processed.")

                accept = request.data.get('accept')
                if accept:
                    # Accept the crew request and create the relationship
                    crew_request.accepted = True
                    crew_request.save()
                    CrewRelationship.objects.create(user1=crew_request.from_user, user2=crew_request.to_user)

                    return success_updated(custom_message="Crew request accepted.")
                
                else:
                    # Reject the crew request
                    crew_request.delete()
                    return success_updated(custom_message="Crew request rejected.")
                
            return bad_request(custom_message="Crew request ID is required.")
        except Exception as e:
            trbk = traceback.format_exc()
            logger.error(f"Error responding to crew request: {e}, traceback: {trbk}")
            return internal_server_error()

    def delete(self, request, id=None):
        try:
            logger.info(f"request.user.id: {request.user.id}")
            if id:
                crew_user = AppUser.objects.filter(id=id).first()
                crew_relation = CrewRelationship.objects.filter(
                    Q(user1=request.user, user2=crew_user) | 
                    Q(user1=crew_user, user2=request.user)
                ).first()

                if not crew_relation:
                    return bad_request(custom_message="Unable to find the user in your crew list!")
                
                crew_relation.delete()
                return success_updated(custom_message="User removed from your crew successfully!")
            
            return bad_request(custom_message="Crew relationship ID is required.")
        
        except Exception as e:
            trbk = traceback.format_exc()
            logger.error(f"Error deleting crew relationship: {e}, traceback: {trbk}")
            return internal_server_error()
