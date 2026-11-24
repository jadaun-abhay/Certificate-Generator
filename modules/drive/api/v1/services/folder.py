from django.core.exceptions import ValidationError

from modules.drive.models import Folder


class FolderService:
    @staticmethod
    def create(*, user_id: int, name: str, parent: Folder | None = None) -> Folder:
        if parent is not None and parent.user_id != user_id:
            raise ValidationError("Parent folder does not belong to this user.")
        folder = Folder(user_id=user_id, name=name, parent=parent)
        folder.full_clean()
        folder.save()
        return folder

    @staticmethod
    def update(*, folder: Folder, **fields) -> Folder:
        parent = fields.get("parent", folder.parent)
        if parent is not None and parent.user_id != folder.user_id:
            raise ValidationError("Parent folder does not belong to this user.")
        if parent is not None and parent.id == folder.id:
            raise ValidationError("A folder cannot be moved into itself.")

        for field, value in fields.items():
            setattr(folder, field, value)
        folder.full_clean()
        folder.save(update_fields=[*fields.keys(), "updated_at"])
        return folder

    @staticmethod
    def trash(*, folder: Folder) -> Folder:
        folder.soft_delete()
        return folder

    @staticmethod
    def restore(*, folder: Folder) -> Folder:
        folder.restore()
        return folder

    @staticmethod
    def delete_permanently(*, folder: Folder) -> None:
        folder.delete()
