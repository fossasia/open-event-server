from django.db import models


class EventType(models.Model):
    name = models.CharField(max_length=2147483647)
    slug = models.CharField(max_length=2147483647, db_index=True, unique=True)
    deleted_at = models.DateTimeField(null=True, blank=True)