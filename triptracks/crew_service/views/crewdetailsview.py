from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound
from knox.auth import TokenAuthentication
from triptracks.crew_service.serializers.crewdetailserializer import CrewRelationshipSerializer, CrewRequestSerializer, AppUserSerializer
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
                
                if not crew_members.exists():
                    return bad_request(custom_message=f"No crew members found for user {crew_user.email}.")

                if request.GET.get('page', 1):
                    paginator = PageNumberPagination()
                    try:
                        paged_crew_members = paginator.paginate_queryset(crew_members, request)
                        serializer = CrewRelationshipSerializer(paged_crew_members, many=True, context={'current_user_id': id})

                        paginated_response = paginator.get_paginated_response(serializer.data)
                        return success(data=paginated_response.data, custom_message="Crew details fetched successfully.")
            
                    except NotFound:
                        return bad_request(custom_message='Invalid page number')
                
                else:
                    return bad_request(custom_message='Invalid page number')
            
            else:
                if request.GET.get('open_requests'):
                    crew_requests = CrewRequest.objects.filter(accepted=False, to_user=request.user)

                    if not crew_requests.exists():
                        return success(custom_message="No new request found")

                    if request.GET.get('page', 1):
                        paginator = PageNumberPagination()
                        try:
                            paged_crew_requests = paginator.paginate_queryset(crew_requests, request)
                            serializer = CrewRequestSerializer(paged_crew_requests, many=True)

                            paginated_response = paginator.get_paginated_response(serializer.data)
                            return success(data=paginated_response.data, custom_message="Crew request details fetched successfully.")
                
                        except NotFound:
                            return bad_request(custom_message='Invalid page number')
                    
                    else:
                        return bad_request(custom_message='Invalid page number')

                elif request.GET.get('email_or_username'):
                    email_or_username = request.GET.get('email_or_username')

                    if not email_or_username:
                        return bad_request(custom_message="Invalid parameter value for: email_or_username")

                    # Users matching the search, excluding current logged in user
                    users_qs = AppUser.objects.filter(
                        Q(email__icontains=email_or_username) | Q(username__icontains=email_or_username)
                    ).exclude(id=request.user.id)

                    # IDs of users who already have a pending request from the current logged in user
                    requested_user_ids = CrewRequest.objects.filter(
                        from_user=request.user
                    ).values_list('to_user_id', flat=True)

                    # Exclude users already requested
                    users_qs = users_qs.exclude(id__in=requested_user_ids)

                    if not users_qs.exists():
                        return success(custom_message="No users found.")

                    paginator = PageNumberPagination()
                    try:
                        paged_users = paginator.paginate_queryset(users_qs, request)
                        serializer = AppUserSerializer(paged_users, many=True, context={'request': request})
                        return paginator.get_paginated_response(serializer.data)
                    except NotFound:
                        return bad_request(custom_message="Invalid page number.")

                else:
                    # List all crew members for the authenticated user
                    crew_members = CrewRelationship.objects.filter(
                        Q(user1=request.user) | Q(user2=request.user)
                    )

                    if not crew_members.exists():
                        return bad_request(custom_message=f"No crew members found for current user.")

                    if request.GET.get('page', 1):
                        paginator = PageNumberPagination()
                        try:
                            paged_crew_members = paginator.paginate_queryset(crew_members, request)
                            serializer = CrewRelationshipSerializer(paged_crew_members, many=True, context={'current_user_id': request.user.id})

                            paginated_response = paginator.get_paginated_response(serializer.data)
                            return success(data=paginated_response.data, custom_message="Crew details fetched successfully.")
                
                        except NotFound:
                            return bad_request(custom_message='Invalid page number')
                    
                    else:
                        return bad_request(custom_message='Invalid page number')

        except Exception as e:
            logger.exception(f"Error fetching crew: {e}")
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
            logger.exception(f"Error creating crew request: {e}")
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
            logger.exception(f"Error responding to crew request: {e}")
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

                crew_request = CrewRequest.objects.filter(
                    Q(from_user=request.user, to_user=crew_user, accepted=True) | 
                    Q(from_user=crew_user, to_user=request.user, accepted=True)
                ).first()

                if crew_request:
                    crew_request.delete()

                return success_updated(custom_message="User removed from your crew successfully!")
            
            return bad_request(custom_message="Crew relationship ID is required.")
        
        except Exception as e:
            logger.exception(f"Error deleting crew relationship: {e}")
            return internal_server_error()
