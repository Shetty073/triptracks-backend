from django.contrib import admin
from .models import Trip, TripAdmin

# Register your models here.
admin.site.register(Trip, TripAdmin)