from django.db import models

from modules.core.choices import StatusChoices


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.IntegerField(
        choices=StatusChoices.choices, default=StatusChoices.ACTIVE
    )

    class Meta:
        abstract = True


class Dropdown(BaseModel):
    label = models.CharField(max_length=255)
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
                fields=["label", "parent"], name="unique_dropdown_label_per_parent"
            ),
            models.CheckConstraint(
                condition=~models.Q(parent=models.F("id")),
                name="dropdown_parent_not_self",
            ),
        ]

    def __str__(self) -> str:
        return self.label
