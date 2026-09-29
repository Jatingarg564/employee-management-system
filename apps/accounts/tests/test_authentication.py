from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import AuthSession
from apps.accounts.services import AccountService


User = get_user_model()


class AuthenticationSessionTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="employee",
            email="employee@test.com",
            password="StrongPassword@123",
            is_active=True,
        )

    def test_successful_login_creates_auth_session(self):
        response = self.client.post(
            "/api/accounts/login/",
            {
                "username": self.user.username,
                "password": "StrongPassword@123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            AuthSession.objects.filter(
                user=self.user,
                revoked_at__isnull=True,
            ).count(),
            1,
        )

    def test_auth_session_stores_refresh_token_jti(self):
        response = self.client.post(
            "/api/accounts/login/",
            {
                "username": self.user.username,
                "password": "StrongPassword@123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        session = AuthSession.objects.get(
            user=self.user,
        )

        self.assertTrue(
            session.refresh_token_jti,
        )

    def test_auth_session_has_expiry(self):
        response = self.client.post(
            "/api/accounts/login/",
            {
                "username": self.user.username,
                "password": "StrongPassword@123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        session = AuthSession.objects.get(
            user=self.user,
        )

        self.assertGreater(
            session.expires_at,
            timezone.now(),
        )

    def test_failed_login_does_not_create_auth_session(self):
        response = self.client.post(
            "/api/accounts/login/",
            {
                "username": self.user.username,
                "password": "WrongPassword@123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertEqual(
            AuthSession.objects.filter(
                user=self.user,
            ).count(),
            0,
        )

    def test_multiple_logins_create_multiple_sessions(self):
        first_response = self.client.post(
            "/api/accounts/login/",
            {
                "username": self.user.username,
                "password": "StrongPassword@123",
            },
            format="json",
        )

        second_response = self.client.post(
            "/api/accounts/login/",
            {
                "username": self.user.username,
                "password": "StrongPassword@123",
            },
            format="json",
        )

        self.assertEqual(
            first_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            AuthSession.objects.filter(
                user=self.user,
                revoked_at__isnull=True,
            ).count(),
            2,
        )
