from datetime import date, datetime

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.attendance.models import Attendance
from apps.employees.tests.base import EmployeeBaseAPITestCase
from apps.attendance.validators import validate_check_out_allowed


class AttendanceValidatorTest(EmployeeBaseAPITestCase):
	def test_checkout_without_checkin_is_rejected(self):
		attendance = Attendance(
			employee=self.employee,
			date=timezone.localdate(),
			check_in=None,
		)

		with self.assertRaises(ValidationError):
			validate_check_out_allowed(attendance, timezone.now())

	def test_checkout_before_checkin_is_rejected(self):
		check_in = timezone.make_aware(datetime(2026, 10, 1, 12, 0))
		check_out = timezone.make_aware(datetime(2026, 10, 1, 11, 0))
		attendance = Attendance(
			employee=self.employee,
			date=date(2026, 10, 1),
			check_in=check_in,
		)

		with self.assertRaises(ValidationError):
			validate_check_out_allowed(attendance, check_out)
