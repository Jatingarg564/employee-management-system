from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.accounts.models import AuthSession


class SessionJWTAuthentication(JWTAuthentication):
    """
    JWT authentication with server-side AuthSession validation.

    In addition to normal JWT validation, this verifies that the token
    belongs to an active server-side authentication session.
    """

    def authenticate(self, request):
        result = super().authenticate(request)

        if result is None:
            return None

        user, validated_token = result

        session_id = validated_token.get("session_id")

        if not session_id:
            raise AuthenticationFailed(
                "Token is not associated with an authentication session."
            )

        try:
            session = (
                AuthSession.objects
                .select_related("user")
                .get(
                    id=session_id,
                    user=user,
                    revoked_at__isnull=True,
                )
            )
        except AuthSession.DoesNotExist:
            raise AuthenticationFailed(
                "Authentication session is invalid or has been revoked."
            )

        if session.expires_at <= timezone.now():
            raise AuthenticationFailed(
                "Authentication session has expired."
            )

        if not user.is_active:
            raise AuthenticationFailed(
                "User account is inactive."
            )

        return user, validated_token