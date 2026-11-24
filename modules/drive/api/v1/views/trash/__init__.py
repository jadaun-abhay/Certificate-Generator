from rest_framework.response import Response

from jadaun.views import BaseAPIView
from modules.drive.api.v1.selectors.trash import TrashSelector
from modules.drive.api.v1.serializers.file import FileSerializer
from modules.drive.api.v1.serializers.folder import FolderSerializer


class TrashListView(BaseAPIView):
    def get(self, request, *args, **kwargs):
        trashed = TrashSelector.list_for_user(request.user.id)
        return Response(
            {
                "folders": FolderSerializer(trashed["folders"], many=True).data,
                "files": FileSerializer(trashed["files"], many=True).data,
            }
        )
