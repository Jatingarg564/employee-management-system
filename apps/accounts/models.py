from django.contrib.auth.models import User
from django.db import models


class AccountVerification(models.Model):
    """
    Stores the account onboarding state for a user.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="account_verification",
    )

    token = models.CharField(
        max_length=255,
        unique=True,
    )

    expires_at = models.DateTimeField()

    is_verified = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.user.username