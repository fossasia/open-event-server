from django.db import models
from events.models import Event
from video_streams.models import VideoStream

class Microlocation(models.Model):
    name = models.CharField(max_length=2147483647)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    floor = models.IntegerField(null=True, blank=True)
    room = models.CharField(max_length=2147483647, null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    video_stream = models.ForeignKey(VideoStream, on_delete=models.CASCADE, null=True, blank=True)
    position = models.IntegerField(default=0)
    hidden_in_scheduler = models.BooleanField(default=False)
    is_chat_enabled = models.BooleanField(null=True, blank=True)
    is_global_event_room = models.BooleanField(null=True, blank=True)
    chat_room_id = models.CharField(max_length=2147483647, null=True, blank=True)