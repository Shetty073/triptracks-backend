from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import NotFound
from knox.auth import TokenAuthentication
from django.db.models import Q, Subquery
from triptracks.logger import logger
from triptracks.responses import (
    bad_request, internal_server_error,
    success, success_created, success_updated
)
from triptracks.identity.models.user import AppUser
from triptracks.crew_service.models.crew import CrewRelationship, CrewRequest
from triptracks.crew_service.serializers.crewdetailserializer import (
    CrewRelationshipSerializer, CrewRequestSerializer, AppUserSerializer
)


class CrewDetailsAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def paginate(self, request, queryset, serializer_class, context=None):
        paginator = PageNumberPagination()
        try:
            paged_qs = paginator.paginate_queryset(queryset, request)
            serializer = serializer_class(paged_qs, many=True, context=context or {})
            return paginator.get_paginated_response(serializer.data)
        except NotFound:
            return bad_request(custom_message="Invalid page number")

    def get(self, request, id=None):
        try:
            user = request.user
            query_params = request.GET
            email_or_username = query_params.get("email_or_username")
            open_requests = query_params.get("open_requests")

            if id:
                crew_user = AppUser.objects.filter(id=id).only("id", "email").first()
                if not crew_user:
                    return bad_request(custom_message="User with that ID does not exist.")

                crew_members = CrewRelationship.objects.filter(
                    Q(user1=crew_user) | Q(user2=crew_user)
                ).select_related("user1", "user2")

                if not crew_members.exists():
                    return bad_request(custom_message=f"No crew members found for user {crew_user.email}.")

                return self.paginate(request, crew_members, CrewRelationshipSerializer, context={'current_user_id': id})

            if open_requests:
                crew_requests = CrewRequest.objects.filter(accepted=False, to_user=user).select_related("from_user")
                if not crew_requests.exists():
                    return success(custom_message="No new request found")

                return self.paginate(request, crew_requests, CrewRequestSerializer)

            if email_or_username:
                # Find matching users not already involved in a crew request or relationship
                sent_ids = CrewRequest.objects.filter(from_user=user).values_list("to_user_id", flat=True)
                received_ids = CrewRequest.objects.filter(to_user=user).values_list("from_user_id", flat=True)

                users = AppUser.objects.filter(
                    Q(email__icontains=email_or_username) | Q(username__icontains=email_or_username)
                ).exclude(
                    id=user.id
                ).exclude(
                    Q(id__in=sent_ids) | Q(id__in=received_ids)
                )

                if not users.exists():
                    return success(custom_message="No users found.")

                return self.paginate(request, users, AppUserSerializer, context={"request": request})

            # Default: fetch current user's crew
            crew_members = CrewRelationship.objects.filter(
                Q(user1=user) | Q(user2=user)
            ).select_related("user1", "user2")

            if not crew_members.exists():
                return bad_request(custom_message="No crew members found for current user.")

            return self.paginate(request, crew_members, CrewRelationshipSerializer, context={'current_user_id': user.id})

        except Exception as e:
            logger.exception(f"Error fetching crew: {e}")
            return internal_server_error()

    def post(self, request):
        try:
            serializer = CrewRequestSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                from_user = request.user
                to_user = serializer.validated_data.get("to_user")

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
            if not id:
                return bad_request(custom_message="Crew request ID is required.")

            crew_request = CrewRequest.objects.filter(
                id=id, to_user=request.user, accepted=False
            ).select_related("from_user", "to_user").first()

            if not crew_request:
                return bad_request(custom_message="Crew request not found or already processed.")

            if request.data.get("accept"):
                crew_request.accepted = True
                crew_request.save()
                CrewRelationship.objects.create(
                    user1=crew_request.from_user,
                    user2=crew_request.to_user
                )
                return success_updated(custom_message="Crew request accepted.")
            else:
                crew_request.delete()
                return success_updated(custom_message="Crew request rejected.")

        except Exception as e:
            logger.exception(f"Error responding to crew request: {e}")
            return internal_server_error()

    def delete(self, request, id=None):
        try:
            if not id:
                return bad_request(custom_message="Crew relationship ID is required.")

            crew_user = AppUser.objects.filter(id=id).only("id").first()
            if not crew_user:
                return bad_request(custom_message="User not found.")

            crew_relation = CrewRelationship.objects.filter(
                Q(user1=request.user, user2=crew_user) |
                Q(user1=crew_user, user2=request.user)
            ).first()

            if not crew_relation:
                return bad_request(custom_message="Unable to find the user in your crew list!")

            crew_relation.delete()

            CrewRequest.objects.filter(
                Q(from_user=request.user, to_user=crew_user, accepted=True) |
                Q(from_user=crew_user, to_user=request.user, accepted=True)
            ).delete()

            return success_updated(custom_message="User removed from your crew successfully!")

        except Exception as e:
            logger.exception(f"Error deleting crew relationship: {e}")
            return internal_server_error()
