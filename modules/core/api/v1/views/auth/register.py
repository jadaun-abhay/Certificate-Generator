from django.contrib.auth import login
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.response import Response

from jadaun.views import BaseAPIView
from modules.core.api.v1.serializers.user import RegisterSerializer, UserSerializer
from modules.core.api.v1.services.user import UserService


class RegisterView(BaseAPIView):
    @extend_schema(
        tags=["core"],
        operation_id="core_auth_register",
        summary="Register a new account",
        description=(
            "Creates the user and logs them in immediately (same "
            "`sessionid` cookie behavior as POST /api/core/v1/auth/)."
        ),
        request=RegisterSerializer,
        responses={201: UserSerializer},
        examples=[
            OpenApiExample(
                "Request",
                value={
                    "email": "jane@example.com",
                    "password": "correct-horse-battery",
                    "first_name": "Jane",
                    "last_name": "Doe",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Minimal request (names optional)",
                value={"email": "jane@example.com", "password": "correct-horse-battery"},
                request_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = UserService.register(**serializer.validated_data)
        login(request, user)

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
