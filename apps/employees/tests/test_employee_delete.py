from rest_framework import status

from apps.employees.choices import EmployeeStatus
from apps.employees.models import Employee
from apps.employees.tests.base import EmployeeBaseAPITestCase


class EmployeeDeleteAPITest(EmployeeBaseAPITestCase):

    def setUp(self):
        self.authenticate()

    def delete_employee(self):
        return self.client.delete(
            self.employee_detail_url()
        )

    # ------------------------------------------------------------
    # Soft Delete
    # ------------------------------------------------------------

    def test_soft_delete_employee(self):

        response = self.delete_employee()

        self.employee.refresh_from_db()
        self.employee.user.refresh_from_db()

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertEqual(
            self.employee.status,
            EmployeeStatus.INACTIVE
        )

        self.assertFalse(
            self.employee.user.is_active
        )

    # ------------------------------------------------------------
    # Employee Still Exists
    # ------------------------------------------------------------

    def test_employee_not_removed_from_database(self):

        employee_id = self.employee.id

        self.delete_employee()

        self.assertTrue(
            Employee.objects.filter(
                id=employee_id
            ).exists()
        )

    # ------------------------------------------------------------
    # User Record Still Exists
    # ------------------------------------------------------------

    def test_user_not_removed_from_database(self):

        user_id = self.employee.user.id

        self.delete_employee()

        self.assertTrue(
            self.employee.user.__class__.objects.filter(
                id=user_id
            ).exists()
        )

    # ------------------------------------------------------------
    # User Account Disabled
    # ------------------------------------------------------------

    def test_user_account_is_disabled(self):

        self.delete_employee()

        self.employee.user.refresh_from_db()

        self.assertFalse(
            self.employee.user.is_active
        )

    # ------------------------------------------------------------
    # Status Updated
    # ------------------------------------------------------------

    def test_employee_status_becomes_inactive(self):

        self.delete_employee()

        self.employee.refresh_from_db()

        self.assertEqual(
            self.employee.status,
            EmployeeStatus.INACTIVE
        )

    # ------------------------------------------------------------
    # Idempotent Delete
    # ------------------------------------------------------------

    def test_delete_inactive_employee(self):

        self.delete_employee()

        response = self.delete_employee()

        self.assertIn(
            response.status_code,
            [
                status.HTTP_204_NO_CONTENT,
                status.HTTP_400_BAD_REQUEST,
            ]
        )

    # ------------------------------------------------------------
    # Invalid Employee
    # ------------------------------------------------------------

    def test_delete_invalid_employee(self):

        response = self.client.delete(
            "/api/employees/999999/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    # ------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------

    def test_delete_requires_authentication(self):

        self.client.force_authenticate(None)

        response = self.delete_employee()

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ]
        )

    # ------------------------------------------------------------
    # Retrieve After Delete
    # ------------------------------------------------------------

    def test_retrieve_after_soft_delete(self):

        self.delete_employee()

        response = self.client.get(
            self.employee_detail_url()
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data["status"],
            EmployeeStatus.INACTIVE
        )

    # ------------------------------------------------------------
    # List After Delete
    # ------------------------------------------------------------

    def test_soft_deleted_employee_in_list(self):

        self.delete_employee()

        response = self.client.get(
            self.employee_list_url()
        )

        employee = next(
            emp
            for emp in response.data
            if emp["id"] == self.employee.id
        )

        self.assertEqual(
            employee["status"],
            EmployeeStatus.INACTIVE
        )

    # ------------------------------------------------------------
    # Employee Count
    # ------------------------------------------------------------

    def test_employee_count_unchanged(self):

        before = Employee.objects.count()

        self.delete_employee()

        after = Employee.objects.count()

        self.assertEqual(
            before,
            after
        )