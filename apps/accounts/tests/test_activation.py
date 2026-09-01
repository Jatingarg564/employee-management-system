from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import AccountVerification
from apps.accounts.services import AccountService


User = get_user_model()


class AccountActivationTest(APITestCase):

    @classmethod
    def setUpTestData(cls):

        cls.user = User.objects.create_user(
            username="employee",
            email="employee@test.com",
            first_name="Test",
            last_name="Employee",
        )

        cls.user.set_unusable_password()
        cls.user.is_active = False
        cls.user.save()

    def create_verification(self):

        return AccountService.create_verification(
            user=self.user,
        )

    # ---------------------------------------------------------
    # VERIFICATION CREATION
    # ---------------------------------------------------------

    def test_verification_record_is_created(self):

        verification = self.create_verification()

        self.assertIsNotNone(
            verification,
        )

        self.assertEqual(
            verification.user,
            self.user,
        )

        self.assertFalse(
            verification.is_verified,
        )

        self.assertTrue(
            verification.token,
        )

    def test_verification_token_has_expiry(self):

        verification = self.create_verification()

        self.assertGreater(
            verification.expires_at,
            timezone.now(),
        )

    def test_verification_token_is_secure_length(self):

        verification = self.create_verification()

        self.assertGreaterEqual(
            len(verification.token),
            32,
        )

    # ---------------------------------------------------------
    # INITIAL ACCOUNT STATE
    # ---------------------------------------------------------

    def test_new_account_is_inactive(self):

        self.assertFalse(
            self.user.is_active,
        )

    def test_new_account_has_no_usable_password(self):

        self.assertFalse(
            self.user.has_usable_password(),
        )

    # ---------------------------------------------------------
    # TOKEN VALIDATION
    # ---------------------------------------------------------

    def test_valid_token_can_be_retrieved(self):

        verification = self.create_verification()

        result = AccountService.verify_token(
            verification.token,
        )

        self.assertEqual(
            result.id,
            verification.id,
        )

    def test_invalid_token_should_fail(self):

        self.create_verification()

        with self.assertRaises(Exception):
            AccountService.verify_token(
                "invalid-token",
            )

    def test_expired_token_should_fail(self):

        verification = self.create_verification()

        verification.expires_at = (
            timezone.now() - timedelta(hours=1)
        )

        verification.save(
            update_fields=[
                "expires_at",
            ],
        )

        with self.assertRaises(Exception):
            AccountService.verify_token(
                verification.token,
            )

    # ---------------------------------------------------------
    # ACCOUNT ACTIVATION
    # ---------------------------------------------------------

    def test_account_activation(self):

        verification = self.create_verification()

        password = "StrongPassword@123"

        user = AccountService.verify_account(
            token=verification.token,
            password=password,
        )

        user.refresh_from_db()

        self.assertTrue(
            user.is_active,
        )

        self.assertTrue(
            user.has_usable_password(),
        )

        self.assertTrue(
            user.check_password(password),
        )

    def test_account_is_marked_verified(self):

        verification = self.create_verification()

        AccountService.verify_account(
            token=verification.token,
            password="StrongPassword@123",
        )

        verification.refresh_from_db()

        self.assertTrue(
            verification.is_verified,
        )

    def test_activated_account_cannot_reuse_token(self):

        verification = self.create_verification()

        AccountService.verify_account(
            token=verification.token,
            password="StrongPassword@123",
        )

        with self.assertRaises(Exception):
            AccountService.verify_token(
                verification.token,
            )

    # ---------------------------------------------------------
    # PASSWORD
    # ---------------------------------------------------------

    def test_activation_sets_correct_password(self):

        verification = self.create_verification()

        password = "StrongPassword@123"

        AccountService.verify_account(
            token=verification.token,
            password=password,
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(password),
        )

    # ---------------------------------------------------------
    # JWT LOGIN
    # ---------------------------------------------------------

    def test_inactive_account_cannot_login(self):

        verification = self.create_verification()

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
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_activated_account_can_login(self):

        verification = self.create_verification()

        password = "StrongPassword@123"

        AccountService.verify_account(
            token=verification.token,
            password=password,
        )

        response = self.client.post(
            "/api/accounts/login/",
            {
                "username": self.user.username,
                "password": password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "access",
            response.data,
        )

        self.assertIn(
            "refresh",
            response.data,
        )