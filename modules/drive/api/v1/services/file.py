from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile

from modules.drive.models import File, Folder


class FileService:
    @staticmethod
    def upload(
        *, user_id: int, uploaded_file: UploadedFile, folder: Folder | None = None
    ) -> File:
        if folder is not None and folder.user_id != user_id:
            raise ValidationError("Folder does not belong to this user.")

        file = File(
            user_id=user_id,
            folder=folder,
            name=uploaded_file.name,
            file=uploaded_file,
            size=uploaded_file.size or 0,
            content_type=uploaded_file.content_type or "",
        )
        file.full_clean(exclude=["file"])
        file.save()
        return file

    @staticmethod
    def update(*, file: File, **fields) -> File:
        folder = fields.get("folder", file.folder)
        if folder is not None and folder.user_id != file.user_id:
            raise ValidationError("Folder does not belong to this user.")

        for field, value in fields.items():
            setattr(file, field, value)
        file.full_clean(exclude=["file"])
        file.save(update_fields=[*fields.keys(), "updated_at"])
        return file

    @staticmethod
    def trash(*, file: File) -> File:
        file.soft_delete()
        return file

    @staticmethod
    def restore(*, file: File) -> File:
        file.restore()
        return file

    @staticmethod
    def delete_permanently(*, file: File) -> None:
        file.file.delete(save=False)
        file.delete()
