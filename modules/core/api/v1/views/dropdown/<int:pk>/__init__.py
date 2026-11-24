from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.response import Response

from jadaun.views import BaseAPIView
from modules.core.api.v1.serializers.common import ErrorSerializer
from modules.core.api.v1.serializers.dropdown import (
    DropdownSerializer,
    DropdownUpdateSerializer,
)
from modules.core.api.v1.services.dropdown import DropdownService
from modules.core.models import Dropdown


class DropdownDetailView(BaseAPIView):
    model = Dropdown  # used by `self.get_object()` (LookupFieldMixin)

    @extend_schema(
        tags=["core"],
        operation_id="core_dropdown_retrieve",
        summary="Get a dropdown entry",
        responses={200: DropdownSerializer, 404: ErrorSerializer},
    )
    def get(self, request, *args, **kwargs):
        dropdown = self.get_object()
        return Response(DropdownSerializer(dropdown).data)

    @extend_schema(
        tags=["core"],
        operation_id="core_dropdown_update",
        summary="Update a dropdown entry",
        description="Partial update - send only the fields you want to change.",
        request=DropdownUpdateSerializer,
        responses={200: DropdownSerializer, 404: ErrorSerializer},
        examples=[
            OpenApiExample("Rename", value={"label": "New label"}, request_only=True),
            OpenApiExample("Reparent", value={"parent": 3}, request_only=True),
        ],
    )
    def patch(self, request, *args, **kwargs):
        dropdown = self.get_object()

        serializer = DropdownUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        dropdown = DropdownService.update(dropdown=dropdown, **serializer.validated_data)

        return Response(DropdownSerializer(dropdown).data)
