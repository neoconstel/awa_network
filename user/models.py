from django.db import models
from django.utils import timezone
import time
import random

from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
    )

	
class AccountManager(BaseUserManager):

    def create_user(self, email, username, first_name, 
                                            password, **other_fields):
        if not email:
            return ValueError('You must provide an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, username=username,
                first_name=first_name, **other_fields)
        user.set_password(password)
        user.save()
        return user

    
    def create_superuser(self, email, username, first_name, 
                                            password, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)
        other_fields.setdefault('is_verified', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError('Superuser must be assigned to is_staff=True')

        if other_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must be assigned to is_superuser=True')
        

        return self.create_user(email, username, first_name, 
                                            password, **other_fields)


# create the custom user model
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('email address', unique=True)
    username = models.CharField(
        max_length=150, unique=True, blank=True, null=False, default="")
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    date_registered = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    profile_image = models.ImageField(
        upload_to="profile_pics", null=False, default='default.ico')
    bio = models.CharField(
        max_length=500, null=False, default="nothing to see here")
    membership = models.CharField(max_length=20, null=False, default="Basic")

    USERNAME_FIELD = 'email'    
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    objects = AccountManager()

    def __str__(self) -> str:
        return self.username

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs) -> None:
        # give UNIQUE default username until user sets desired username.
        if not self.username:
            self.username = (
                f"user_{int(time.time()) + self.__class__.objects.count()}"
                f"{random.randint(1000,9999)}")            

        new_user = super().save(*args, **kwargs)      
        return new_user


class InvalidAccessToken(models.Model):
    token = models.CharField(max_length=1000)
    datetime = models.DateTimeField(default=timezone.now)
    