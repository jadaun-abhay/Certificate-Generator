from rest_framework import serializers

from modules.drive.models import File
from modules.handler.models import CertificateTemplate, GenerationJob


class GenerationJobSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = GenerationJob
        fields = [
            "id",
            "template",
            "data_file",
            "purpose",
            "status",
            "status_display",
            "output_folder",
            "output_zip",
            "error_message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "status_display",
            "output_folder",
            "output_zip",
            "error_message",
            "created_at",
            "updated_at",
        ]


class GenerationJobCreateSerializer(serializers.Serializer):
    template = serializers.PrimaryKeyRelatedField(
        queryset=CertificateTemplate.objects.all()
    )
    data_file = serializers.PrimaryKeyRelatedField(queryset=File.objects.all())
    purpose = serializers.CharField(max_length=255)
