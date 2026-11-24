import os

from django.conf import settings
from django.core.files.storage import default_storage
from django.db import models

from .base import DriveBaseModel
from .folder import Folder


def drive_file_path(instance: "File", filename: str) -> str:
    return os.path.join("drive", str(instance.user_id), filename)


class File(DriveBaseModel):
    """An uploaded file, optionally placed inside a `Folder`."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="drive_files",
    )
    folder = models.ForeignKey(
        Folder,
        on_delete=models.CASCADE,
        related_name="files",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to=drive_file_path, storage=default_storage)
    size = models.PositiveBigIntegerField(default=0)
    content_type = models.CharField(max_length=255, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "folder", "name"],
                nulls_distinct=False,
                name="unique_file_name_per_folder",
            ),
        ]

    def __str__(self) -> str:
        return self.name
