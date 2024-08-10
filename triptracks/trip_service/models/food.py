from django.db import models
from django.contrib import admin

from triptracks.identity.models.user import AppUser
from triptracks.trip_service.models.trip import Trip


class Food(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(blank=False, null=False, max_length=100)
    cost_per_unit = models.DecimalField(blank=True, null=True, max_digits=11, decimal_places=2)
    quantity = models.DecimalField(blank=True, null=True, max_digits=11, decimal_places=2)
    total_cost = models.DecimalField(blank=True, null=True, max_digits=11, decimal_places=2)
    trip = models.ForeignKey(Trip, related_name="foods", null=True, on_delete=models.SET_NULL)
    created_by = models.ForeignKey(AppUser, related_name="food_items_added", null=True, on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(AppUser, related_name="food_items_updated", null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class FoodAdmin(admin.ModelAdmin):
  list_display = ("id", "name", "cost_per_unit", "quantity", "total_cost")
