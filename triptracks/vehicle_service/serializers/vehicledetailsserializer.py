from rest_framework import serializers
from triptracks.vehicle_service.models import Vehicle
from triptracks.common_utils import is_none_or_empty

class VehicleDetailsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Vehicle
        fields = ["id", "name", "make", "model", "type", "fuel_type", "mileage"]
        read_only_fields = ["id"]

    def validate(self, data):
        print(data)
        name = data.get("name")
        make = data.get("make")
        model = data.get("model")
        type = data.get("type")
        fuel_type = data.get("fuel_type")
        mileage = data.get("mileage")

        if data.get("method") == "PATCH":
            print("Inside here")
            if not any([is_none_or_empty(name), is_none_or_empty(make), is_none_or_empty(model), is_none_or_empty(type), is_none_or_empty(fuel_type), is_none_or_empty(mileage)]):
                raise serializers.ValidationError("Mandatory parameters should not be empty")
        else:
            print("Inside here")
            if not all([is_none_or_empty(name), is_none_or_empty(make), is_none_or_empty(model), is_none_or_empty(type), is_none_or_empty(fuel_type), is_none_or_empty(mileage)]):
                raise serializers.ValidationError("Mandatory parameters should not be empty")
        
        return data

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        vehicle = Vehicle.objects.create(**validated_data)

        return vehicle
    
    def update(self, instance, validated_data):
        # Custom update method to handle partial updates
        instance.name = validated_data.get('name', instance.name)
        instance.make = validated_data.get('make', instance.make)
        instance.model = validated_data.get('model', instance.model)
        instance.type = validated_data.get('type', instance.type)
        instance.fuel_type = validated_data.get('fuel_type', instance.fuel_type)
        instance.mileage = validated_data.get('mileage', instance.mileage)

        instance.save()

        return instance
