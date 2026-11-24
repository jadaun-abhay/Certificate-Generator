from rest_framework import status
from rest_framework.response import Response

from jadaun.views import BaseAPIView
from modules.handler.api.v1.serializers.job import GenerationJobSerializer
from modules.handler.models import GenerationJob


class JobDetailView(BaseAPIView):
    model = GenerationJob

    def get_object(self) -> GenerationJob:
        job = super().get_object()
        if job.user_id != self.request.user.id:
            self.fail("Job not found.", status_code=status.HTTP_404_NOT_FOUND)
        return job

    def get(self, request, *args, **kwargs):
        job = self.get_object()
        return Response(GenerationJobSerializer(job).data)
