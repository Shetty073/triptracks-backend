import math
from rest_framework import serializers
from triptracks.identity.models.user import AppUser
from triptracks.logger import logger
from triptracks.constants import TripConfigs
from triptracks.trip_service.models import Trip
from triptracks.common_utils import is_none_or_empty
from triptracks.trip_service.models.tripvehicle import TripVehicle
from triptracks.vehicle_service.models.vehicle import Vehicle

class TripVehicleSerializer(serializers.ModelSerializer):
    vehicle = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all())
    driver = serializers.PrimaryKeyRelatedField(queryset=AppUser.objects.all())
    passengers = serializers.PrimaryKeyRelatedField(queryset=AppUser.objects.all(), many=True)

    class Meta:
        model = TripVehicle
        fields = [
            'id', 'vehicle', 'driver', 'passengers', 'fuel_cost_per_unit', 'calculated_fuel_cost', 
            'final_fuel_cost', 'final_fuel_adjustments'
        ]

        read_only_fields = [
            'id', 'calculated_fuel_cost'
        ]

    def validate(self, data):
        required_fields = [
            'vehicle', 'driver', 'passengers', 'fuel_cost_per_unit'
        ]

        missing_fields = [field for field in required_fields if is_none_or_empty(data.get(field))]

        if missing_fields:
            logger.error(f"Mandatory parameters should not be empty: {missing_fields} => payload: {data}")
            raise serializers.ValidationError(f"Mandatory parameters should not be empty: {', '.join(missing_fields)}")

        vehicle = data.get('vehicle')
        if vehicle.mileage == 0:
            raise serializers.ValidationError("Vehicle mileage cannot be zero for fuel cost calculation")

        distance = self.context.get('trip_distance')
        if distance and distance <= 0:
            raise serializers.ValidationError("Trip distance is invalid.")

        return data

    def calculate_fuel_cost(self, validated_data, instance=None):
        distance = float(self.context.get('trip_distance'))

        fuel_cost_per_unit = float(validated_data.get('fuel_cost_per_unit'))
        vehicle_mileage = float(instance.mileage)

        validated_data['calculated_fuel_cost'] = (distance / vehicle_mileage) * fuel_cost_per_unit

    def create(self, validated_data):
        vehicle = validated_data.get('vehicle')
        passengers = validated_data.pop('passengers', None)
        self.calculate_fuel_cost(validated_data, vehicle)

        trip_vehicle = TripVehicle.objects.create(**validated_data)

        if passengers:
            trip_vehicle.passengers.set(passengers)
        
        return trip_vehicle

    def update(self, instance, validated_data):
        vehicle = validated_data.get('vehicle')
        passengers = validated_data.pop('passengers', None)
        self.calculate_fuel_cost(validated_data, vehicle)

        for field, value in validated_data.items():
            setattr(instance, field, value)
        
        instance.save()

        if passengers:
            instance.passengers.set(passengers)
        
        return instance


class TripDetailsSerializer(serializers.ModelSerializer):
    vehicles = TripVehicleSerializer(many=True)
    travellers = serializers.PrimaryKeyRelatedField(queryset=AppUser.objects.all(), many=True)

    class Meta:
        model = Trip

        fields = [
            'id', 'origin_location', 'origin_lat', 'origin_long', 'destination_location',
            'destination_lat', 'destination_long', 'distance', 'distance_unit', 
            'average_distance_per_day', 'vehicles', 'accomodation_days', 'accomodation_cost_per_day', 
            'calculated_accomodation_cost', 'final_accomodation_cost', 'final_accomodation_adjustments', 
            'food_cost_per_day', 'calculated_food_cost', 'final_food_cost', 'final_food_adjustments', 
            'travellers', 'organizer', 'created_at', 'updated_by', 'updated_at'
        ]

        read_only_fields = [
            'id', 'accomodation_days', 
            'calculated_accomodation_cost', 'calculated_food_cost', 
            'organizer', 'created_at', 'updated_by', 'updated_at'
        ]

    def validate(self, data):
        required_fields = [
            'origin_location', 'origin_lat', 'origin_long', 'destination_location', 'destination_lat',
            'destination_long', 'distance', 'distance_unit', 'vehicles', 'food_cost_per_day', 'travellers'
        ]

        missing_fields = [field for field in required_fields if is_none_or_empty(data.get(field))]

        if missing_fields:
            logger.error(f"Mandatory parameters should not be empty: {missing_fields} => payload: {data}")
            raise serializers.ValidationError(f"Mandatory parameters should not be empty: {', '.join(missing_fields)}")
        
        if data.get('distance', -1) <= 0:
            raise serializers.ValidationError("Distance must be a positive value")
        
        return data

    def calculate_trip_costs(self, validated_data, instance=None):
        # Get the distance
        distance = validated_data.get('distance', instance.distance if instance else None)
        average_distance_per_day = validated_data.get('average_distance_per_day', instance.average_distance_per_day if instance else None)
        accomodation_cost_per_day = validated_data.get('accomodation_cost_per_day', instance.accomodation_cost_per_day if instance else None)
        food_cost_per_day = validated_data.get('food_cost_per_day', instance.food_cost_per_day if instance else None)

        if distance is None or average_distance_per_day is None or accomodation_cost_per_day is None or food_cost_per_day is None:
            raise serializers.ValidationError("Missing required fields for cost calculation")

        # Calculate accommodation days
        travel_days_fract = distance / average_distance_per_day
        fractional_part_percent = travel_days_fract % 1
        accomodation_distance_threshold = getattr(TripConfigs, 'ACCOMODATION_DISTANCE_THRESHOLD', 0.125)
        travel_days = math.ceil(travel_days_fract) if fractional_part_percent > accomodation_distance_threshold else math.floor(travel_days_fract)
        accomodation_days = travel_days - 1
        validated_data['accomodation_days'] = accomodation_days

        # Calculate accomodation cost
        validated_data['calculated_accomodation_cost'] = accomodation_days * accomodation_cost_per_day

        # Calculate food cost
        validated_data['calculated_food_cost'] = travel_days * food_cost_per_day

    def create(self, validated_data):
        request = self.context['request']
        vehicles_data = validated_data.pop('vehicles')
        travellers = validated_data.pop('travellers', None)

        # Calculate global trip costs (accommodation, food)
        self.calculate_trip_costs(validated_data)

        validated_data['organizer'] = request.user
        validated_data['updated_by'] = request.user

        trip = Trip.objects.create(**validated_data)

        # Handle vehicles separately
        for vehicle_data in vehicles_data:
            vehicle_data['vehicle'] = vehicle_data.get('vehicle').id
            vehicle_data['driver'] = vehicle_data.get('driver').id
            vehicle_data['passengers'] = [p.id for p in vehicle_data.get('passengers')]

            vehicle_serializer = TripVehicleSerializer(data=vehicle_data, context={'trip_distance': trip.distance})
            if vehicle_serializer.is_valid(raise_exception=True):
                vehicle = vehicle_serializer.save()
                trip.vehicles.add(vehicle)

        # Set travellers if provided
        if travellers:
            trip.travellers.set(travellers)

        return trip

    def update(self, instance, validated_data):
        vehicles_data = validated_data.pop('vehicles', None)
        travellers = validated_data.pop('travellers', None)

        # Recalculate fuel cost and accomodation days if distance is changed
        if 'distance' in validated_data:
            self.calculate_trip_costs(validated_data, instance)

        validated_data['updated_by'] = self.context['request'].user

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()

        # Update vehicles
        instance.vehicles.all().delete()
        for vehicle_data in vehicles_data:
            vehicle_serializer = TripVehicleSerializer(data=vehicle_data, context={'trip_distance': instance.distance})
            if vehicle_serializer.is_valid(raise_exception=True):
                # Instead of updating we will always create fresh ones for this as we have cleared the existing one
                vehicle = vehicle_serializer.save()
                instance.vehicles.add(vehicle)

        # Update travellers
        if travellers:
            instance.travellers.set(travellers)

        return instance