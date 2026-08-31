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

    @staticmethod
    @transaction.atomic
    def create_verification(user):
        """
        Create or replace an account verification token.
        """

        token = secrets.token_urlsafe(32)

        expires_at = (
            timezone.now()
            + timedelta(
                hours=AccountService.VERIFICATION_TOKEN_EXPIRY_HOURS
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
                "Invalid verification token."
            )

        if verification.is_verified:
            raise ValidationError(
                "This account has already been verified."
            )

        if timezone.now() > verification.expires_at:
            raise ValidationError(
                "This verification token has expired."
            )

        return verification

    @staticmethod
    @transaction.atomic
    def verify_account(token, password):
        """
        Verify the account and establish the user's password.
        """

        verification = AccountService.verify_token(
            token
        )

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