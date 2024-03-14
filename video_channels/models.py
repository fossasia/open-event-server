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

class VideoStreams(models.Model):
    name = models.CharField(max_length=2147483647, null=True)
    url = models.CharField(max_length=2147483647, null=True)
    password = models.CharField(max_length=2147483647, null=True, blank=True)
    additional_information = models.CharField(max_length=2147483647, null=True, blank=True)
    extra = models.JSONField(null=True, blank=True)
    bg_img_url = models.CharField(max_length=2147483647, null=True, blank=True)
    is_chat_enabled = models.BooleanField(null=True, blank=True)
    is_global_event_room = models.BooleanField(null=True, blank=True)
    chat_room_id = models.CharField(max_length=2147483647, null=True, blank=True)
    event_id = models.ForeignKey('events.Event', on_delete=models.SET_NULL, null=True, blank=True)
    channel_id = models.ForeignKey(VideoChannel, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name
