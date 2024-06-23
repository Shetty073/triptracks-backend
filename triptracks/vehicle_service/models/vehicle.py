from django.db import models
from django.contrib import admin

from triptracks.identity.models.user import AppUser

class Vehicle(models.Model):
    TYPE_CHOICES = {
        "motorcycle": "Motorcycle",
        "car": "Car"
    }

    FUEL_TYPE_CHOICES = {
        "petrol": "Petrol",
        "diesel": "Diesel",
        "cng": "CNG",
        "electric": "Electric"
    }

    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(blank=False, null=False, max_length=50)
    make = models.CharField(blank=False, null=False, max_length=50)
    model = models.CharField(blank=False, null=False, max_length=50)
    type = models.CharField(blank=False, null=False, choices=TYPE_CHOICES, max_length=12)
    fuel_type = models.CharField(blank=False, null=False, choices=FUEL_TYPE_CHOICES, max_length=10)
    mileage = models.DecimalField(blank=False, null=False, max_digits=4, decimal_places=2)
    owner = models.ForeignKey(AppUser, related_name="vehicles", on_delete=models.CASCADE)

class VehicleAdmin(admin.ModelAdmin):
  list_display = ("id", "name", "type", "fuel_type", "owner")
