from django.conf import settings
from django.db import models

from .base import DriveBaseModel


class Folder(DriveBaseModel):
    """A directory in a user's drive. `parent = None` means a root folder."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="drive_folders",
    )
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="children",
        null=True,
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "parent", "name"],
                # Postgres treats NULL as distinct from NULL by default, so
                # without this two root folders (`parent=None`) could still
                # share a name for the same user.
                nulls_distinct=False,
                name="unique_folder_name_per_parent",
            ),
            models.CheckConstraint(
                condition=~models.Q(parent=models.F("id")),
                name="folder_parent_not_self",
            ),
        ]

    def __str__(self) -> str:
        return self.name
