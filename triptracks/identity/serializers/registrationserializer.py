from rest_framework import serializers
from triptracks.identity.models import AppUser

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = AppUser
        fields = ["email", "password", "first_name", "last_name"]


    def create(self, validated_data):
        user = AppUser.objects.create_user(**validated_data)
        return user
    
