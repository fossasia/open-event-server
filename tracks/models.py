from django.db import models
from events.models import Event

class Track(models.Model):
    name = models.CharField(max_length=2147483647)
    description = models.TextField(null=True, blank=True)
    color = models.CharField(max_length=2147483647)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)  # Assuming 'Event' model exists
    deleted_at = models.DateTimeField(null=True, blank=True)
    position = models.IntegerField(null=True, blank=True)