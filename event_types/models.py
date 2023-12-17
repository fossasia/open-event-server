from django.db import models


class EventType(models.Model):
    name = models.CharField(null=True, blank=True, max_length=200)
    slug = models.CharField(max_length=200)

    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.slug})"
