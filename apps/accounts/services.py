from datetime import timedelta
import secrets
from rest_framework_simplejwt.exceptions import TokenError
from django.conf import settings
from django.contrib.auth import authenticate
from django.db import transaction
from django.utils import timezone

from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import AccountVerification, AuthSession


class AuthenticationService:
    """
    Handles authentication-related business logic.
    """

    @staticmethod
    @transaction.atomic
    def login(username, password):
        user = authenticate(username=username, password=password)

        if user is None:
            raise AuthenticationFailed("Invalid username or password.")

        if not user.is_active:
            raise AuthenticationFailed("This user account is inactive.")

        refresh = RefreshToken.for_user(user)

        employee = getattr(user, "employee_profile", None)

        if employee is not None:
            refresh["user_id"] = user.id
            refresh["employee_id"] = employee.id
            refresh["role"] = employee.role
            refresh["username"] = user.username
        else:
            refresh["user_id"] = user.id
            refresh["username"] = user.username

        AuthSession.objects.create(
            user=user,
            refresh_token_jti=refresh["jti"],
            expires_at=(
                timezone.now()
                + settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]
            ),
        )

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    @staticmethod
    @transaction.atomic
    def refresh(refresh_token):
        """
        Refresh authentication tokens using a server-managed AuthSession.

        The AuthSession represents the logical login session. Refresh-token
        rotation updates the JTI on the same AuthSession instead of creating
        a new session.
        """

        # Validate the refresh token and extract its current JTI.
        try:
            refresh = RefreshToken(refresh_token)
        except TokenError:
            raise AuthenticationFailed(
                "Refresh token is invalid, expired, or has been revoked."
            )

        old_jti = refresh["jti"]

        # Lock the session row so concurrent refresh requests cannot
        # rotate the same session at the same time.
        try:
            session = (
                AuthSession.objects
                .select_for_update()
                .select_related("user")
                .get(
                    refresh_token_jti=old_jti,
                    revoked_at__isnull=True,
                )
            )
        except AuthSession.DoesNotExist:
            raise AuthenticationFailed(
                "Authentication session is invalid or has been revoked."
            )

        now = timezone.now()

        # Check the server-side session expiry.
        if session.expires_at <= now:
            raise AuthenticationFailed(
                "Authentication session has expired."
            )

        # A deactivated account must not be able to refresh tokens.
        if not session.user.is_active:
            raise AuthenticationFailed(
                "This user account is inactive."
            )

        # Let SimpleJWT perform its standard refresh-token validation
        # and rotation:
        #
        # - validate the refresh token
        # - verify the user is active
        # - blacklist the old refresh token
        # - generate a new JTI
        # - update expiry and issued-at
        # - generate the access token
        serializer = TokenRefreshSerializer(
            data={
                "refresh": refresh_token,
            }
        )

        serializer.is_valid(raise_exception=True)

        tokens = serializer.validated_data

        # SimpleJWT has rotated the refresh token. Extract the new JTI.
        new_refresh = RefreshToken(tokens["refresh"])
        new_jti = new_refresh["jti"]

        # Update the SAME AuthSession rather than creating a new one.
        session.refresh_token_jti = new_jti
        session.last_used_at = now

        session.save(
            update_fields=[
                "refresh_token_jti",
                "last_used_at",
            ]
        )

        return tokens


class AccountService:
    """
    Handles employee account onboarding.
    """

    VERIFICATION_TOKEN_EXPIRY_HOURS = 24

    @classmethod
    def create_verification(cls, user):
        """
        Create or replace an account verification token.
        """

        token = secrets.token_urlsafe(32)

        created_at = timezone.now()

        expires_at = (
            created_at
            + timedelta(
                hours=cls.VERIFICATION_TOKEN_EXPIRY_HOURS,
            )
        )

        verification, _ = (
            AccountVerification.objects.update_or_create(
                user=user,
                defaults={
                    "token": token,
                    "expires_at": expires_at,
                    "is_verified": False,
                },
            )
        )

        return verification

    @staticmethod
    def verify_token(token):
        """
        Validate an account verification token.
        """

        try:
            verification = (
                AccountVerification.objects
                .select_related("user")
                .get(token=token)
            )
        except AccountVerification.DoesNotExist:
            raise ValidationError(
                {
                    "code": "INVALID_TOKEN",
                    "detail": "Invalid activation link.",
                }
            )

        if verification.is_verified:
            raise ValidationError(
                {
                    "code": "ALREADY_VERIFIED",
                    "detail": (
                        "This activation link has already been used."
                    ),
                }
            )

        if timezone.now() >= verification.expires_at:
            raise ValidationError(
                {
                    "code": "TOKEN_EXPIRED",
                    "detail": (
                        "This activation link has expired."
                    ),
                }
            )

        return verification

    @classmethod
    @transaction.atomic
    def verify_account(cls, token, password):
        """
        Verify the account and establish the user's password.
        """

        verification = cls.verify_token(token)

        user = verification.user

        user.set_password(password)
        user.is_active = True

        user.save(
            update_fields=[
                "password",
                "is_active",
            ]
        )

        verification.is_verified = True

        verification.save(
            update_fields=[
                "is_verified",
            ]
        )

        return user