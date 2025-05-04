from django.contrib import admin
from .models import Vehicle, VehicleAdmin

# Register your models here.
admin.site.register(Vehicle, VehicleAdmin)
