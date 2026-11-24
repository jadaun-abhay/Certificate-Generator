from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response

from jadaun.views import BaseAPIView
from modules.drive.api.v1.selectors.file import FileSelector
from modules.drive.api.v1.serializers.file import FileSerializer, FileUploadSerializer
from modules.drive.api.v1.services.file import FileService


class FileListCreateView(BaseAPIView):
    def get(self, request, *args, **kwargs):
        folder_id = request.query_params.get("folder")
        files = FileSelector.list_for_user(request.user.id, folder_id=folder_id)
        return Response(FileSerializer(files, many=True).data)

    def post(self, request, *args, **kwargs):
        serializer = FileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            file = FileService.upload(
                user_id=request.user.id,
                uploaded_file=serializer.validated_data["file"],
                folder=serializer.validated_data["folder"],
            )
        except ValidationError as exc:
            self.fail(
                "; ".join(exc.messages), status_code=status.HTTP_400_BAD_REQUEST
            )

        return Response(FileSerializer(file).data, status=status.HTTP_201_CREATED)
