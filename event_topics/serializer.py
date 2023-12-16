from rest_framework import serializers

from .models import EventTopic


class EventTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventTopic
        fields = ("id", "name", "slug", "system_image_url")
