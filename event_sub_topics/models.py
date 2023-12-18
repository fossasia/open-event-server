from django.db import models


class EventSubTopic(models.Model):
    name = models.CharField(max_length=200, null=True)
    slug = models.CharField(max_length=200, null=True)

    event_topic_id = models.ForeignKey(
        "event_topics.EventTopic",
        on_delete=models.CASCADE,
        null=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=["slug", "event_topic_id"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.slug}) - {self.event_topic_id}"
