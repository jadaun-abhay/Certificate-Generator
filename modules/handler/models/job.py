from django.conf import settings
from django.db import models

from modules.core.models import BaseModel
from modules.drive.models import File, Folder
from modules.handler.choices import JobStatus

from .template import CertificateTemplate


class GenerationJob(BaseModel):
    """A batch certificate-generation run.

    `purpose` names the drive folder (under a top-level "Certificates"
    folder) the finished zip gets saved into - see
    `modules.handler.api.v1.services.job.JobService` for how that folder is
    resolved/created.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="generation_jobs",
    )
    template = models.ForeignKey(
        CertificateTemplate, on_delete=models.CASCADE, related_name="jobs"
    )
    data_file = models.ForeignKey(File, on_delete=models.CASCADE, related_name="+")
    purpose = models.CharField(max_length=255)
    status = models.IntegerField(
        choices=JobStatus.choices, default=JobStatus.PENDING
    )
    output_folder = models.ForeignKey(
        Folder, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    output_zip = models.ForeignKey(
        File, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    error_message = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.template.name} -> {self.purpose} ({self.get_status_display()})"
