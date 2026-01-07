from rest_framework import serializers
from .models import EventMail


class EventMailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventMail
        fields = "__all__"
        read_only_fields = ("created_by", "created_at", "status")
