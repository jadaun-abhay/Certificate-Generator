from django.db import models
from django.utils import timezone

from modules.core.models import BaseModel


class DriveBaseModel(BaseModel):
    """Adds soft-delete (trash) and starring on top of the core `BaseModel`.

    Trash is modeled as a flag on the item itself rather than a separate
    `Trash` table - a trashed folder/file is just a row with `is_deleted`
    set, so listing "my files" and listing "trash" are both plain filters
    on the same tables instead of a second source of truth to keep in sync.
    """

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_starred = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def soft_delete(self) -> None:
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])

    def restore(self) -> None:
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])
