from django.contrib.auth import authenticate, login
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.response import Response

from jadaun.views import BaseAPIView
from modules.core.api.v1.serializers.common import ErrorSerializer
from modules.core.api.v1.serializers.user import (
    AuthStatusSerializer,
    LoginSerializer,
    UserSerializer,
)


class LoginView(BaseAPIView):
    @extend_schema(
        tags=["core"],
        operation_id="core_auth_status",
        summary="Check login status",
        description="Whether the current session is authenticated, and if so, who as.",
        responses={200: AuthStatusSerializer},
        examples=[
            OpenApiExample(
                "Authenticated",
                value={
                    "is_authenticated": True,
                    "user": {
                        "id": 1,
                        "email": "jane@example.com",
                        "first_name": "Jane",
                        "last_name": "Doe",
                        "is_active": True,
                        "created_at": "2026-01-01T12:00:00Z",
                    },
                },
                response_only=True,
            ),
            OpenApiExample(
                "Not authenticated",
                value={"is_authenticated": False, "user": None},
                response_only=True,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"is_authenticated": False, "user": None})
        return Response(
            {"is_authenticated": True, "user": UserSerializer(request.user).data}
        )

    @extend_schema(
        tags=["core"],
        operation_id="core_auth_login",
        summary="Log in",
        description=(
            "Session-cookie login. On success, the response sets a "
            "`sessionid` cookie - send it back on every subsequent request."
        ),
        request=LoginSerializer,
        responses={200: UserSerializer, 401: ErrorSerializer},
        examples=[
            OpenApiExample(
                "Request",
                value={"email": "jane@example.com", "password": "correct-horse-battery"},
                request_only=True,
            ),
            OpenApiExample(
                "Invalid credentials",
                value={"detail": "Invalid email or password."},
                response_only=True,
                status_codes=["401"],
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            username=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        if user is None:
            self.fail(
                "Invalid email or password.", status_code=status.HTTP_401_UNAUTHORIZED
            )

        login(request, user)
        return Response(UserSerializer(user).data)
