from rest_framework import serializers
from .models import Ticket

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'name', 'description', 'price', 'quantity', 'is_active']
        read_only_fields = ['id', 'created_at', 'updated_at']