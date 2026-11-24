from django.conf import settings
from django.db import models

from modules.core.models import BaseModel


class Font(BaseModel):
    """A reusable .ttf/.otf uploaded by a user, used by `TemplateField`s.

    Kept handler-private (not a `drive.File`) - a font is a tool shared
    across templates/jobs, not a document the user browses in their drive.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="fonts",
    )
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="fonts/")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"], name="unique_font_name_per_user"
            ),
        ]

    def __str__(self) -> str:
        return self.name
