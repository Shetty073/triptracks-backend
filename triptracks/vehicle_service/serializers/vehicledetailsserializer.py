from rest_framework import serializers
from triptracks.vehicle_service.models import Vehicle
from triptracks.common_utils import is_none_or_empty
from triptracks.logger import logger

class VehicleDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle

        fields = ['id', 'name', 'make', 'model', 'type', 'fuel_type', 'mileage']

        read_only_fields = ["id"]

    def validate(self, data):
        required_fields = ['name', 'make', 'model', 'type', 'fuel_type', 'mileage']

        missing_fields = [field for field in required_fields if is_none_or_empty(data.get(field))]

        if missing_fields:
            logger.error(f"Mandatory parameters should not be empty: {missing_fields} => payload: {data}")
            raise serializers.ValidationError(f"Mandatory parameters should not be empty: {', '.join(missing_fields)}")

        return data

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user

        vehicle = Vehicle.objects.create(**validated_data)
        return vehicle
    
    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()
        return instance
