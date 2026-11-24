from django.db import models


class JobStatus(models.IntegerChoices):
    PENDING = 1
    PROCESSING = 2
    COMPLETED = 3
    FAILED = 4


class Alignment(models.TextChoices):
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"
