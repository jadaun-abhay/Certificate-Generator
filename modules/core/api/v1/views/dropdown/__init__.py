from rest_framework import status
from rest_framework.response import Response

from jadaun.views import BaseAPIView
from modules.core.api.v1.selectors.dropdown import DropdownSelector
from modules.core.api.v1.serializers.dropdown import DropdownSerializer
from modules.core.api.v1.services.dropdown import DropdownService


class DropdownListCreateView(BaseAPIView):
    def get(self, request, *args, **kwargs):
        dropdowns = DropdownSelector.all()
        return Response(DropdownSerializer(dropdowns, many=True).data)

    def post(self, request, *args, **kwargs):
        serializer = DropdownSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dropdown = DropdownService.create(**serializer.validated_data)

        return Response(
            DropdownSerializer(dropdown).data, status=status.HTTP_201_CREATED
        )
