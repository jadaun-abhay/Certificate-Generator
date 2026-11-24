from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response

from jadaun.views import BaseAPIView
from modules.core.api.v1.serializers.common import ErrorSerializer
from modules.handler.api.v1.serializers.template import TemplateSerializer
from modules.handler.models import CertificateTemplate


class TemplateDetailView(BaseAPIView):
    model = CertificateTemplate

    def get_object(self) -> CertificateTemplate:
        template = super().get_object()
        if template.user_id != self.request.user.id:
            self.fail("Template not found.", status_code=status.HTTP_404_NOT_FOUND)
        return template

    @extend_schema(
        tags=["handler"],
        operation_id="handler_template_retrieve",
        summary="Get a certificate template",
        description="Includes its field rectangles under `fields_data`.",
        responses={200: TemplateSerializer, 404: ErrorSerializer},
    )
    def get(self, request, *args, **kwargs):
        template = self.get_object()
        return Response(TemplateSerializer(template).data)
