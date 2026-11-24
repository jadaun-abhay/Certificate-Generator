from rest_framework import status
from rest_framework.response import Response

from jadaun.views import BaseAPIView
from modules.handler.api.v1.serializers.template import TemplateSerializer
from modules.handler.models import CertificateTemplate


class TemplateDetailView(BaseAPIView):
    model = CertificateTemplate

    def get_object(self) -> CertificateTemplate:
        template = super().get_object()
        if template.user_id != self.request.user.id:
            self.fail("Template not found.", status_code=status.HTTP_404_NOT_FOUND)
        return template

    def get(self, request, *args, **kwargs):
        template = self.get_object()
        return Response(TemplateSerializer(template).data)
