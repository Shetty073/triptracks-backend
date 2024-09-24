from django.db import models
from django.contrib import admin

from triptracks.identity.models.user import AppUser

from triptracks.vehicle_service.models.vehicle import Vehicle


class TripVehicle(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    vehicle = models.ForeignKey(Vehicle, related_name="tripvehicles", null=True, on_delete=models.SET_NULL)
    fuel_cost_per_unit = models.DecimalField(blank=True, null=True, max_digits=11, decimal_places=2)
    calculated_fuel_cost = models.DecimalField(blank=True, null=True, max_digits=11, decimal_places=2)
    final_fuel_cost = models.DecimalField(blank=True, null=True, max_digits=11, decimal_places=2)
    final_fuel_adjustments = models.CharField(blank=True, null=True, max_length=250)
    driver = models.ForeignKey(AppUser, related_name="trips_as_driver", null=True, on_delete=models.SET_NULL)
    passengers = models.ManyToManyField(AppUser, related_name="trips_as_passenger")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TripVehicleAdmin(admin.ModelAdmin):
    list_display = ("id", "vehicle", "driver",)
    search_fields = ("origin_location", "destination_location",)
    list_filter = ("driver",)
    ordering = ("-created_at",)
