from django.db import models
from django.contrib import admin

from triptracks.identity.models.user import AppUser
from django.core.validators import MinValueValidator, MaxValueValidator

from triptracks.trip_service.models.tripvehicle import TripVehicle


class Trip(models.Model):
    LAT_VALIDATOR = [
        MinValueValidator(-90.0), 
        MaxValueValidator(90.0)
    ]
    
    LONG_VALIDATOR = [
        MinValueValidator(-100.0), 
        MaxValueValidator(100.0)
    ]

    DISTANCE_UNIT_TYPE_CHOICES = {
        "km": "Km",
        "mile": "Mile"
    }

    id = models.AutoField(auto_created=True, primary_key=True)
    origin_location = models.CharField(blank=False, null=False, max_length=100)
    origin_lat = models.FloatField(blank=True, null=True, default=0.0, validators=LAT_VALIDATOR)
    origin_long = models.FloatField(blank=True, null=True, default=0.0, validators=LONG_VALIDATOR)
    destination_location = models.CharField(blank=False, null=False, max_length=100)
    destination_lat = models.FloatField(blank=True, null=True, default=0.0, validators=LAT_VALIDATOR)
    destination_long = models.FloatField(blank=True, null=True, default=0.0, validators=LONG_VALIDATOR)
    distance = models.DecimalField(blank=False, null=False, max_digits=7, decimal_places=2)
    distance_unit = models.CharField(blank=False, null=False, choices=DISTANCE_UNIT_TYPE_CHOICES, max_length=12)
    average_distance_per_day = models.DecimalField(blank=False, null=False, max_digits=7, decimal_places=2)
    vehicles = models.ManyToManyField(TripVehicle, related_name="trips")
    accomodation_days = models.DecimalField(blank=True, null=True, max_digits=11, decimal_places=2)
    accomodation_cost_per_day = models.DecimalField(blank=True, null=True, max_digits=11, decimal_places=2)
    calculated_accomodation_cost = models.DecimalField(blank=True, null=True, max_digits=11, decimal_places=2)
    final_accomodation_cost = models.DecimalField(blank=True, null=True, max_digits=11, decimal_places=2)
    final_accomodation_adjustments = models.CharField(blank=True, null=True, max_length=250)
    food_cost_per_day = models.DecimalField(blank=True, null=True, max_digits=11, decimal_places=2)
    calculated_food_cost = models.DecimalField(blank=True, null=True, max_digits=11, decimal_places=2)
    final_food_cost = models.DecimalField(blank=True, null=True, max_digits=11, decimal_places=2)
    final_food_adjustments = models.CharField(blank=True, null=True, max_length=250)
    organizer = models.ForeignKey(AppUser, related_name="trips_organized", null=True, on_delete=models.SET_NULL)
    travellers = models.ManyToManyField(AppUser, related_name="trips_participated")
    updated_by = models.ForeignKey(AppUser, related_name="trips_updated", null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['origin_location']),
            models.Index(fields=['destination_location']),
            models.Index(fields=['organizer']),
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at']),
            models.Index(fields=['distance']),
            models.Index(fields=['distance_unit']),
        ]

class TripAdmin(admin.ModelAdmin):
    list_display = ("id", "origin_location", "destination_location", "distance", "organizer")
    search_fields = ("origin_location", "destination_location",)
    list_filter = ("organizer", "updated_by")
    ordering = ("-created_at",)
