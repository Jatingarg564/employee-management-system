from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase

from apps.employees.choices import (
    EmployeeStatus,
    EmploymentRole,
    EmploymentType,
)
from apps.employees.models import (
    Department,
    Designation,
    Employee,
)


class EmployeeModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.department = Department.objects.create(
            name="Information Technology",
            code="IT",
        )

        cls.designation = Designation.objects.create(
            name="Software Engineer",
        )

        cls.user = User.objects.create_user(
            username="john",
            email="john@test.com",
            password="Admin@123",
        )

        cls.employee = Employee.objects.create(
            user=cls.user,
            employee_code="EMIT20260001",
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            phone_number="9999999999",
            date_of_birth=date(1995, 1, 1),
            date_of_joining=date(2026, 1, 10),
            department=cls.department,
            designation=cls.designation,
            employment_type=EmploymentType.FULL_TIME,
            role=EmploymentRole.EMPLOYEE,
            salary=Decimal("50000"),
            status=EmployeeStatus.ACTIVE,
        )

    # ---------------------------------------------------------
    # __str__
    # ---------------------------------------------------------

    def test_department_str(self):

        self.assertEqual(
            str(self.department),
            self.department.name,
        )

    def test_designation_str(self):

        self.assertEqual(
            str(self.designation),
            self.designation.name,
        )

    def test_employee_str(self):

        self.assertEqual(
            str(self.employee),
            f"{self.employee.employee_code} - {self.employee.first_name} {self.employee.last_name}",
        )

    # ---------------------------------------------------------
    # Default Values
    # ---------------------------------------------------------

    def test_default_employee_status(self):

        user = User.objects.create_user(
            username="defaultstatus",
            email="default@test.com",
            password="Admin@123",
        )

        employee = Employee.objects.create(
            user=user,
            employee_code="EMIT20260002",
            first_name="Default",
            last_name="Employee",
            email="default@test.com",
            phone_number="8888888888",
            date_of_birth=date(1995, 5, 5),
            date_of_joining=date.today(),
            department=self.department,
            designation=self.designation,
            employment_type=EmploymentType.FULL_TIME,
            role=EmploymentRole.EMPLOYEE,
            salary=Decimal("30000"),
        )

        self.assertEqual(
            employee.status,
            EmployeeStatus.ACTIVE,
        )

    # ---------------------------------------------------------
    # Uniqueness
    # ---------------------------------------------------------

    def test_employee_code_unique(self):

        user = User.objects.create_user(
            username="duplicatecode",
            email="duplicate@test.com",
            password="Admin@123",
        )

        with self.assertRaises(IntegrityError):

            Employee.objects.create(
                user=user,
                employee_code="EMIT20260001",
                first_name="Test",
                last_name="User",
                email="duplicate@test.com",
                phone_number="7777777777",
                date_of_birth=date(1994, 1, 1),
                date_of_joining=date.today(),
                department=self.department,
                designation=self.designation,
                employment_type=EmploymentType.FULL_TIME,
                role=EmploymentRole.EMPLOYEE,
                salary=Decimal("30000"),
            )

    def test_email_unique(self):

        user = User.objects.create_user(
            username="duplicateemail",
            email="duplicate2@test.com",
            password="Admin@123",
        )

        with self.assertRaises(IntegrityError):

            Employee.objects.create(
                user=user,
                employee_code="EMIT20260003",
                first_name="Test",
                last_name="User",
                email="john@test.com",
                phone_number="6666666666",
                date_of_birth=date(1994, 1, 1),
                date_of_joining=date.today(),
                department=self.department,
                designation=self.designation,
                employment_type=EmploymentType.FULL_TIME,
                role=EmploymentRole.EMPLOYEE,
                salary=Decimal("30000"),
            )

    def test_phone_number_unique(self):

        user = User.objects.create_user(
            username="duplicatephone",
            email="phone@test.com",
            password="Admin@123",
        )

        with self.assertRaises(IntegrityError):

            Employee.objects.create(
                user=user,
                employee_code="EMIT20260004",
                first_name="Test",
                last_name="User",
                email="phone@test.com",
                phone_number="9999999999",
                date_of_birth=date(1994, 1, 1),
                date_of_joining=date.today(),
                department=self.department,
                designation=self.designation,
                employment_type=EmploymentType.FULL_TIME,
                role=EmploymentRole.EMPLOYEE,
                salary=Decimal("30000"),
            )

    # ---------------------------------------------------------
    # Foreign Keys
    # ---------------------------------------------------------

    def test_employee_department_relation(self):

        self.assertEqual(
            self.employee.department,
            self.department,
        )

    def test_employee_designation_relation(self):

        self.assertEqual(
            self.employee.designation,
            self.designation,
        )

    def test_employee_user_relation(self):

        self.assertEqual(
            self.employee.user,
            self.user,
        )

    # ---------------------------------------------------------
    # Timestamp Fields
    # ---------------------------------------------------------

    def test_created_at_exists(self):

        self.assertIsNotNone(
            self.employee.created_at,
        )

    def test_updated_at_exists(self):

        self.assertIsNotNone(
            self.employee.updated_at,
        )

    # ---------------------------------------------------------
    # Choice Fields
    # ---------------------------------------------------------

    def test_role_saved(self):

        self.assertEqual(
            self.employee.role,
            EmploymentRole.EMPLOYEE,
        )

    def test_employment_type_saved(self):

        self.assertEqual(
            self.employee.employment_type,
            EmploymentType.FULL_TIME,
        )

    def test_status_saved(self):

        self.assertEqual(
            self.employee.status,
            EmployeeStatus.ACTIVE,
        )