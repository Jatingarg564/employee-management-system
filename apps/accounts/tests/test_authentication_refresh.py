from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from apps.accounts.models import AuthSession

User = get_user_model()


class AuthenticationRefreshTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="employee",
            email="employee@test.com",
            password="StrongPassword@123",
            is_active=True,
        )

    def login(self):
        response = self.client.post(
            "/api/accounts/login/",
            {
                "username": "employee",
                "password": "StrongPassword@123",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        return response.data

    def test_valid_refresh_succeeds(self):
        tokens = self.login()

        response = self.client.post(
            "/api/accounts/token/refresh/",
            {
                "refresh": tokens["refresh"],
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_refresh_updates_same_auth_session(self):
        tokens = self.login()

        session = AuthSession.objects.get(
            user=self.user,
            revoked_at__isnull=True,
        )

        old_session_id = session.id
        old_jti = session.refresh_token_jti

        response = self.client.post(
            "/api/accounts/token/refresh/",
            {
                "refresh": tokens["refresh"],
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        session.refresh_from_db()

        assert session.id == old_session_id
        assert session.refresh_token_jti != old_jti

    def test_old_refresh_token_cannot_be_reused(self):
        tokens = self.login()

        first_refresh = self.client.post(
            "/api/accounts/token/refresh/",
            {
                "refresh": tokens["refresh"],
            },
            format="json",
        )

        assert first_refresh.status_code == status.HTTP_200_OK

        second_refresh = self.client.post(
            "/api/accounts/token/refresh/",
            {
                "refresh": tokens["refresh"],
            },
            format="json",
        )

        assert second_refresh.status_code == status.HTTP_401_UNAUTHORIZED

    def test_revoked_auth_session_cannot_refresh(self):
        tokens = self.login()

        session = AuthSession.objects.get(user=self.user)
        session.revoked_at = timezone.now()
        session.save(update_fields=["revoked_at"])

        response = self.client.post(
            "/api/accounts/token/refresh/",
            {
                "refresh": tokens["refresh"],
            },
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_expired_auth_session_cannot_refresh(self):
        tokens = self.login()

        session = AuthSession.objects.get(user=self.user)

        session.expires_at = timezone.now() - timedelta(minutes=1)
        session.save(update_fields=["expires_at"])

        response = self.client.post(
            "/api/accounts/token/refresh/",
            {
                "refresh": tokens["refresh"],
            },
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_multiple_sessions_are_independent(self):
        first_login = self.login()
        second_login = self.login()

        sessions = list(
            AuthSession.objects.filter(
                user=self.user,
                revoked_at__isnull=True,
            ).order_by("id")
        )

        assert len(sessions) == 2

        first_refresh = self.client.post(
            "/api/accounts/token/refresh/",
            {
                "refresh": first_login["refresh"],
            },
            format="json",
        )

        assert first_refresh.status_code == status.HTTP_200_OK

        sessions[0].refresh_from_db()
        sessions[1].refresh_from_db()

        assert sessions[0].refresh_token_jti != sessions[1].refresh_token_jti

    def test_expired_access_token_does_not_block_refresh_with_valid_refresh_token(self):
        tokens = self.login()

        session = AuthSession.objects.get(user=self.user)
        expired_access = AccessToken()
        expired_access["user_id"] = self.user.id
        expired_access["session_id"] = session.id
        expired_access["token_type"] = "access"
        expired_access["exp"] = timezone.now() - timedelta(minutes=5)

        response = self.client.post(
            "/api/accounts/token/refresh/",
            {
                "refresh": tokens["refresh"],
            },
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {expired_access}",
        )

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data