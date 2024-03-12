from django.db import models

from users.models import CustomUser


# Create your models here.
class Group(models.Model):
    deleted_at = models.DateTimeField(null=True, blank=True)
    name = models.CharField(max_length=255)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    social_links = models.JSONField(null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    banner_url = models.URLField(null=True, blank=True)
    logo_url = models.URLField(null=True, blank=True)
    follower_count = models.IntegerField(default=0)
    thumbnail_image_url = models.URLField(null=True, blank=True)
    is_promoted = models.BooleanField(default=False)
