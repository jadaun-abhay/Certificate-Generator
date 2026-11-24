from rest_framework import status
from rest_framework.response import Response

from jadaun.views import BaseAPIView
from modules.drive.api.v1.serializers.file import FileSerializer
from modules.drive.api.v1.serializers.folder import FolderSerializer
from modules.drive.api.v1.services.trash import TrashService
from modules.drive.models import File


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

    def patch(self, request, *args, **kwargs):
        item = self.get_trashed_item()
        item = TrashService.restore(item=item)
        serializer_cls = FileSerializer if isinstance(item, File) else FolderSerializer
        return Response(serializer_cls(item).data)

    def delete(self, request, *args, **kwargs):
        item = self.get_trashed_item()
        TrashService.delete_permanently(item=item)
        return Response(status=status.HTTP_204_NO_CONTENT)
