from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response

from jadaun.views import BaseAPIView
from modules.drive.api.v1.selectors.folder import FolderSelector
from modules.drive.api.v1.serializers.folder import FolderSerializer
from modules.drive.api.v1.services.folder import FolderService


class FolderListCreateView(BaseAPIView):
    def get(self, request, *args, **kwargs):
        parent_id = request.query_params.get("parent")
        folders = FolderSelector.list_for_user(
            request.user.id, parent_id=parent_id
        )
        return Response(FolderSerializer(folders, many=True).data)

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
