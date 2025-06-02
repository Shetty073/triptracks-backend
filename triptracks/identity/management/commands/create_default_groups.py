from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from triptracks.identity.models.user import AppUser

class Command(BaseCommand):
    help = 'Creates default groups and assigns superusers and staff to the Staff group'

    def handle(self, *args, **kwargs):
        group_names = ['Staff', 'User']
        groups = {}

        # Create groups
        for name in group_names:
            group, created = Group.objects.get_or_create(name=name)
            groups[name] = group
            if created:
                self.stdout.write(self.style.SUCCESS(f"Group '{name}' created."))
            else:
                self.stdout.write(self.style.WARNING(f"Group '{name}' already exists."))

        # Assign superusers and staff to 'Staff' group
        staff_group = groups.get('Staff')
        if staff_group:
            staff_users = AppUser.objects.filter(is_active=True).filter(is_superuser=True) | AppUser.objects.filter(is_active=True).filter(is_staff=True)
            staff_users = staff_users.distinct()

            if staff_users.exists():
                for user in staff_users:
                    user.groups.add(staff_group)
                    self.stdout.write(self.style.SUCCESS(f"AppUser '{user.username}' added to 'Staff' group."))
            else:
                self.stdout.write(self.style.WARNING("No superusers or staff users found to assign to 'Staff' group."))
