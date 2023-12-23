from django.db import models
from users.models import CustomUser

class Group(models.Model):
    name = models.CharField(max_length=2147483647)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(null=True, blank=True)
    modified_at = models.DateTimeField(null=True, blank=True)
    social_links = models.JSONField(blank=True, null=True)
    about = models.TextField(null=True, blank=True)
    banner_url = models.CharField(max_length=2147483647, null=True, blank=True)
    logo_url = models.CharField(max_length=2147483647, null=True, blank=True)
    follower_count = models.IntegerField(default=0)
    thumbnail_image_url = models.CharField(max_length=2147483647, null=True, blank=True)
    is_promoted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)