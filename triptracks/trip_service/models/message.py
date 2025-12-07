from django.db import models
from django.contrib import admin

from triptracks.identity.models.user import AppUser
from triptracks.trip_service.models.trip import Trip


class Message(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    message = models.CharField(blank=False, null=False, max_length=2048)
    author = models.ForeignKey(AppUser, related_name="messages", null=True, on_delete=models.SET_NULL)
    trip = models.ForeignKey(Trip, related_name="messages", null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['author']),
            models.Index(fields=['message']),
            models.Index(fields=['trip']),
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at']),
        ]

class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "author", "trip")
    search_fields = ("message", "author", "trip")
    list_filter = ("author", "trip")
    ordering = ("-created_at",)
