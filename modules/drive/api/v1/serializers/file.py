from rest_framework import serializers

from modules.drive.models import File, Folder


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = [
            "id",
            "name",
            "folder",
            "file",
            "size",
            "content_type",
            "is_starred",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "size",
            "content_type",
            "created_at",
            "updated_at",
        ]


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    folder = serializers.PrimaryKeyRelatedField(
        queryset=Folder.objects.all(),
        required=False,
        allow_null=True,
        default=None,
    )


class FileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ["name", "folder", "is_starred"]
        extra_kwargs = {
            "name": {"required": False},
            "folder": {"required": False},
            "is_starred": {"required": False},
        }
