from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response

from jadaun.views import BaseAPIView
from modules.core.api.v1.serializers.common import ErrorSerializer
from modules.handler.api.v1.selectors.font import FontSelector
from modules.handler.api.v1.serializers.font import FontSerializer
from modules.handler.api.v1.services.font import FontService


class FontListCreateView(BaseAPIView):
    @extend_schema(
        tags=["handler"],
        operation_id="handler_font_list",
        summary="List your uploaded fonts",
        responses={200: FontSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        fonts = FontSelector.list_for_user(request.user.id)
        return Response(FontSerializer(fonts, many=True).data)

    @extend_schema(
        tags=["handler"],
        operation_id="handler_font_create",
        summary="Upload a font",
        description=(
            "multipart/form-data. The resulting font's id can be used as "
            "`TemplateField.font` when creating a template."
        ),
        request={"multipart/form-data": FontSerializer},
        responses={201: FontSerializer, 400: ErrorSerializer},
    )
    def post(self, request, *args, **kwargs):
        serializer = FontSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        font = FontService.create(
            user_id=request.user.id,
            name=serializer.validated_data["name"],
            uploaded_file=serializer.validated_data["file"],
        )

        return Response(FontSerializer(font).data, status=status.HTTP_201_CREATED)
