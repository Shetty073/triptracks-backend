import math
from datetime import datetime
from rest_framework import serializers
from triptracks.logger import logger
from triptracks.constants import TripConfigs
from triptracks.trip_service.models import Trip
from triptracks.common_utils import is_none_or_empty

class TripDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip

        fields = [
            'id', 'origin_location', 'origin_lat', 'origin_long', 'destination_location',
            'destination_lat', 'destination_long', 'distance', 'distance_unit', 
            'average_distance_per_day', 'vehicle', 'fuel_cost_per_unit', 'calculated_fuel_cost', 
            'final_fuel_cost', 'final_fuel_adjustments', 'accomodation_days', 'accomodation_cost_per_day', 
            'calculated_accomodation_cost', 'final_accomodation_cost', 'final_accomodation_adjustments', 
            'food_cost_per_day', 'calculated_food_cost', 'final_food_cost', 'final_food_adjustments', 
            'travellers', 'organizer', 'created_at', 'updated_by', 'updated_at'
        ]

        read_only_fields = [
            'id', 'calculated_fuel_cost', 'accomodation_days', 
            'calculated_accomodation_cost', 'calculated_food_cost', 
            'organizer', 'created_at', 'updated_by', 'updated_at'
        ]

    def validate(self, data):
        required_fields = [
            'origin_location', 'origin_lat', 'origin_long', 'destination_location', 'destination_lat',
            'destination_long', 'distance', 'distance_unit', 'vehicle', 'food_cost_per_day', 'travellers'
        ]

        missing_fields = [field for field in required_fields if is_none_or_empty(data.get(field))]

        if missing_fields:
            logger.error(f"Mandatory parameters should not be empty: {missing_fields} => payload: {data}")
            raise serializers.ValidationError(f"Mandatory parameters should not be empty: {', '.join(missing_fields)}")

        return data

    def calculate_trip_costs(self, validated_data, vehicle, instance=None):
        distance = validated_data.get('distance', instance.distance if instance else None)
        average_distance_per_day = validated_data.get('average_distance_per_day', instance.average_distance_per_day if instance else None)
        fuel_cost_per_unit = validated_data.get('fuel_cost_per_unit', instance.fuel_cost_per_unit if instance else None)
        accomodation_cost_per_day = validated_data.get('accomodation_cost_per_day', instance.accomodation_cost_per_day if instance else None)
        food_cost_per_day = validated_data.get('food_cost_per_day', instance.food_cost_per_day if instance else None)

        # Calculate fuel cost
        vehicle_mileage = vehicle.mileage
        validated_data['calculated_fuel_cost'] = (distance / vehicle_mileage) * fuel_cost_per_unit
        
        # Calculate accomodation days
        travel_days_fract = distance / average_distance_per_day
        fractional_part_percent = travel_days_fract % 1
        accomodation_distance_threshold = getattr(TripConfigs, 'ACCOMODATION_DISTANCE_THRESHOLD', 0.125)
        travel_days = math.ceil(travel_days_fract) if fractional_part_percent > accomodation_distance_threshold else math.floor(travel_days_fract)
        accomodation_days = travel_days - 1
        validated_data['accomodation_days'] = accomodation_days

        # Calculate accomodation cost
        validated_data['calculated_accomodation_cost'] = accomodation_days  * accomodation_cost_per_day

        # Calculate food cost
        validated_data['calculated_food_cost'] = travel_days * food_cost_per_day

    def create(self, validated_data):
        request = self.context['request']
        travellers = validated_data.pop('travellers', None)

        vehicle = validated_data.get('vehicle')
        
        if vehicle:
            self.calculate_trip_costs(validated_data, vehicle)

        validated_data['organizer'] = request.user
        validated_data['updated_by'] = request.user

        trip = Trip.objects.create(**validated_data)

        if travellers:
            trip.travellers.set(travellers)
        
        return trip
    
    def update(self, instance, validated_data):
        request = self.context['request']
        travellers = validated_data.pop('travellers', None)

        vehicle = validated_data.get('vehicle', instance.vehicle)
        
        # Recalculate fuel cost and accomodation days if distance / vehicle / fuel_cost_per_unit is updated
        if 'distance' in validated_data or 'fuel_cost_per_unit' in validated_data or vehicle != instance.vehicle:
            self.calculate_trip_costs(validated_data, vehicle, instance)

        validated_data['updated_by'] = request.user

        for field, value in validated_data.items():
            setattr(instance, field, value)

        if travellers:
            instance.travellers.set(travellers)

        instance.save()
        return instance
