import uuid
from rest_framework import serializers
from triptracks.logger import logger
from triptracks.common_utils import is_none_or_empty
from triptracks.identity.models import AppUser

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = AppUser
        fields = ["email", "password", "password_confirm", "first_name", "last_name"]

    def validate(self, data):        
        required_fields = ["email", "password", "password_confirm", "first_name", "last_name"]

        missing_fields = [field for field in required_fields if is_none_or_empty(data.get(field))]

        if missing_fields:
            logger.error(f"Mandatory parameters should not be empty: {missing_fields} => payload: {data}")
            raise serializers.ValidationError(f"Mandatory parameters should not be empty: {', '.join(missing_fields)}")

        password = data.get('password')
        password_confirm = data.get('password_confirm')

        if password != password_confirm:
            raise serializers.ValidationError("Password and confirm_password should match")

        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm", None)
        user = AppUser.objects.create_user(**validated_data)
        return user
    
