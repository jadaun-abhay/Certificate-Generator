from django.core.exceptions import ValidationError
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.response import Response

from jadaun.views import BaseAPIView
from modules.core.api.v1.serializers.common import ErrorSerializer
from modules.drive.api.v1.selectors.folder import FolderSelector
from modules.drive.api.v1.serializers.folder import FolderSerializer
from modules.drive.api.v1.services.folder import FolderService


class FolderListCreateView(BaseAPIView):
    @extend_schema(
        tags=["drive"],
        operation_id="drive_folder_list",
        summary="List folders",
        description="Omit `parent` to list root-level folders.",
        parameters=[
            OpenApiParameter(
                "parent",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                required=False,
                description="Parent folder id. Omit/blank for root-level folders.",
            ),
        ],
        responses={200: FolderSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        parent_id = request.query_params.get("parent")
        folders = FolderSelector.list_for_user(
            request.user.id, parent_id=parent_id
        )
        return Response(FolderSerializer(folders, many=True).data)

    @extend_schema(
        tags=["drive"],
        operation_id="drive_folder_create",
        summary="Create a folder",
        request=FolderSerializer,
        responses={201: FolderSerializer, 400: ErrorSerializer},
        examples=[
            OpenApiExample(
                "Root folder", value={"name": "Projects", "parent": None}, request_only=True
            ),
            OpenApiExample(
                "Nested folder", value={"name": "2026", "parent": 3}, request_only=True
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        serializer = FolderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            folder = FolderService.create(
                user_id=request.user.id, **serializer.validated_data
            )
        except ValidationError as exc:
            self.fail(
                "; ".join(exc.messages), status_code=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            FolderSerializer(folder).data, status=status.HTTP_201_CREATED
        )
