from rest_framework import serializers

from .models import EventMail


class EventMailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventMail
        fields = ("id", "event_id", "email", "role", "created_at")

