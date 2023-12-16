from django.db import models


class VideoChannel(models.Model):
    name = models.CharField(max_length=200)
    provider = models.CharField(max_length=200)
    url = models.URLField()
    api_url = models.URLField(null=True, blank=True)
    extra = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    api_key = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.name} {self.provider} {self.url} {self.api_url} {self.extra} {self.api_key}"
