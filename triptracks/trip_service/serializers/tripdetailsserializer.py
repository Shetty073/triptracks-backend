from rest_framework import serializers
from triptracks.trip_service.models import Trip

class TripDetailsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Trip
        fields = [
            'id', 'origin_location', 'origin_lat', 'origin_long', 'destination_location', 'destination_lat',
            'destination_long', 'distance', 'distance_unit', 'vehicle', 'fuel_cost', 'accomodation_days',
            'final_accomodation_cost', 'food_cost_per_day', 'calculated_food_cost', 'final_food_cost', 'organizer', 
            'created_at', 'updated_at', 'travellers'
        ]
        read_only_fields = ['id', 'organizer', 'created_at', 'updated_at']

    def validate(self, data):
        if not data.get('origin_location') or not data.get('destination_location'):
            raise serializers.ValidationError("Origin and destination locations must be specified.")
        return data

    def create(self, validated_data):
        validated_data['organizer'] = self.context['request'].user
        trip = Trip.objects.create(**validated_data)
        return trip
    
    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance
