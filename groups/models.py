from django.db import models


class Group(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    social_links = models.JSONField(null=True)
    about = models.TextField(null=True)
    banner_url = models.URLField(null=True)
    logo_url = models.URLField(null=True)
    thumbnail_image_url = models.URLField(null=True)
    is_promoted = models.BooleanField(default=False)
    follower_count = models.IntegerField(null=True, default=0)
    deleted_at = models.DateTimeField(null=True)

    user_id = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
    )

    def __str__(self):
        return f"{self.name} ({self.user_id})"
