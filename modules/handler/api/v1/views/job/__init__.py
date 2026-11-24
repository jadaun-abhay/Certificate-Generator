from django.core.exceptions import ValidationError
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.response import Response

from jadaun.views import BaseAPIView
from modules.core.api.v1.serializers.common import ErrorSerializer
from modules.handler.api.v1.selectors.job import JobSelector
from modules.handler.api.v1.serializers.job import (
    GenerationJobCreateSerializer,
    GenerationJobSerializer,
)
from modules.handler.api.v1.services.job import JobService


class JobListCreateView(BaseAPIView):
    @extend_schema(
        tags=["handler"],
        operation_id="handler_job_list",
        summary="List your certificate-generation jobs",
        responses={200: GenerationJobSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        jobs = JobSelector.list_for_user(request.user.id)
        return Response(GenerationJobSerializer(jobs, many=True).data)

    @extend_schema(
        tags=["handler"],
        operation_id="handler_job_create",
        summary="Generate a batch of certificates",
        description=(
            "`data_file` must already be an uploaded `drive.File` id "
            "(csv/json/xlsx - one row per certificate, columns matching "
            "the template's field names). Dispatches to a Celery worker "
            "and returns immediately with `status: pending` - poll "
            "GET /api/handler/v1/job/{id}/ for completion. On success, "
            "the output zip is saved into a `Certificates/<purpose>/` "
            "folder in your drive."
        ),
        request=GenerationJobCreateSerializer,
        responses={201: GenerationJobSerializer, 400: ErrorSerializer},
        examples=[
            OpenApiExample(
                "Request",
                value={"template": 1, "data_file": 3, "purpose": "Python Bootcamp Batch 1"},
                request_only=True,
            ),
        ],
    )
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
