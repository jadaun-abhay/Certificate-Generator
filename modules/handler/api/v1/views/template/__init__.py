from django.core.exceptions import ValidationError
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.response import Response

from jadaun.views import BaseAPIView
from modules.core.api.v1.serializers.common import ErrorSerializer
from modules.handler.api.v1.selectors.template import TemplateSelector
from modules.handler.api.v1.serializers.template import (
    TemplateCreateSerializer,
    TemplateSerializer,
)
from modules.handler.api.v1.services.template import TemplateService


class TemplateListCreateView(BaseAPIView):
    @extend_schema(
        tags=["handler"],
        operation_id="handler_template_list",
        summary="List your certificate templates",
        responses={200: TemplateSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        templates = TemplateSelector.list_for_user(request.user.id)
        return Response(TemplateSerializer(templates, many=True).data)

    @extend_schema(
        tags=["handler"],
        operation_id="handler_template_create",
        summary="Create a certificate template",
        description=(
            "`file` must already be an uploaded `drive.File` id (upload it "
            "via POST /api/drive/v1/file/ first). Box coordinates are pixels "
            "on that image, top-left origin."
        ),
        request=TemplateCreateSerializer,
        responses={201: TemplateSerializer, 400: ErrorSerializer},
        examples=[
            OpenApiExample(
                "Course completion template",
                value={
                    "name": "Course Completion",
                    "file": 2,
                    "fields": [
                        {
                            "field_name": "name",
                            "top_left_x": 100,
                            "top_left_y": 100,
                            "bottom_right_x": 700,
                            "bottom_right_y": 180,
                            "alignment": "center",
                            "text_color": "#000000",
                        },
                        {
                            "field_name": "course",
                            "top_left_x": 100,
                            "top_left_y": 220,
                            "bottom_right_x": 700,
                            "bottom_right_y": 280,
                            "alignment": "left",
                            "text_color": "#000000",
                        },
                    ],
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        serializer = TemplateCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            template = TemplateService.create(
                user_id=request.user.id, **serializer.validated_data
            )
        except ValidationError as exc:
            self.fail(
                "; ".join(exc.messages), status_code=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            TemplateSerializer(template).data, status=status.HTTP_201_CREATED
        )
