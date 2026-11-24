from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response

from jadaun.views import BaseAPIView
from modules.handler.api.v1.selectors.template import TemplateSelector
from modules.handler.api.v1.serializers.template import (
    TemplateCreateSerializer,
    TemplateSerializer,
)
from modules.handler.api.v1.services.template import TemplateService


class TemplateListCreateView(BaseAPIView):
    def get(self, request, *args, **kwargs):
        templates = TemplateSelector.list_for_user(request.user.id)
        return Response(TemplateSerializer(templates, many=True).data)

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
