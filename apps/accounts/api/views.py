from drf_spectacular.utils import extend_schema

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.api.serializers import (
    LoginSerializer,
)
from apps.accounts.services import (
    AuthenticationService,
)


class LoginAPIView(APIView):
    """
    API endpoint for user authentication.
    """

    permission_classes = []

    @extend_schema(
        tags=["Authentication"],
        summary="User Login",
        description=(
            "Authenticate a user and return JWT "
            "access and refresh tokens."
        ),
        request=LoginSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "access": {
                        "type": "string",
                    },
                    "refresh": {
                        "type": "string",
                    },
                },
            },
        },
    )
    def post(
        self,
        request,
        *args,
        **kwargs,
    ):
        """
        Authenticate the user.
        """

        serializer = LoginSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        tokens = AuthenticationService.login(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )

        return Response(
            tokens,
            status=status.HTTP_200_OK,
        )