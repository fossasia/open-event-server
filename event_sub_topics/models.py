from django.db import models

from event_topics.models import EventTopic


# Create your models here.
class EventSubTopic(models.Model):
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)
    event_type = models.ForeignKey(EventTopic, on_delete=models.SET_NULL, null=True, blank=True)
