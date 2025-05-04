from django.contrib import admin
from .models import (
    CrewRequest, CrewRequestAdmin, 
    CrewRelationship, CrewRelationshipAdmin
)


# Register your models here.
admin.site.register(CrewRequest, CrewRequestAdmin)
admin.site.register(CrewRelationship, CrewRelationshipAdmin)
