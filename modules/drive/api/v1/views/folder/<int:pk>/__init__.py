from django.core.exceptions import ValidationError
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.response import Response

from jadaun.views import BaseAPIView
from modules.core.api.v1.serializers.common import ErrorSerializer
from modules.drive.api.v1.serializers.folder import (
    FolderSerializer,
    FolderUpdateSerializer,
)
from modules.drive.api.v1.services.folder import FolderService
from modules.drive.models import Folder


class FolderDetailView(BaseAPIView):
    model = Folder

    def get_object(self) -> Folder:
        folder = super().get_object()
        if folder.user_id != self.request.user.id or folder.is_deleted:
            self.fail(
                "Folder not found.", status_code=status.HTTP_404_NOT_FOUND
            )
        return folder

    @extend_schema(
        tags=["drive"],
        operation_id="drive_folder_retrieve",
        summary="Get a folder",
        responses={200: FolderSerializer, 404: ErrorSerializer},
    )
    def get(self, request, *args, **kwargs):
        folder = self.get_object()
        return Response(FolderSerializer(folder).data)

    @extend_schema(
        tags=["drive"],
        operation_id="drive_folder_update",
        summary="Rename, move, or star a folder",
        description="Partial update - send only the fields you want to change.",
        request=FolderUpdateSerializer,
        responses={200: FolderSerializer, 400: ErrorSerializer, 404: ErrorSerializer},
        examples=[
            OpenApiExample("Rename", value={"name": "Archive"}, request_only=True),
            OpenApiExample("Move", value={"parent": 7}, request_only=True),
            OpenApiExample("Star", value={"is_starred": True}, request_only=True),
        ],
    )
    def patch(self, request, *args, **kwargs):
        folder = self.get_object()

        serializer = FolderUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            folder = FolderService.update(folder=folder, **serializer.validated_data)
        except ValidationError as exc:
            self.fail(
                "; ".join(exc.messages), status_code=status.HTTP_400_BAD_REQUEST
            )

        return Response(FolderSerializer(folder).data)

    @extend_schema(
        tags=["drive"],
        operation_id="drive_folder_trash",
        summary="Move a folder to trash",
        description="Soft-delete - restore it via PATCH /api/drive/v1/trash/folder/{id}/.",
        responses={204: None, 404: ErrorSerializer},
    )
    def delete(self, request, *args, **kwargs):
        folder = self.get_object()
        FolderService.trash(folder=folder)
        return Response(status=status.HTTP_204_NO_CONTENT)
