from django.contrib import admin
from triptracks.identity.models import AppUser, AppUserAdmin

# Register your models here.
admin.site.register(AppUser, AppUserAdmin)
