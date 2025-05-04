from rest_framework import serializers
from triptracks.identity.models.user import AppUser
from triptracks.crew_service.models.crew import CrewRelationship, CrewRequest


class AppUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ('id', 'email', 'first_name', 'last_name', 'username', 'profile_photo')
        read_only_fields = ('id', 'username')

class CrewRequestSerializer(serializers.ModelSerializer):
    from_user = AppUserSerializer(read_only=True)
    to_user = serializers.PrimaryKeyRelatedField(queryset=AppUser.objects.all())

    class Meta:
        model = CrewRequest
        fields = ('id', 'from_user', 'to_user', 'created_at', 'accepted')
        read_only_fields = ('id', 'created_at')

    def create(self, validated_data):
        """Override create method to ensure from_user is set correctly."""
        from_user = self.context['request'].user
        to_user = validated_data['to_user']
        crew_request = CrewRequest.objects.create(from_user=from_user, to_user=to_user)
        return crew_request

# class CrewRelationshipSerializer(serializers.ModelSerializer):
#     user1 = AppUserSerializer()
#     user2 = AppUserSerializer()

#     class Meta:
#         model = CrewRelationship
#         fields = ('id', 'user1', 'user2', 'created_at')
#         read_only_fields = ('id', 'created_at')

class CrewRelationshipSerializer(serializers.ModelSerializer):
    requested_user = serializers.SerializerMethodField()

    class Meta:
        model = CrewRelationship
        fields = ('id', 'requested_user', 'created_at')
        read_only_fields = ('id', 'created_at')

    def get_requested_user(self, obj):
        current_user_id = self.context.get('current_user_id')

        # Return the user who is not the current user
        if obj.user1.id == current_user_id:
            return {
                "id": obj.user2.id,
                "email": obj.user2.email,
                "first_name": obj.user2.first_name,
                "last_name": obj.user2.last_name,
                "username": obj.user2.username,
            }
        
        elif obj.user2.id == current_user_id:
            return {
                "id": obj.user1.id,
                "email": obj.user1.email,
                "first_name": obj.user1.first_name,
                "last_name": obj.user1.last_name,
                "username": obj.user1.username,
            }
        
        return None
