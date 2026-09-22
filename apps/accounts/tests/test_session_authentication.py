from datetime import date 
from django.utils import timezone
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import AuthSession
from apps.accounts.services import AuthenticationService
from apps.employees.choices import EmploymentRole, EmploymentType, EmployeeStatus
from apps.employees.models import Department, Designation, Employee


User = get_user_model()


class SessionJWTAuthenticationTest(APITestCase):
    """
    Tests server-side AuthSession validation for JWT authentication.
    """

    def setUp(self):
        self.designation = Designation.objects.create(
            name="Software Engineer",
        )

        self.department = Department.objects.create(
            name="Information Technology",
            code="IT",
        )

        self.user = User.objects.create_user(
            username="session_test_user",
            password="Test@12345",
            is_active=True,
        )

        self.employee = Employee.objects.create(
            user=self.user,
            employee_code="TESTSESSION001",
            first_name="Session",
            last_name="Test",
            email="session@test.com",
            phone_number="9000000099",
            date_of_birth=date(1995, 1, 1),
            date_of_joining=date.today(),
            department=self.department,
            designation=self.designation,
            role=EmploymentRole.EMPLOYEE,
            employment_type=EmploymentType.FULL_TIME,
            salary=Decimal("50000"),
            status=EmployeeStatus.ACTIVE,
        )

        self.login_url = "/api/accounts/login/"
        self.protected_url = "/api/employees/me/"

    def login(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "session_test_user",
                "password": "Test@12345",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        return response.data

    def test_valid_access_token_with_active_session_is_accepted(self):
        tokens = self.login()

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {tokens['access']}"
        )

        response = self.client.get(
            self.protected_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_revoked_session_rejects_existing_access_token(self):
        tokens = self.login()

        session = AuthSession.objects.get(
            user=self.user,
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {tokens['access']}"
        )

        response = self.client.get(
            self.protected_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        session.revoked_at = timezone.now()
        session.save(
            update_fields=["revoked_at"],
        )

        response = self.client.get(
            self.protected_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )