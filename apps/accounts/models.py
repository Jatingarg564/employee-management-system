from django.contrib.auth.models import User
from django.db import models


class AccountVerification(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="account_verification",
    )
    token = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class AuthSession(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="auth_sessions",
    )
    refresh_token_jti = models.CharField(
        max_length=255,
        unique=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    last_used_at = models.DateTimeField(
        auto_now=True,
    )
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.user.username} - {self.refresh_token_jti}"