from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class AppUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is mandatory")
        
        email = self.normalize_email(email=email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    

    def create_super_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class AppUser(AbstractUser):
    email = models.EmailField(unique=True)

    # Additional fields here
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = AppUserManager()
