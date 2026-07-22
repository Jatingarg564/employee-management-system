from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient

from apps.employees.models import (
    Department,
    Designation,
    Employee,
)

from apps.employees.choices import (
    EmploymentRole,
    EmploymentType,
    EmployeeStatus,
)

User = get_user_model()


class EmployeeBaseAPITestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):

        cls.client = APIClient()

        cls.user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="Admin@123"
        )

        cls.department = Department.objects.create(
            name="Information Technology",
            code="IT"
        )

        cls.designation = Designation.objects.create(
            name="Software Engineer"
        )

        cls.manager_user = User.objects.create_user(
            username="manager",
            email="manager@test.com",
            password="Admin@123"
        )

        cls.manager = Employee.objects.create(
            user=cls.manager_user,
            employee_code="EMIT20260001",
            first_name="John",
            last_name="Manager",
            email="manager@test.com",
            phone_number="9999999999",
            date_of_birth=date(1995, 1, 1),
            date_of_joining=date.today(),
            department=cls.department,
            designation=cls.designation,
            role=EmploymentRole.EMPLOYEE,
            employment_type=EmploymentType.FULL_TIME,
            salary=Decimal("70000"),
            status=EmployeeStatus.ACTIVE,
        )

        cls.employee_user = User.objects.create_user(
            username="employee",
            email="employee@test.com",
            password="Admin@123"
        )

        cls.employee = Employee.objects.create(
            user=cls.employee_user,
            employee_code="EMIT20260002",
            first_name="Alice",
            last_name="Smith",
            email="employee@test.com",
            phone_number="8888888888",
            date_of_birth=date(1998, 5, 15),
            date_of_joining=date.today(),
            department=cls.department,
            designation=cls.designation,
            reporting_to=cls.manager,
            role=EmploymentRole.EMPLOYEE,
            employment_type=EmploymentType.FULL_TIME,
            salary=Decimal("50000"),
            status=EmployeeStatus.ACTIVE,
        )

    def authenticate(self):
        """
        Override this if authentication changes.
        """
        self.client.force_authenticate(user=self.user)

    def employee_detail_url(self):
        return f"/api/employees/{self.employee.id}/"

    def employee_status_url(self):
        return f"/api/employees/{self.employee.id}/status/"

    def employee_list_url(self):
        return "/api/employees/"