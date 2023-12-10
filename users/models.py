from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    name = models.CharField(null=True, blank=True, max_length=100)
    is_admin = models.BooleanField(default=False)
    is_super_admin = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
