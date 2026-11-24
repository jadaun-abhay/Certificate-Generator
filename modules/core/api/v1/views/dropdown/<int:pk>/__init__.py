from rest_framework.response import Response

from jadaun.views import BaseAPIView
from modules.core.api.v1.serializers.dropdown import (
    DropdownSerializer,
    DropdownUpdateSerializer,
)
from modules.core.api.v1.services.dropdown import DropdownService
from modules.core.models import Dropdown


class DropdownDetailView(BaseAPIView):
    model = Dropdown  # used by `self.get_object()` (LookupFieldMixin)

    def get(self, request, *args, **kwargs):
        dropdown = self.get_object()
        return Response(DropdownSerializer(dropdown).data)

    def patch(self, request, *args, **kwargs):
        dropdown = self.get_object()

        serializer = DropdownUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        dropdown = DropdownService.update(dropdown=dropdown, **serializer.validated_data)

        return Response(DropdownSerializer(dropdown).data)
