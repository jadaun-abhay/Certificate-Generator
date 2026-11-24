from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response

from jadaun.views import BaseAPIView
from modules.handler.api.v1.selectors.job import JobSelector
from modules.handler.api.v1.serializers.job import (
    GenerationJobCreateSerializer,
    GenerationJobSerializer,
)
from modules.handler.api.v1.services.job import JobService


class JobListCreateView(BaseAPIView):
    def get(self, request, *args, **kwargs):
        jobs = JobSelector.list_for_user(request.user.id)
        return Response(GenerationJobSerializer(jobs, many=True).data)

    def post(self, request, *args, **kwargs):
        serializer = GenerationJobCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            job = JobService.create(user_id=request.user.id, **serializer.validated_data)
        except ValidationError as exc:
            self.fail(
                "; ".join(exc.messages), status_code=status.HTTP_400_BAD_REQUEST
            )

        JobService.enqueue(job=job)

        return Response(
            GenerationJobSerializer(job).data, status=status.HTTP_201_CREATED
        )
