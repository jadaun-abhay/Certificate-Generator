from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response

from jadaun.views import BaseAPIView
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

    def get(self, request, *args, **kwargs):
        file = self.get_object()
        return Response(FileSerializer(file).data)

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

    def delete(self, request, *args, **kwargs):
        file = self.get_object()
        FileService.trash(file=file)
        return Response(status=status.HTTP_204_NO_CONTENT)
