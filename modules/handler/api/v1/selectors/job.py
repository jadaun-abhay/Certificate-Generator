from django.db.models import QuerySet

from modules.handler.models import GenerationJob


class JobSelector:
    @staticmethod
    def list_for_user(user_id: int) -> QuerySet[GenerationJob]:
        return GenerationJob.objects.filter(user_id=user_id)

    @staticmethod
    def get_by_id(user_id: int, job_id: int) -> GenerationJob | None:
        return GenerationJob.objects.filter(user_id=user_id, id=job_id).first()
