from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    PolymorphicProxySerializer,
    extend_schema,
)
from rest_framework import status
from rest_framework.response import Response

from jadaun.views import BaseAPIView
from modules.core.api.v1.serializers.common import ErrorSerializer
from modules.drive.api.v1.serializers.file import FileSerializer
from modules.drive.api.v1.serializers.folder import FolderSerializer
from modules.drive.api.v1.services.trash import TrashService
from modules.drive.models import File

_KIND_PARAM = OpenApiParameter(
    "kind",
    OpenApiTypes.STR,
    OpenApiParameter.PATH,
    enum=["folder", "file"],
    description="Which table `id` refers to.",
)
_TRASH_ITEM_RESPONSE = PolymorphicProxySerializer(
    component_name="TrashItem",
    serializers=[FolderSerializer, FileSerializer],
    resource_type_field_name=None,
)


class TrashItemView(BaseAPIView):
    def get_trashed_item(self):
        kind = self.kwargs.get("kind")
        if kind not in ("folder", "file"):
            self.fail(
                "kind must be 'folder' or 'file'.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        item = TrashService.get_trashed_item(
            self.request.user.id, kind, self.kwargs.get("pk")
        )
        if item is None:
            self.fail("Item not found in trash.", status_code=status.HTTP_404_NOT_FOUND)
        return item

    @extend_schema(
        tags=["drive"],
        operation_id="drive_trash_restore",
        summary="Restore a trashed folder or file",
        parameters=[_KIND_PARAM],
        responses={200: _TRASH_ITEM_RESPONSE, 404: ErrorSerializer},
    )
    def patch(self, request, *args, **kwargs):
        item = self.get_trashed_item()
        item = TrashService.restore(item=item)
        serializer_cls = FileSerializer if isinstance(item, File) else FolderSerializer
        return Response(serializer_cls(item).data)

    @extend_schema(
        tags=["drive"],
        operation_id="drive_trash_delete_permanently",
        summary="Permanently delete a trashed folder or file",
        description="Irreversible - unlike DELETE on the folder/file endpoints, this does not just move it to trash.",
        parameters=[_KIND_PARAM],
        responses={204: None, 404: ErrorSerializer},
    )
    def delete(self, request, *args, **kwargs):
        item = self.get_trashed_item()
        TrashService.delete_permanently(item=item)
        return Response(status=status.HTTP_204_NO_CONTENT)
