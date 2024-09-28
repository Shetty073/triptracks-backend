from triptracks.identity.models.user import AppUser
from django.db import models
from django.contrib import admin


class CrewRequest(models.Model):
    from_user = models.ForeignKey(AppUser, related_name='sent_crew_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(AppUser, related_name='received_crew_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('from_user', 'to_user')  # Ensure no duplicate requests

    def __str__(self):
        return f"{self.from_user.email} -> {self.to_user.email} (Accepted: {self.accepted})"

class CrewRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'from_user', 'to_user', 'created_at', 'accepted')
    search_fields = ('from_user__email', 'to_user__email')
    list_filter = ('accepted', 'created_at')
    ordering = ('-created_at',)


class CrewRelationship(models.Model):
    user1 = models.ForeignKey(AppUser, related_name='crew_relations1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(AppUser, related_name='crew_relations2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')  # Prevent duplicates and ensure mutual connection

    def __str__(self):
        return f"{self.user1.email} <-> {self.user2.email}"

class CrewRelationshipAdmin(admin.ModelAdmin):
    list_display = ('id', 'user1', 'user2', 'created_at')
    search_fields = ('user1__email', 'user2__email')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
