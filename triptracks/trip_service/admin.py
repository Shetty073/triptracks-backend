from django.contrib import admin
from .models import (
    Trip, TripAdmin, TripVehicle, TripVehicleAdmin, 
    Food, FoodAdmin, Accommodation, AccommodationAdmin, 
    Expense, ExpenseAdmin
)


# Register your models here.
admin.site.register(Trip, TripAdmin)
admin.site.register(TripVehicle, TripVehicleAdmin)
admin.site.register(Food, FoodAdmin)
admin.site.register(Accommodation, AccommodationAdmin)
admin.site.register(Expense, ExpenseAdmin)
