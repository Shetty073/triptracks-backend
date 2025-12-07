from rest_framework import serializers
from triptracks.identity.models.user import AppUser
from triptracks.logger import logger
from triptracks.trip_service.models import Message
from triptracks.common_utils import is_none_or_empty

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser  # or your Author model
        fields = ['id', 'first_name', 'last_name']

class TripMessagesSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Message

        fields = [
            'id', 'message', 'author', 'trip', 'created_at', 'updated_at'
        ]

        read_only_fields = [
            'id', 'author', 'trip', 'created_at', 'updated_at'
        ]

    def validate(self, data):
        required_fields = [
            'message'
        ]

        missing_fields = [field for field in required_fields if is_none_or_empty(data.get(field))]

        if missing_fields:
            logger.error(f"Mandatory parameters should not be empty: {missing_fields} => payload: {data}")
            raise serializers.ValidationError(f"Mandatory parameters should not be empty: {', '.join(missing_fields)}")
        
        return data

    def create(self, validated_data):
        request = self.context['request']

        validated_data['author'] = request.user
        validated_data['trip_id'] = request.data.get("trip_id")

        trip = Message.objects.create(**validated_data)

        return trip

    def update(self, instance, validated_data):

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()

        return instance