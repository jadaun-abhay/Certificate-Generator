from django.conf import settings
from django.db import models

from modules.core.models import BaseModel
from modules.drive.models import File
from modules.handler.choices import Alignment


class CertificateTemplate(BaseModel):
    """A template image plus the field rectangles placed on it.

    `file` points at the already-uploaded `drive.File` for the template
    image, rather than owning its own `FileField` - uploads go through
    drive's own upload endpoint first, keeping "every file the user has"
    in one place.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="certificate_templates",
    )
    name = models.CharField(max_length=255)
    file = models.ForeignKey(
        File,
        on_delete=models.CASCADE,
        related_name="+",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"], name="unique_template_name_per_user"
            ),
        ]

    def __str__(self) -> str:
        return self.name


class TemplateField(BaseModel):
    """One rectangle on a template where a data column gets drawn."""

    template = models.ForeignKey(
        CertificateTemplate, on_delete=models.CASCADE, related_name="fields"
    )
    field_name = models.CharField(max_length=255)
    top_left_x = models.PositiveIntegerField()
    top_left_y = models.PositiveIntegerField()
    bottom_right_x = models.PositiveIntegerField()
    bottom_right_y = models.PositiveIntegerField()
    alignment = models.CharField(
        max_length=10, choices=Alignment.choices, default=Alignment.CENTER
    )
    font = models.ForeignKey(
        "handler.Font",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="template_fields",
    )
    text_color = models.CharField(max_length=7, default="#000000")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["template", "field_name"],
                name="unique_field_name_per_template",
            ),
            models.CheckConstraint(
                condition=models.Q(bottom_right_x__gt=models.F("top_left_x"))
                & models.Q(bottom_right_y__gt=models.F("top_left_y")),
                name="template_field_box_is_valid",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.template.name}:{self.field_name}"
