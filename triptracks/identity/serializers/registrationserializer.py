import uuid
from rest_framework import serializers
from triptracks.common_utils import is_none_or_empty
from triptracks.identity.models import AppUser

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = AppUser
        fields = ["email", "password", "password_confirm", "first_name", "last_name"]

    def validate(self, data):        
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        password = data.get("password")
        password_confirm = data.get("password_confirm")

        if not all([is_none_or_empty(first_name), is_none_or_empty(last_name), is_none_or_empty(email)]):
            raise serializers.ValidationError("Mandatory parameters should not be empty")

        if password != password_confirm:
            raise serializers.ValidationError("Password and confirm_password should match")

        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm", None)
        user = AppUser.objects.create_user(**validated_data)
        return user
    
