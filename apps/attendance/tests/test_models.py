from datetime import date

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.attendance.models import Attendance, AttendancePause
from apps.employees.tests.base import EmployeeBaseAPITestCase


class AttendanceModelTest(EmployeeBaseAPITestCase):
	def test_attendance_uses_employee_and_allows_unchecked_out_state(self):
		attendance = Attendance.objects.create(
			employee=self.employee,
			date=date(2026, 10, 1),
			check_in=timezone.now(),
		)

		self.assertEqual(attendance.employee, self.employee)
		self.assertIsNone(attendance.check_out)
		self.assertIsNone(attendance.work_duration)
		self.assertEqual(
			self.employee.attendance_records.get(),
			attendance,
		)

	def test_employee_and_date_must_be_unique(self):
		Attendance.objects.create(
			employee=self.employee,
			date=date(2026, 10, 1),
			check_in=timezone.now(),
		)

		with self.assertRaises(IntegrityError):
			with transaction.atomic():
				Attendance.objects.create(
					employee=self.employee,
					date=date(2026, 10, 1),
					check_in=timezone.now(),
				)

	def test_date_and_check_in_are_required(self):
		attendance = Attendance(employee=self.employee)

		with self.assertRaises(ValidationError):
			attendance.full_clean()

	def test_only_one_active_pause_per_attendance_is_allowed(self):
		attendance = Attendance.objects.create(
			employee=self.employee,
			date=date(2026, 10, 1),
			check_in=timezone.now(),
		)
		AttendancePause.objects.create(
			attendance=attendance,
			started_at=timezone.now(),
		)

		with self.assertRaises(IntegrityError):
			with transaction.atomic():
				AttendancePause.objects.create(
					attendance=attendance,
					started_at=timezone.now(),
				)
