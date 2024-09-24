from django.contrib import admin
from .models import Trip, TripAdmin, TripVehicle, TripVehicleAdmin

# Register your models here.
admin.site.register(Trip, TripAdmin)
admin.site.register(TripVehicle, TripVehicleAdmin)