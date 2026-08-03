from datetime import timedelta

from django.utils import timezone
from rest_framework import status

from apps.employees.choices import EmployeeStatus
from apps.employees.models import Employee
from apps.employees.tests.base import EmployeeBaseAPITestCase


class EmployeeStatusAPITest(EmployeeBaseAPITestCase):

    def setUp(self):
        self.authenticate()

    def patch_status(self, new_status):
        return self.client.patch(
            self.employee_status_url(),
            {"status": new_status},
            format="json"
        )

    # ------------------------------------------------------------------
    # ACTIVE
    # ------------------------------------------------------------------

    def test_active_to_inactive(self):

        response = self.patch_status(EmployeeStatus.INACTIVE)

        self.employee.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.employee.status, EmployeeStatus.INACTIVE)
        self.assertFalse(self.employee.user.is_active)

    def test_active_to_on_leave(self):

        response = self.patch_status(EmployeeStatus.ON_LEAVE)

        self.employee.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.employee.status, EmployeeStatus.ON_LEAVE)
        self.assertTrue(self.employee.user.is_active)

    def test_active_to_resigned(self):

        response = self.patch_status(EmployeeStatus.RESIGNED)

        self.employee.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.employee.status, EmployeeStatus.RESIGNED)
        self.assertFalse(self.employee.user.is_active)
        self.assertIsNotNone(self.employee.resignation_date)

    def test_active_to_terminated(self):

        response = self.patch_status(EmployeeStatus.TERMINATED)

        self.employee.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.employee.status, EmployeeStatus.TERMINATED)
        self.assertFalse(self.employee.user.is_active)
        self.assertIsNotNone(self.employee.termination_date)

    # ------------------------------------------------------------------
    # INACTIVE
    # ------------------------------------------------------------------

    def test_inactive_to_active(self):

        self.employee.status = EmployeeStatus.INACTIVE
        self.employee.save()

        response = self.patch_status(EmployeeStatus.ACTIVE)

        self.employee.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.employee.status, EmployeeStatus.ACTIVE)
        self.assertTrue(self.employee.user.is_active)

    def test_inactive_to_on_leave(self):

        self.employee.status = EmployeeStatus.INACTIVE
        self.employee.save()

        response = self.patch_status(EmployeeStatus.ON_LEAVE)

        self.employee.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.employee.status, EmployeeStatus.ON_LEAVE)

    def test_inactive_to_resigned(self):

        self.employee.status = EmployeeStatus.INACTIVE
        self.employee.save()

        response = self.patch_status(EmployeeStatus.RESIGNED)

        self.employee.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(self.employee.resignation_date)

    def test_inactive_to_terminated(self):

        self.employee.status = EmployeeStatus.INACTIVE
        self.employee.save()

        response = self.patch_status(EmployeeStatus.TERMINATED)

        self.employee.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(self.employee.termination_date)

    # ------------------------------------------------------------------
    # ON LEAVE
    # ------------------------------------------------------------------

    def test_on_leave_to_active(self):

        self.employee.status = EmployeeStatus.ON_LEAVE
        self.employee.save()

        response = self.patch_status(EmployeeStatus.ACTIVE)

        self.employee.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.employee.status, EmployeeStatus.ACTIVE)

    def test_on_leave_to_inactive(self):

        self.employee.status = EmployeeStatus.ON_LEAVE
        self.employee.save()

        response = self.patch_status(EmployeeStatus.INACTIVE)

        self.employee.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_on_leave_to_resigned(self):

        self.employee.status = EmployeeStatus.ON_LEAVE
        self.employee.save()

        response = self.patch_status(EmployeeStatus.RESIGNED)

        self.employee.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_on_leave_to_terminated(self):

        self.employee.status = EmployeeStatus.ON_LEAVE
        self.employee.save()

        response = self.patch_status(EmployeeStatus.TERMINATED)

        self.employee.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ------------------------------------------------------------------
    # RESIGNED
    # ------------------------------------------------------------------

    def test_resigned_to_active_within_30_days(self):

        self.employee.status = EmployeeStatus.RESIGNED
        self.employee.resignation_date = (
            timezone.now().date() - timedelta(days=15)
        )
        self.employee.save()

        response = self.patch_status(EmployeeStatus.ACTIVE)

        self.employee.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.employee.status, EmployeeStatus.ACTIVE)

    def test_resigned_to_active_after_30_days_should_fail(self):

        self.employee.status = EmployeeStatus.RESIGNED
        self.employee.resignation_date = (
            timezone.now().date() - timedelta(days=40)
        )
        self.employee.save()

        response = self.patch_status(EmployeeStatus.ACTIVE)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_resigned_without_date_should_fail(self):

        self.employee.status = EmployeeStatus.RESIGNED
        self.employee.resignation_date = None
        self.employee.save()

        response = self.patch_status(EmployeeStatus.ACTIVE)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------
    # TERMINATED
    # ------------------------------------------------------------------

    def test_terminated_to_active_should_fail(self):

        self.employee.status = EmployeeStatus.TERMINATED
        self.employee.save()

        response = self.patch_status(EmployeeStatus.ACTIVE)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_terminated_to_inactive_should_fail(self):

        self.employee.status = EmployeeStatus.TERMINATED
        self.employee.save()

        response = self.patch_status(EmployeeStatus.INACTIVE)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_terminated_to_on_leave_should_fail(self):

        self.employee.status = EmployeeStatus.TERMINATED
        self.employee.save()

        response = self.patch_status(EmployeeStatus.ON_LEAVE)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_terminated_to_resigned_should_fail(self):

        self.employee.status = EmployeeStatus.TERMINATED
        self.employee.save()

        response = self.patch_status(EmployeeStatus.RESIGNED)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------
    # Regression Tests
    # ------------------------------------------------------------------

    def test_reactivation_should_not_clear_resignation_date(self):

        resignation_date = timezone.now().date()

        self.employee.status = EmployeeStatus.RESIGNED
        self.employee.resignation_date = resignation_date
        self.employee.save()

        response = self.patch_status(EmployeeStatus.ACTIVE)

        self.employee.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.employee.resignation_date,
            resignation_date
        )

    def test_resignation_date_only_set_once(self):

        self.employee.status = EmployeeStatus.RESIGNED
        self.employee.resignation_date = timezone.now().date()
        self.employee.save()

        first_date = self.employee.resignation_date

        self.patch_status(EmployeeStatus.ACTIVE)
        self.patch_status(EmployeeStatus.RESIGNED)

        self.employee.refresh_from_db()

        self.assertEqual(
            self.employee.resignation_date,
            first_date
        )

    def test_termination_date_only_set_once(self):
        self.patch_status(EmployeeStatus.TERMINATED)

        self.employee.refresh_from_db()
        first_date = self.employee.termination_date

        # Try terminating again (or another operation that shouldn't overwrite the date)
        self.patch_status(EmployeeStatus.TERMINATED)

        self.employee.refresh_from_db()

        self.assertEqual(self.employee.termination_date, first_date)