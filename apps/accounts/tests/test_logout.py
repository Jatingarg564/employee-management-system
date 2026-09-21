from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import AuthSession

User = get_user_model()


class LogoutTest(APITestCase):

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

    def test_logout_succeeds(self):
        tokens = self.login()

        response = self.client.post(
            "/api/accounts/logout/",
            {
                "refresh": tokens["refresh"],
            },
            format="json",
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_logout_revokes_auth_session(self):
        tokens = self.login()

        session = AuthSession.objects.get(
            user=self.user,
            revoked_at__isnull=True,
        )

        response = self.client.post(
            "/api/accounts/logout/",
            {
                "refresh": tokens["refresh"],
            },
            format="json",
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        session.refresh_from_db()

        assert session.revoked_at is not None

    def test_refresh_fails_after_logout(self):
        tokens = self.login()

        logout_response = self.client.post(
            "/api/accounts/logout/",
            {
                "refresh": tokens["refresh"],
            },
            format="json",
        )

        assert logout_response.status_code == status.HTTP_204_NO_CONTENT

        refresh_response = self.client.post(
            "/api/accounts/token/refresh/",
            {
                "refresh": tokens["refresh"],
            },
            format="json",
        )

        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_only_revokes_current_session(self):
        first_login = self.login()
        second_login = self.login()

        sessions = list(
            AuthSession.objects.filter(
                user=self.user,
                revoked_at__isnull=True,
            ).order_by("id")
        )

        assert len(sessions) == 2

        logout_response = self.client.post(
            "/api/accounts/logout/",
            {
                "refresh": first_login["refresh"],
            },
            format="json",
        )

        assert logout_response.status_code == status.HTTP_204_NO_CONTENT

        sessions[0].refresh_from_db()
        sessions[1].refresh_from_db()

        assert sessions[0].revoked_at is not None
        assert sessions[1].revoked_at is None

        second_refresh = self.client.post(
            "/api/accounts/token/refresh/",
            {
                "refresh": second_login["refresh"],
            },
            format="json",
        )

        assert second_refresh.status_code == status.HTTP_200_OK

    def test_logout_with_invalid_refresh_token_fails(self):
        response = self.client.post(
            "/api/accounts/logout/",
            {
                "refresh": "invalid-refresh-token",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_already_revoked_session_fails(self):
        tokens = self.login()

        session = AuthSession.objects.get(
            user=self.user,
            revoked_at__isnull=True,
        )

        session.revoked_at = timezone.now()

        session.save(
            update_fields=[
                "revoked_at",
            ]
        )

        response = self.client.post(
            "/api/accounts/logout/",
            {
                "refresh": tokens["refresh"],
            },
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED