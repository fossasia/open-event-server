from rest_framework import serializers

from .models import EventSubTopic


class EventSubTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventSubTopic
        fields = ("id", "name", "slug", "event_topic_id")
