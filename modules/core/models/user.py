import os

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.files.storage import default_storage
from django.db import models

from modules.core.choices import UploadTypeChoices

from .base import BaseModel


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(
        self, email: str, password: str | None, **extra_fields
    ) -> "User":
        if not email:
            raise ValueError("Users must have an email address.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self, email: str, password: str | None = None, **extra_fields
    ) -> "User":
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(
        self, email: str, password: str | None = None, **extra_fields
    ) -> "User":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    username = None
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # Overridden to give `groups`/`user_permissions` their own reverse
    # accessor - `PermissionsMixin`'s defaults clash with any other
    # installed `AbstractUser`/`PermissionsMixin` model.
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="core_user_set",
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="core_user_set",
        blank=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = UserManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["email"], name="unique_user_email"),
        ]

    def __str__(self) -> str:
        return self.email


def upload_file_path(instance: "UploadFile", filename: str) -> str:
    return os.path.join(
        "uploads",
        str(instance.user_id),
        instance.get_type_display().lower(),
        filename,
    )


class UploadFile(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="uploads",
    )
    type = models.IntegerField(choices=UploadTypeChoices.choices)
    file = models.FileField(upload_to=upload_file_path, storage=default_storage)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(type__in=UploadTypeChoices.values),
                name="upload_file_valid_type",
            ),
        ]

    def __str__(self) -> str:
        return self.file.name
