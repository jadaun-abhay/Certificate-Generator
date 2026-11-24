from rest_framework import serializers

from modules.drive.models import Folder


class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = [
            "id",
            "name",
            "parent",
            "is_starred",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class FolderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ["name", "parent", "is_starred"]
        extra_kwargs = {
            "name": {"required": False},
            "parent": {"required": False},
            "is_starred": {"required": False},
        }
