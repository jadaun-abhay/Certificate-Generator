from django.contrib.auth import login
from rest_framework import status
from rest_framework.response import Response

from jadaun.views import BaseAPIView
from modules.core.api.v1.serializers.user import RegisterSerializer, UserSerializer
from modules.core.api.v1.services.user import UserService


class RegisterView(BaseAPIView):
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = UserService.register(**serializer.validated_data)
        login(request, user)

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
