from django.db import models
from django.contrib import admin

from triptracks.identity.models.user import AppUser
from triptracks.trip_service.models.abstractcostitem import AbstractCostItem
from triptracks.trip_service.models.trip import Trip


class Food(AbstractCostItem):
    id = models.AutoField(auto_created=True, primary_key=True)
    trip = models.ForeignKey(Trip, related_name="foods", null=True, on_delete=models.SET_NULL)
    paid_by = models.ForeignKey(AppUser, related_name="foods_paid",  null=True, on_delete=models.SET_NULL)
    created_by = models.ForeignKey(AppUser, related_name="foods_created",  null=True, on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(AppUser, related_name="foods_updated",  null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class FoodAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "cost_per_unit", "no_of_units", "total_cost")
    search_fields = ("name",)
    list_filter = ("created_by", "trip")
    ordering = ("-created_at",)