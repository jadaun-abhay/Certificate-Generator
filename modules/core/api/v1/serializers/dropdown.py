from rest_framework import serializers

from modules.core.models import Dropdown


class DropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dropdown
        fields = ["id", "label", "parent", "status", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class DropdownUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dropdown
        fields = ["label", "parent", "status"]
        extra_kwargs = {
            "label": {"required": False},
            "parent": {"required": False},
            "status": {"required": False},
        }
