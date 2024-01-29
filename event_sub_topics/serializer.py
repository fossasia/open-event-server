from rest_framework import serializers

from .models import EventSubTopic

class EventSubTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventSubTopic
        fields = '__all__'
