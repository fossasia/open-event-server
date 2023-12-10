from rest_framework import serializers

from .models import CustomSysRole


class CustomSysRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomSysRole
        fields = ("id", "name")
