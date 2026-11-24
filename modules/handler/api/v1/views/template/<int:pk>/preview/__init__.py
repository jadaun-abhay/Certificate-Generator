from django.http import HttpResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status

from jadaun.views import BaseAPIView
from modules.core.api.v1.serializers.common import ErrorSerializer
from modules.handler.api.v1.serializers.template import PreviewSerializer
from modules.handler.api.v1.services.preview import PreviewService
from modules.handler.models import CertificateTemplate


class TemplatePreviewView(BaseAPIView):
    model = CertificateTemplate

    def get_object(self) -> CertificateTemplate:
        template = super().get_object()
        if template.user_id != self.request.user.id:
            self.fail("Template not found.", status_code=status.HTTP_404_NOT_FOUND)
        return template

    @extend_schema(
        tags=["handler"],
        operation_id="handler_template_preview",
        summary="Render one sample row (preview only, nothing saved)",
        description=(
            "`row` keys must match the template's `field_name`s. Returns a "
            "raw `image/png` body - not JSON. For eyeballing a template "
            "before committing to a full generation job."
        ),
        request=PreviewSerializer,
        responses={200: OpenApiTypes.BINARY, 400: ErrorSerializer, 404: ErrorSerializer},
        examples=[
            OpenApiExample(
                "Request",
                value={"row": {"name": "Alice Johnson", "course": "Python Bootcamp"}},
                request_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        template = self.get_object()

        serializer = PreviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        image_bytes = PreviewService.render(
            template=template, sample_row=serializer.validated_data["row"]
        )
        return HttpResponse(image_bytes, content_type="image/png")
