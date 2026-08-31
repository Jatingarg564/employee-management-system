from datetime import timedelta
import secrets

from django.contrib.auth import authenticate
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed, ValidationError

from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import AccountVerification


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