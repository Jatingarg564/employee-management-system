from decimal import Decimal

from rest_framework import status

from apps.employees.choices import (
    EmploymentRole,
    EmploymentType,
    EmployeeStatus,
)
from apps.employees.models import (
    Department,
    Designation,
)
from apps.employees.tests.base import EmployeeBaseAPITestCase


class EmployeeUpdateAPITest(EmployeeBaseAPITestCase):

    def setUp(self):
        self.authenticate()

        self.new_department = Department.objects.create(
            name="Human Resource",
            code="HR"
        )

        self.new_designation = Designation.objects.create(
            name="Senior Software Engineer"
        )

    def patch_employee(self, payload):
        return self.client.patch(
            self.employee_detail_url(),
            payload,
            format="json"
        )

    # ------------------------------------------------------------
    # Basic Field Updates
    # ------------------------------------------------------------

    def test_update_first_name(self):

        response = self.patch_employee({
            "first_name": "Peter"
        })

        self.employee.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.employee.first_name, "Peter")

    def test_update_last_name(self):

        response = self.patch_employee({
            "last_name": "Parker"
        })

        self.employee.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.employee.last_name, "Parker")

    def test_update_phone_number(self):

        response = self.patch_employee({
            "phone_number": "9876543210"
        })

        self.employee.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.employee.phone_number,
            "9876543210"
        )

    def test_update_address(self):

        response = self.patch_employee({
            "address": "New Delhi"
        })

        self.employee.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.employee.address,
            "New Delhi"
        )

    def test_update_salary(self):

        response = self.patch_employee({
            "salary": "85000"
        })

        self.employee.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.employee.salary,
            Decimal("85000")
        )

    def test_update_employment_type(self):

        response = self.patch_employee({
            "employment_type": EmploymentType.PART_TIME
        })

        self.employee.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.employee.employment_type,
            EmploymentType.PART_TIME
        )

    def test_update_designation(self):

        response = self.patch_employee({
            "designation": self.new_designation.id
        })

        self.employee.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.employee.designation,
            self.new_designation
        )

    # ------------------------------------------------------------
    # Department Update
    # ------------------------------------------------------------

    def test_change_department(self):

        response = self.patch_employee({
            "department": self.new_department.id
        })

        self.employee.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.employee.department,
            self.new_department
        )

    def test_department_change_regenerates_employee_code(self):

        old_code = self.employee.employee_code

        response = self.patch_employee({
            "department": self.new_department.id
        })

        self.employee.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertNotEqual(
            old_code,
            self.employee.employee_code
        )

        self.assertTrue(
            self.employee.employee_code.startswith(
                f"{self.employee.role}{self.new_department.code}"
            )
        )

    # ------------------------------------------------------------
    # Role Update
    # ------------------------------------------------------------

    def test_change_role(self):

        response = self.patch_employee({
            "role": EmploymentRole.MANAGER
        })

        self.employee.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.employee.role,
            EmploymentRole.MANAGER
        )

    def test_role_change_regenerates_employee_code(self):

        old_code = self.employee.employee_code

        response = self.patch_employee({
            "role": EmploymentRole.MANAGER
        })

        self.employee.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertNotEqual(
            old_code,
            self.employee.employee_code
        )

        self.assertTrue(
            self.employee.employee_code.startswith(
                f"{EmploymentRole.MANAGER}{self.department.code}"
            )
        )

    # ------------------------------------------------------------
    # Combined Update
    # ------------------------------------------------------------

    def test_change_department_and_role(self):

        response = self.patch_employee({

            "department": self.new_department.id,

            "role": EmploymentRole.HR

        })

        self.employee.refresh_from_db()

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            self.employee.department,
            self.new_department
        )

        self.assertEqual(
            self.employee.role,
            EmploymentRole.HR
        )

        self.assertTrue(
            self.employee.employee_code.startswith(
                f"HR{self.new_department.code}"
            )
        )