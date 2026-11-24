from rest_framework import serializers

from modules.handler.models import Font


class FontSerializer(serializers.ModelSerializer):
    class Meta:
        model = Font
        fields = ["id", "name", "file", "created_at"]
        read_only_fields = ["id", "created_at"]
