from django.http import HttpResponse
from rest_framework import status

from jadaun.views import BaseAPIView
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

    def post(self, request, *args, **kwargs):
        template = self.get_object()

        serializer = PreviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        image_bytes = PreviewService.render(
            template=template, sample_row=serializer.validated_data["row"]
        )
        return HttpResponse(image_bytes, content_type="image/png")
