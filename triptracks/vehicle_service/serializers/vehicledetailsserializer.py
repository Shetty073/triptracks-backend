from rest_framework import serializers
from triptracks.vehicle_service.models import Vehicle
from triptracks.common_utils import is_none_or_empty

class VehicleDetailsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Vehicle
        fields = ["id", "name", "make", "model", "type", "fuel_type", "mileage"]

    def validate(self, data):
        name = data.get("name")
        make = data.get("make")
        model = data.get("model")
        type = data.get("type")
        fuel_type = data.get("fuel_type")
        mileage = data.get("mileage")

        if not all([is_none_or_empty(name), is_none_or_empty(make), is_none_or_empty(model), is_none_or_empty(type), is_none_or_empty(fuel_type), is_none_or_empty(mileage)]):
            raise serializers.ValidationError("Mandatory parameters should not be empty")
        
        return data

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        vehicle = Vehicle.objects.create(**validated_data)
        return vehicle
