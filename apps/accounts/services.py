from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed

from rest_framework_simplejwt.tokens import RefreshToken


class AuthenticationService:
    """
    Handles authentication-related business logic.
    """

    @staticmethod
    def login(
        username,
        password,
    ):
        """
        Authenticate a user and generate JWT tokens.
        """

        user = authenticate(
            username=username,
            password=password,
        )

        if user is None:
            raise AuthenticationFailed(
                "Invalid username or password."
            )

        if not user.is_active:
            raise AuthenticationFailed(
                "This user account is inactive."
            )

        refresh = RefreshToken.for_user(
            user,
        )

        return {
            "access": str(
                refresh.access_token,
            ),
            "refresh": str(
                refresh,
            ),
        }