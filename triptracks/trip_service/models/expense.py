from django.db import models
from django.contrib import admin

from triptracks.identity.models.user import AppUser


class Expense(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(blank=False, null=False, max_length=100)
    cost_per_day = models.DecimalField(blank=True, null=True, max_digits=11, decimal_places=2)
    no_of_days = models.DecimalField(blank=True, null=True, max_digits=11, decimal_places=2)
    total_cost = models.DecimalField(blank=True, null=True, max_digits=11, decimal_places=2)
    paid_by = models.ForeignKey(AppUser, related_name="expenses_paid_by", null=True, on_delete=models.SET_NULL)
    created_by = models.ForeignKey(AppUser, related_name="expenses_added", null=True, on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(AppUser, related_name="expenses_updated", null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ExpenseAdmin(admin.ModelAdmin):
  list_display = ("id", "name", "cost_per_day", "no_of_days", "total_cost")
