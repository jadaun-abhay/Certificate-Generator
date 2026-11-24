from django.db.models import QuerySet

from modules.drive.models import Folder


class FolderSelector:
    @staticmethod
    def list_for_user(
        user_id: int, *, parent_id: int | None = None
    ) -> QuerySet[Folder]:
        return Folder.objects.filter(
            user_id=user_id, parent_id=parent_id, is_deleted=False
        )

    @staticmethod
    def get_by_id(user_id: int, folder_id: int) -> Folder | None:
        return Folder.objects.filter(
            user_id=user_id, id=folder_id, is_deleted=False
        ).first()

    @staticmethod
    def trashed_for_user(user_id: int) -> QuerySet[Folder]:
        return Folder.objects.filter(user_id=user_id, is_deleted=True)
