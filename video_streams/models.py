from django.db import models
from events.models import Event
from video_channels.models import VideoChannel

class VideoStream(models.Model):
    name = models.CharField(max_length=2147483647)
    url = models.CharField(max_length=2147483647)
    password = models.CharField(max_length=2147483647, null=True, blank=True)
    additional_information = models.CharField(max_length=2147483647, null=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True, unique=True)
    channel = models.ForeignKey(VideoChannel, on_delete=models.SET_NULL, null=True, blank=True)
    extra = models.JSONField(null=True, blank=True)
    bg_img_url = models.CharField(max_length=2147483647, null=True, blank=True)
    is_chat_enabled = models.BooleanField(null=True, blank=True)
    is_global_event_room = models.BooleanField(null=True, blank=True)
    chat_room_id = models.CharField(max_length=2147483647, null=True, blank=True)