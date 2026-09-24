from drf_spectacular.utils import extend_schema

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.api.serializers import (
    AccountActivationSerializer,
    LoginSerializer,
    LogoutSerializer,
    TokenRefreshSerializer,
    TokenValidationSerializer,
)

from apps.accounts.services import (
    AccountService,
    AuthenticationService,
)


@method_decorator(csrf_exempt, name="dispatch")
class LoginAPIView(APIView):
    """
    API endpoint for user authentication.
    """

    permission_classes = []
    authentication_classes = []

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

        try:
            tokens = AuthenticationService.login(
                username=serializer.validated_data["username"],
                password=serializer.validated_data["password"],
            )
        except AuthenticationFailed as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(
            tokens,
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name="dispatch")
class ValidateActivationTokenAPIView(APIView):
    """
    API endpoint for validating an employee activation token.
    """

    permission_classes = []
    authentication_classes = []

    @extend_schema(
        tags=["Authentication"],
        summary="Validate Activation Token",
        description=(
            "Validate an employee account activation token "
            "before displaying the account activation form."
        ),
        request=TokenValidationSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "valid": {
                        "type": "boolean",
                    },
                    "detail": {
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
        Validate the activation token.
        """

        serializer = TokenValidationSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        AccountService.verify_token(
            serializer.validated_data["token"],
        )

        return Response(
            {
                "valid": True,
                "detail": "Activation token is valid.",
            },
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name="dispatch")
class AccountActivationAPIView(APIView):
    """
    API endpoint for employee account activation.
    """

    permission_classes = []
    authentication_classes = []

    @extend_schema(
        tags=["Authentication"],
        summary="Activate Employee Account",
        description=(
            "Activate an employee account using the "
            "verification token and establish a password."
        ),
        request=AccountActivationSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "detail": {
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
        Activate the employee account.
        """

        serializer = AccountActivationSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        AccountService.verify_account(
            token=serializer.validated_data["token"],
            password=serializer.validated_data["password"],
        )

        return Response(
            {
                "detail": "Account activated successfully.",
            },
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name="dispatch")
class TokenRefreshAPIView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            tokens = AuthenticationService.refresh(
                refresh_token=serializer.validated_data["refresh"]
            )
        except AuthenticationFailed as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(
            tokens,
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name="dispatch")
class LogoutAPIView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            AuthenticationService.logout(
                refresh_token=serializer.validated_data["refresh"]
            )
        except AuthenticationFailed as exc:
            return Response(
                {
                    "detail": str(exc),
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(
            {"detail": "Logged out successfully."},
            status=status.HTTP_200_OK,
        )