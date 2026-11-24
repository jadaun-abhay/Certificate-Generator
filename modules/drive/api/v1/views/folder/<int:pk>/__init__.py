from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response

from jadaun.views import BaseAPIView
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

    def get(self, request, *args, **kwargs):
        folder = self.get_object()
        return Response(FolderSerializer(folder).data)

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

    def delete(self, request, *args, **kwargs):
        folder = self.get_object()
        FolderService.trash(folder=folder)
        return Response(status=status.HTTP_204_NO_CONTENT)
