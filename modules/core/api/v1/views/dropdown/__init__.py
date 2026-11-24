from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.response import Response

from jadaun.views import BaseAPIView
from modules.core.api.v1.selectors.dropdown import DropdownSelector
from modules.core.api.v1.serializers.dropdown import DropdownSerializer
from modules.core.api.v1.services.dropdown import DropdownService


class DropdownListCreateView(BaseAPIView):
    @extend_schema(
        tags=["core"],
        operation_id="core_dropdown_list",
        summary="List dropdown entries",
        description="All entries, flat - use `parent` to build the tree client-side.",
        responses={200: DropdownSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        dropdowns = DropdownSelector.all()
        return Response(DropdownSerializer(dropdowns, many=True).data)

    @extend_schema(
        tags=["core"],
        operation_id="core_dropdown_create",
        summary="Create a dropdown entry",
        request=DropdownSerializer,
        responses={201: DropdownSerializer},
        examples=[
            OpenApiExample(
                "Root entry",
                value={"label": "Country", "parent": None},
                request_only=True,
            ),
            OpenApiExample(
                "Child entry",
                value={"label": "India", "parent": 1},
                request_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        serializer = DropdownSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dropdown = DropdownService.create(**serializer.validated_data)

        return Response(
            DropdownSerializer(dropdown).data, status=status.HTTP_201_CREATED
        )
