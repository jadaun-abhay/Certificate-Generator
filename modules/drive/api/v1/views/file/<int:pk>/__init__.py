from django.core.exceptions import ValidationError
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.response import Response

from jadaun.views import BaseAPIView
from modules.core.api.v1.serializers.common import ErrorSerializer
from modules.drive.api.v1.serializers.file import FileSerializer, FileUpdateSerializer
from modules.drive.api.v1.services.file import FileService
from modules.drive.models import File


class FileDetailView(BaseAPIView):
    model = File

    def get_object(self) -> File:
        file = super().get_object()
        if file.user_id != self.request.user.id or file.is_deleted:
            self.fail("File not found.", status_code=status.HTTP_404_NOT_FOUND)
        return file

    @extend_schema(
        tags=["drive"],
        operation_id="drive_file_retrieve",
        summary="Get a file",
        responses={200: FileSerializer, 404: ErrorSerializer},
    )
    def get(self, request, *args, **kwargs):
        file = self.get_object()
        return Response(FileSerializer(file).data)

    @extend_schema(
        tags=["drive"],
        operation_id="drive_file_update",
        summary="Rename, move, or star a file",
        description="Partial update - send only the fields you want to change.",
        request=FileUpdateSerializer,
        responses={200: FileSerializer, 400: ErrorSerializer, 404: ErrorSerializer},
        examples=[
            OpenApiExample("Rename", value={"name": "report-final.pdf"}, request_only=True),
            OpenApiExample("Move", value={"folder": 7}, request_only=True),
            OpenApiExample("Star", value={"is_starred": True}, request_only=True),
        ],
    )
    def patch(self, request, *args, **kwargs):
        file = self.get_object()

        serializer = FileUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            file = FileService.update(file=file, **serializer.validated_data)
        except ValidationError as exc:
            self.fail(
                "; ".join(exc.messages), status_code=status.HTTP_400_BAD_REQUEST
            )

        return Response(FileSerializer(file).data)

    @extend_schema(
        tags=["drive"],
        operation_id="drive_file_trash",
        summary="Move a file to trash",
        description="Soft-delete - restore it via PATCH /api/drive/v1/trash/file/{id}/.",
        responses={204: None, 404: ErrorSerializer},
    )
    def delete(self, request, *args, **kwargs):
        file = self.get_object()
        FileService.trash(file=file)
        return Response(status=status.HTTP_204_NO_CONTENT)
