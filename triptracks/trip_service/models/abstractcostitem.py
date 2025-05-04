from django.db import models

from triptracks.identity.models.user import AppUser

class AbstractCostItem(models.Model):
    UNIT_TYPE_CHOICES = {
        "item": "Item",
        "litre": "L",
        "kg": "Kg",
        "day": "Day",
        "night": "Night",
    }
        
    name = models.CharField(blank=False, null=False, max_length=100)
    cost_per_unit = models.DecimalField(blank=True, null=True, max_digits=11, decimal_places=2)
    unit_type = models.CharField(blank=False, null=False, choices=UNIT_TYPE_CHOICES, max_length=12)
    no_of_units = models.DecimalField(blank=True, null=True, max_digits=11, decimal_places=2)
    total_cost = models.DecimalField(blank=True, null=True, max_digits=11, decimal_places=2)

    @property
    def total_cost(self):
        return self.cost_per_unit * self.no_of_units if self.cost_per_unit and self.no_of_units else None
    
    class Meta:
        abstract = True
