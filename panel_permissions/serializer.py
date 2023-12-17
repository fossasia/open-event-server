from rest_framework import serializers

from .models import PanelPermission


class PanelPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PanelPermission
        fields = ("id", "panel_name", "can_access")
