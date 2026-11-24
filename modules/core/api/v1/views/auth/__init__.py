from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.response import Response

from jadaun.views import BaseAPIView
from modules.core.api.v1.serializers.user import LoginSerializer, UserSerializer


class LoginView(BaseAPIView):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"is_authenticated": False, "user": None})
        return Response(
            {"is_authenticated": True, "user": UserSerializer(request.user).data}
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
