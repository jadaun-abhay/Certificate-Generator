from modules.drive.api.v1.services.file import FileService
from modules.drive.api.v1.services.folder import FolderService
from modules.drive.models import File, Folder


class TrashService:
    @staticmethod
    def get_trashed_item(user_id: int, kind: str, item_id: int) -> Folder | File | None:
        if kind == "folder":
            return Folder.objects.filter(
                user_id=user_id, id=item_id, is_deleted=True
            ).first()
        if kind == "file":
            return File.objects.filter(
                user_id=user_id, id=item_id, is_deleted=True
            ).first()
        return None

    @staticmethod
    def restore(*, item: Folder | File) -> Folder | File:
        if isinstance(item, Folder):
            return FolderService.restore(folder=item)
        return FileService.restore(file=item)

    @staticmethod
    def delete_permanently(*, item: Folder | File) -> None:
        if isinstance(item, Folder):
            FolderService.delete_permanently(folder=item)
        else:
            FileService.delete_permanently(file=item)
