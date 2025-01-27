# filepath: accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name='profile')
    location = models.CharField(max_length=255, blank=True, null=True)
    tel = models.CharField(max_length=20, blank=True, null=True)

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('business', 'Business'),
    )

    email = models.EmailField(unique=True)
    type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')

    def __str__(self):
        return self.username
