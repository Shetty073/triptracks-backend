from string import ascii_lowercase, digits
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib import admin
from django.db import models
from shortuuid.django_fields import ShortUUIDField


class AppUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is mandatory")
        
        email = self.normalize_email(email=email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class AppUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = ShortUUIDField(
        length=16,
        max_length=40,
        prefix="id_",
        alphabet=f"{ascii_lowercase}{digits}"
    )

    # Additional fields here
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = AppUserManager()

class AppUserAdmin(admin.ModelAdmin):
  list_display = ("id", "first_name", "last_name", "email", "is_staff", "is_superuser")
