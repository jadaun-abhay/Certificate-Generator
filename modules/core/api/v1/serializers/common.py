from rest_framework import serializers


class ErrorSerializer(serializers.Serializer):
    """Shape of every error body raised via `BaseAPIView.fail()` - used for
    schema documentation only, never instantiated by a view."""

    detail = serializers.CharField()
