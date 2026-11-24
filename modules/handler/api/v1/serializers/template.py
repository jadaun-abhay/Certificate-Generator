from rest_framework import serializers

from modules.drive.models import File
from modules.handler.choices import Alignment
from modules.handler.models import CertificateTemplate, Font, TemplateField


class TemplateFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateField
        fields = [
            "id",
            "field_name",
            "top_left_x",
            "top_left_y",
            "bottom_right_x",
            "bottom_right_y",
            "alignment",
            "font",
            "text_color",
        ]
        read_only_fields = ["id"]


class TemplateFieldInputSerializer(serializers.Serializer):
    """Same shape as `TemplateFieldSerializer`, but standalone (not a
    `ModelSerializer`) so it doesn't require `template` - used only for the
    nested `fields` list on template creation, before the template exists."""

    field_name = serializers.CharField()
    top_left_x = serializers.IntegerField(min_value=0)
    top_left_y = serializers.IntegerField(min_value=0)
    bottom_right_x = serializers.IntegerField(min_value=0)
    bottom_right_y = serializers.IntegerField(min_value=0)
    alignment = serializers.ChoiceField(
        choices=Alignment.choices, default=Alignment.CENTER
    )
    font = serializers.PrimaryKeyRelatedField(
        queryset=Font.objects.all(),
        required=False,
        allow_null=True,
        default=None,
    )
    text_color = serializers.CharField(default="#000000")


class TemplateSerializer(serializers.ModelSerializer):
    fields_data = TemplateFieldSerializer(source="fields", many=True, read_only=True)

    class Meta:
        model = CertificateTemplate
        fields = ["id", "name", "file", "fields_data", "created_at"]
        read_only_fields = ["id", "created_at"]


class TemplateCreateSerializer(serializers.Serializer):
    name = serializers.CharField()
    file = serializers.PrimaryKeyRelatedField(queryset=File.objects.all())
    fields = TemplateFieldInputSerializer(many=True)


class PreviewSerializer(serializers.Serializer):
    row = serializers.DictField(child=serializers.CharField(allow_blank=True))
