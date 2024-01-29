from django.db import models
from event_topics.models import EventTopic

class EventSubTopic(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    slug = models.CharField(max_length=200, null=True, blank=True)
    event_topic = models.ForeignKey(EventTopic, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = (('slug', 'event_topic'),)
        
    def __str__(self):
        return self.name