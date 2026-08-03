from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
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
from apps.employees.services import EmployeeService


class EmployeeServiceTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.department = Department.objects.create(
            name="Information Technology",
            code="IT",
        )

        cls.department2 = Department.objects.create(
            name="Human Resource",
            code="HR",
        )

        cls.designation = Designation.objects.create(
            name="Software Engineer",
        )

        cls.user = User.objects.create_user(
            username="john",
            password="Admin@123",
            email="john@test.com",
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
    # Employee Sequence
    # ---------------------------------------------------------

    def test_get_employee_sequence(self):

        sequence = EmployeeService.get_employee_sequence(
            "EMIT20260015"
        )

        self.assertEqual(sequence, 15)

    def test_get_next_employee_sequence(self):

        sequence = EmployeeService.get_next_employee_sequence(
            EmploymentRole.EMPLOYEE,
            self.department,
        )

        self.assertEqual(sequence, 2)

    # ---------------------------------------------------------
    # Employee Code Generation
    # ---------------------------------------------------------

    def test_generate_employee_code(self):

        code = EmployeeService.generate_employee_code(
            role=EmploymentRole.EMPLOYEE,
            department=self.department,
            joining_year=2026,
            sequence=15,
        )

        self.assertEqual(
            code,
            "EMIT20260015",
        )

    def test_employee_code_contains_department_code(self):

        code = EmployeeService.generate_employee_code(
            role=EmploymentRole.MANAGER,
            department=self.department2,
            joining_year=2026,
            sequence=5,
        )

        self.assertTrue(code.startswith("MGHR"))

    # ---------------------------------------------------------
    # Employee Update
    # ---------------------------------------------------------

    def test_update_first_name(self):

        EmployeeService.update_employee(
            self.employee,
            {
                "first_name": "Peter",
            },
        )

        self.employee.refresh_from_db()

        self.assertEqual(
            self.employee.first_name,
            "Peter",
        )

    def test_update_salary(self):

        EmployeeService.update_employee(
            self.employee,
            {
                "salary": Decimal("80000"),
            },
        )

        self.employee.refresh_from_db()

        self.assertEqual(
            self.employee.salary,
            Decimal("80000"),
        )

    def test_update_department(self):

        EmployeeService.update_employee(
            self.employee,
            {
                "department": self.department2,
            },
        )

        self.employee.refresh_from_db()

        self.assertEqual(
            self.employee.department,
            self.department2,
        )

    def test_update_role(self):

        EmployeeService.update_employee(
            self.employee,
            {
                "role": EmploymentRole.MANAGER,
            },
        )

        self.employee.refresh_from_db()

        self.assertEqual(
            self.employee.role,
            EmploymentRole.MANAGER,
        )

    def test_department_change_regenerates_employee_code(self):

        old_code = self.employee.employee_code

        EmployeeService.update_employee(
            self.employee,
            {
                "department": self.department2,
            },
        )

        self.employee.refresh_from_db()

        self.assertNotEqual(
            old_code,
            self.employee.employee_code,
        )

    def test_role_change_regenerates_employee_code(self):

        old_code = self.employee.employee_code

        EmployeeService.update_employee(
            self.employee,
            {
                "role": EmploymentRole.MANAGER,
            },
        )

        self.employee.refresh_from_db()

        self.assertNotEqual(
            old_code,
            self.employee.employee_code,
        )

    # ---------------------------------------------------------
    # Employee Status
    # ---------------------------------------------------------

    def test_set_inactive(self):

        EmployeeService.update_employee_status(
            self.employee,
            {
                "status": EmployeeStatus.INACTIVE,
            },
        )

        self.employee.refresh_from_db()
        self.employee.user.refresh_from_db()

        self.assertEqual(
            self.employee.status,
            EmployeeStatus.INACTIVE,
        )

        self.assertFalse(
            self.employee.user.is_active,
        )

    def test_set_on_leave(self):

        EmployeeService.update_employee_status(
            self.employee,
            {
                "status": EmployeeStatus.ON_LEAVE,
            },
        )

        self.employee.refresh_from_db()

        self.assertEqual(
            self.employee.status,
            EmployeeStatus.ON_LEAVE,
        )

    def test_set_resigned(self):

        EmployeeService.update_employee_status(
            self.employee,
            {
                "status": EmployeeStatus.RESIGNED,
            },
        )

        self.employee.refresh_from_db()
        self.employee.user.refresh_from_db()

        self.assertFalse(
            self.employee.user.is_active,
        )

        self.assertIsNotNone(
            self.employee.resignation_date,
        )

    def test_set_terminated(self):

        EmployeeService.update_employee_status(
            self.employee,
            {
                "status": EmployeeStatus.TERMINATED,
            },
        )

        self.employee.refresh_from_db()
        self.employee.user.refresh_from_db()

        self.assertFalse(
            self.employee.user.is_active,
        )

        self.assertIsNotNone(
            self.employee.termination_date,
        )

    # ---------------------------------------------------------
    # Soft Delete
    # ---------------------------------------------------------

    def test_soft_delete_employee(self):

        EmployeeService.soft_delete_employee(
            self.employee,
        )

        self.employee.refresh_from_db()
        self.employee.user.refresh_from_db()

        self.assertEqual(
            self.employee.status,
            EmployeeStatus.INACTIVE,
        )

        self.assertFalse(
            self.employee.user.is_active,
        )

    def test_soft_delete_keeps_record(self):

        employee_id = self.employee.id

        EmployeeService.soft_delete_employee(
            self.employee,
        )

        self.assertTrue(
            Employee.objects.filter(
                id=employee_id
            ).exists()
        )

    # ---------------------------------------------------------
    # Department Transfer
    # ---------------------------------------------------------

    def test_transfer_department(self):

        employee = EmployeeService.transfer_employee(
            self.employee.id,
            self.department2,
        )

        employee.refresh_from_db()

        self.assertEqual(
            employee.department,
            self.department2,
        )

    def test_transfer_same_department_should_fail(self):

        with self.assertRaises(ValidationError):

            EmployeeService.transfer_employee(
                self.employee.id,
                self.department,
            )