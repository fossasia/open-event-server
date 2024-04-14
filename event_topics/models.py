from django.db import models


class EventTopic(models.Model):
    name = models.CharField(null=True, blank=True, max_length=200)
    slug = models.CharField(max_length=200)

    system_image_url = models.URLField(null=True, blank=True)

    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}"


class EventSubTopic(models.Model):
    name = models.CharField(max_length=200, null=True)
    slug = models.CharField(max_length=200, null=True)
    event_topic_id = models.ForeignKey(EventTopic, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.name}"
