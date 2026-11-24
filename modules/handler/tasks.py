from celery import shared_task
from django.conf import settings


@shared_task
def generate_certificates_task(job_id: int) -> None:
    from modules.handler.api.v1.services.job import JobService
    from modules.handler.models import GenerationJob

    job = GenerationJob.objects.get(id=job_id)
    JobService.run(job=job, default_font_path=settings.HANDLER_DEFAULT_FONT_PATH)
