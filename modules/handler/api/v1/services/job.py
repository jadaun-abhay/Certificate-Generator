import io
import uuid
from zipfile import ZipFile

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from PIL import Image

from modules.drive.models import File, Folder
from modules.handler.api.v1.services.data_file import parse_rows
from modules.handler.api.v1.services.rendering import render_fields
from modules.handler.choices import JobStatus
from modules.handler.models import CertificateTemplate, GenerationJob

CERTIFICATES_ROOT_FOLDER_NAME = "Certificates"


class JobService:
    @staticmethod
    def resolve_output_folder(*, user_id: int, purpose: str) -> Folder:
        root, _ = Folder.objects.get_or_create(
            user_id=user_id, parent=None, name=CERTIFICATES_ROOT_FOLDER_NAME
        )
        purpose_folder, _ = Folder.objects.get_or_create(
            user_id=user_id, parent=root, name=purpose
        )
        return purpose_folder

    @staticmethod
    def create(
        *,
        user_id: int,
        template: CertificateTemplate,
        data_file: File,
        purpose: str,
    ) -> GenerationJob:
        if template.user_id != user_id:
            raise ValidationError("Template does not belong to this user.")
        if data_file.user_id != user_id:
            raise ValidationError("Data file does not belong to this user.")

        output_folder = JobService.resolve_output_folder(
            user_id=user_id, purpose=purpose
        )

        job = GenerationJob(
            user_id=user_id,
            template=template,
            data_file=data_file,
            purpose=purpose,
            status=JobStatus.PENDING,
            output_folder=output_folder,
        )
        job.full_clean()
        job.save()
        return job

    @staticmethod
    def enqueue(*, job: GenerationJob) -> None:
        from modules.handler.tasks import generate_certificates_task

        generate_certificates_task.delay(job.id)

    @staticmethod
    def run(*, job: GenerationJob, default_font_path: str) -> GenerationJob:
        """Does the actual rendering work - called from the Celery task, not
        from the request/response cycle."""
        job.status = JobStatus.PROCESSING
        job.save(update_fields=["status", "updated_at"])

        try:
            rows = parse_rows(job.data_file)

            template_file = job.template.file
            template_file.file.open("rb")
            try:
                template_image = Image.open(template_file.file).convert("RGB")
            finally:
                template_file.file.close()

            fields = list(job.template.fields.all())

            zip_buffer = io.BytesIO()
            with ZipFile(zip_buffer, "w") as zip_file:
                for index, row in enumerate(rows, start=1):
                    rendered = render_fields(
                        template_image, fields, row, default_font_path
                    )
                    image_buffer = io.BytesIO()
                    rendered.save(image_buffer, format="JPEG")
                    zip_file.writestr(
                        f"certificate-{index}.jpeg", image_buffer.getvalue()
                    )

            zip_name = f"{job.purpose}-{uuid.uuid4().hex[:8]}.zip"
            output_zip = File.objects.create(
                user_id=job.user_id,
                folder=job.output_folder,
                name=zip_name,
                file=ContentFile(zip_buffer.getvalue(), name=zip_name),
                size=zip_buffer.getbuffer().nbytes,
                content_type="application/zip",
            )

            job.output_zip = output_zip
            job.status = JobStatus.COMPLETED
            job.save(update_fields=["output_zip", "status", "updated_at"])
        except Exception as exc:  # noqa: BLE001 - surfaced on the job, not raised
            job.status = JobStatus.FAILED
            job.error_message = str(exc)
            job.save(update_fields=["status", "error_message", "updated_at"])

        return job
