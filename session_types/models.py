from django.db import models
from events.models import Event

class SessionType(models.Model):
    name = models.CharField(max_length=2147483647)
    length = models.CharField(max_length=2147483647)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    position = models.IntegerField(null=True, blank=True)