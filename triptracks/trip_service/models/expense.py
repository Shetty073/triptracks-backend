from django.db import models
from django.contrib import admin

from triptracks.identity.models.user import AppUser
from triptracks.trip_service.models.abstractcostitem import AbstractCostItem
from triptracks.trip_service.models.trip import Trip


class Expense(AbstractCostItem):
    id = models.AutoField(auto_created=True, primary_key=True)
    trip = models.ForeignKey(Trip, related_name="expenses", null=True, on_delete=models.SET_NULL)
    paid_by = models.ForeignKey(AppUser, related_name="expenses_paid",  null=True, on_delete=models.SET_NULL)
    created_by = models.ForeignKey(AppUser, related_name="expenses_created",  null=True, on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(AppUser, related_name="expenses_updated",  null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['trip']),
            models.Index(fields=['paid_by']),
            models.Index(fields=['created_by']),
            models.Index(fields=['updated_by']),
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at']),
        ]

class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "cost_per_unit", "no_of_units", "total_cost")
    search_fields = ("name",)
    list_filter = ("created_by", "trip")
    ordering = ("-created_at",)
