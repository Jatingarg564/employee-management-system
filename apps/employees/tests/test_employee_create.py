from datetime import date, timedelta

from django.urls import reverse
from rest_framework import status

from apps.employees.models import Employee
from apps.employees.tests.base import EmployeeBaseAPITestCase


class EmployeeCreateAPITest(EmployeeBaseAPITestCase):

    def setUp(self):
        self.authenticate()

    def get_payload(self):
        return {
            "username": "newemployee",
            "password": "Admin@123",

            "first_name": "Peter",
            "last_name": "Parker",
            "email": "peter@test.com",
            "phone_number": "9876543210",

            "date_of_birth": "1998-01-01",
            "date_of_joining": str(date.today()),

            "department": self.department.id,
            "designation": self.designation.id,

            "employment_type": "FT",
            "role": "EM",

            "salary": "50000"
        }

    def test_create_employee_successfully(self):

        payload = self.get_payload()

        response = self.client.post(
            self.employee_list_url(),
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            Employee.objects.count(),
            3
        )

    def test_duplicate_email_should_fail(self):

        payload = self.get_payload()

        payload["email"] = self.employee.email

        response = self.client.post(
            self.employee_list_url(),
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_duplicate_username_should_fail(self):

        payload = self.get_payload()

        payload["username"] = self.employee.user.username

        response = self.client.post(
            self.employee_list_url(),
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_salary_zero_should_fail(self):

        payload = self.get_payload()

        payload["salary"] = 0

        response = self.client.post(
            self.employee_list_url(),
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_negative_salary_should_fail(self):

        payload = self.get_payload()

        payload["salary"] = -100

        response = self.client.post(
            self.employee_list_url(),
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_future_joining_date_should_fail(self):

        payload = self.get_payload()

        payload["date_of_joining"] = str(
            date.today() + timedelta(days=5)
        )

        response = self.client.post(
            self.employee_list_url(),
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_age_less_than_eighteen_should_fail(self):

        payload = self.get_payload()

        payload["date_of_birth"] = str(
            date.today() - timedelta(days=365 * 17)
        )

        response = self.client.post(
            self.employee_list_url(),
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_missing_required_field_should_fail(self):

        payload = self.get_payload()

        payload.pop("first_name")

        response = self.client.post(
            self.employee_list_url(),
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_employee_code_generated(self):

        payload = self.get_payload()

        response = self.client.post(
            self.employee_list_url(),
            payload,
            format="json"
        )

        employee = Employee.objects.get(
            email="peter@test.com"
        )

        self.assertTrue(
            employee.employee_code.startswith("EMIT")
        )

    def test_default_status_is_active(self):

        payload = self.get_payload()

        self.client.post(
            self.employee_list_url(),
            payload,
            format="json"
        )

        employee = Employee.objects.get(
            email="peter@test.com"
        )

        self.assertEqual(
            employee.status,
            "AC"
        )