from django.db import models
from event_topics.models import EventTopic

class EventSubTopic(models.Model):
    name = models.CharField(max_length=2147483647, null=True, blank=True)
    slug = models.CharField(max_length=2147483647, null=True, blank=True)
    event_topic = models.ForeignKey(EventTopic, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = (('slug', 'event_topic'),)