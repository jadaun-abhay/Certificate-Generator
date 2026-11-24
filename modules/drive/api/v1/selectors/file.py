from django.db.models import QuerySet

from modules.drive.models import File


class FileSelector:
    @staticmethod
    def list_for_user(
        user_id: int, *, folder_id: int | None = None
    ) -> QuerySet[File]:
        return File.objects.filter(
            user_id=user_id, folder_id=folder_id, is_deleted=False
        )

    @staticmethod
    def get_by_id(user_id: int, file_id: int) -> File | None:
        return File.objects.filter(
            user_id=user_id, id=file_id, is_deleted=False
        ).first()

    @staticmethod
    def trashed_for_user(user_id: int) -> QuerySet[File]:
        return File.objects.filter(user_id=user_id, is_deleted=True)
