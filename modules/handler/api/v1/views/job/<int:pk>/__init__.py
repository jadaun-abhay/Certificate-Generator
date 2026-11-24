from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response

from jadaun.views import BaseAPIView
from modules.core.api.v1.serializers.common import ErrorSerializer
from modules.handler.api.v1.serializers.job import GenerationJobSerializer
from modules.handler.models import GenerationJob


class JobDetailView(BaseAPIView):
    model = GenerationJob

    def get_object(self) -> GenerationJob:
        job = super().get_object()
        if job.user_id != self.request.user.id:
            self.fail("Job not found.", status_code=status.HTTP_404_NOT_FOUND)
        return job

    @extend_schema(
        tags=["handler"],
        operation_id="handler_job_retrieve",
        summary="Poll a generation job's status",
        description=(
            "`status`: pending -> processing -> completed/failed. Once "
            "`completed`, `output_zip` is the `drive.File` id of the "
            "result. If `failed`, `error_message` has why."
        ),
        responses={200: GenerationJobSerializer, 404: ErrorSerializer},
    )
    def get(self, request, *args, **kwargs):
        job = self.get_object()
        return Response(GenerationJobSerializer(job).data)
