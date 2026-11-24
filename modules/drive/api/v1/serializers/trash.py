from rest_framework import serializers

from .file import FileSerializer
from .folder import FolderSerializer


class TrashListSerializer(serializers.Serializer):
    """Shape of `GET /api/drive/v1/trash/` - schema-only."""

    folders = FolderSerializer(many=True)
    files = FileSerializer(many=True)
