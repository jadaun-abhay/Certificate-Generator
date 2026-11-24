from rest_framework import status
from rest_framework.response import Response

from jadaun.views import BaseAPIView
from modules.handler.api.v1.selectors.font import FontSelector
from modules.handler.api.v1.serializers.font import FontSerializer
from modules.handler.api.v1.services.font import FontService


class FontListCreateView(BaseAPIView):
    def get(self, request, *args, **kwargs):
        fonts = FontSelector.list_for_user(request.user.id)
        return Response(FontSerializer(fonts, many=True).data)

    def post(self, request, *args, **kwargs):
        serializer = FontSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        font = FontService.create(
            user_id=request.user.id,
            name=serializer.validated_data["name"],
            uploaded_file=serializer.validated_data["file"],
        )

        return Response(FontSerializer(font).data, status=status.HTTP_201_CREATED)
