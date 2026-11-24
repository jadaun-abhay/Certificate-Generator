from django.db import models


class StatusChoices(models.IntegerChoices):
    INACTIVE = 0
    ACTIVE = 1
    ARCHIVED = 2


class UploadTypeChoices(models.IntegerChoices):
    IMAGE = 1
    DOCUMENT = 2
    SPREADSHEET = 3
    OTHER = 4
