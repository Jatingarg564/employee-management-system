from datetime import datetime, timedelta
from unittest.mock import patch

from django.db import IntegrityError
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError

from apps.attendance.models import Attendance, AttendancePause
from apps.attendance.services import AttendanceService
from apps.employees.tests.base import EmployeeBaseAPITestCase


class AttendanceServiceTest(EmployeeBaseAPITestCase):
	def setUp(self):
		self.check_in_time = timezone.make_aware(
			datetime(2026, 10, 1, 9, 0),
		)
		self.pause_time = timezone.make_aware(
			datetime(2026, 10, 1, 12, 0),
		)

	@patch("apps.attendance.services.timezone.now")
	def test_check_in_creates_backend_timestamped_record(self, mock_now):
		mock_now.return_value = self.check_in_time

		attendance = AttendanceService.check_in(self.employee_user)

		self.assertEqual(Attendance.objects.count(), 1)
		self.assertEqual(attendance.employee, self.employee)
		self.assertEqual(attendance.date, timezone.localdate(self.check_in_time))
		self.assertEqual(attendance.check_in, self.check_in_time)
		self.assertIsNone(attendance.check_out)
		self.assertIsNone(attendance.work_duration)

	@patch("apps.attendance.services.timezone.now")
	def test_duplicate_check_in_does_not_modify_existing_record(self, mock_now):
		mock_now.return_value = self.check_in_time
		existing = Attendance.objects.create(
			employee=self.employee,
			date=timezone.localdate(self.check_in_time),
			check_in=self.check_in_time - timedelta(hours=1),
			check_out=self.check_in_time,
			work_duration=timedelta(hours=1),
		)

		with self.assertRaises(ValidationError):
			AttendanceService.check_in(self.employee_user)

		existing.refresh_from_db()
		self.assertEqual(Attendance.objects.count(), 1)
		self.assertEqual(existing.check_in, self.check_in_time - timedelta(hours=1))
		self.assertEqual(existing.check_out, self.check_in_time)
		self.assertEqual(existing.work_duration, timedelta(hours=1))

	@patch("apps.attendance.services.Attendance.objects.create")
	@patch("apps.attendance.services.timezone.now")
	def test_unique_constraint_race_is_reported_as_duplicate(
		self,
		mock_now,
		mock_create,
	):
		mock_now.return_value = self.check_in_time
		existing = Attendance(
			employee=self.employee,
			date=timezone.localdate(self.check_in_time),
			check_in=self.check_in_time,
		)
		existing.save()
		mock_create.side_effect = IntegrityError("duplicate employee/date")

		with patch(
			"apps.attendance.services.get_attendance_for_employee_and_date",
			side_effect=(None, existing),
		):
			with self.assertRaises(ValidationError):
				AttendanceService.check_in(self.employee_user)

		self.assertEqual(Attendance.objects.count(), 1)

	@patch("apps.attendance.services.timezone.now")
	def test_check_out_updates_same_record_and_calculates_duration(self, mock_now):
		check_out_time = self.check_in_time + timedelta(hours=8, minutes=30)
		mock_now.return_value = self.check_in_time
		attendance = AttendanceService.check_in(self.employee_user)
		attendance_id = attendance.id
		mock_now.return_value = check_out_time

		checked_out = AttendanceService.check_out(self.employee_user)

		self.assertEqual(checked_out.id, attendance_id)
		self.assertEqual(Attendance.objects.count(), 1)
		self.assertEqual(checked_out.check_out, check_out_time)
		self.assertEqual(checked_out.work_duration, timedelta(hours=8, minutes=30))

	@patch("apps.attendance.services.timezone.now")
	def test_check_out_without_check_in_is_not_found(self, mock_now):
		mock_now.return_value = self.check_in_time

		with self.assertRaises(NotFound):
			AttendanceService.check_out(self.employee_user)

	@patch("apps.attendance.services.timezone.now")
	def test_duplicate_check_out_does_not_overwrite_previous_checkout(
		self,
		mock_now,
	):
		previous_checkout = self.check_in_time + timedelta(hours=8)
		attendance = Attendance.objects.create(
			employee=self.employee,
			date=timezone.localdate(self.check_in_time),
			check_in=self.check_in_time,
			check_out=previous_checkout,
			work_duration=timedelta(hours=8),
		)
		mock_now.return_value = self.check_in_time + timedelta(hours=9)

		with self.assertRaises(ValidationError):
			AttendanceService.check_out(self.employee_user)

		attendance.refresh_from_db()
		self.assertEqual(attendance.check_out, previous_checkout)
		self.assertEqual(attendance.work_duration, timedelta(hours=8))

	@patch("apps.attendance.services.timezone.now")
	def test_pause_requires_checkin_and_rejects_after_checkout(self, mock_now):
		mock_now.return_value = self.check_in_time
		with self.assertRaises(NotFound):
			AttendanceService.pause(self.employee_user)

		attendance = Attendance.objects.create(
			employee=self.employee,
			date=timezone.localdate(self.check_in_time),
			check_in=self.check_in_time,
			check_out=self.check_in_time + timedelta(hours=8),
			work_duration=timedelta(hours=8),
		)
		mock_now.return_value = attendance.check_out + timedelta(minutes=1)
		with self.assertRaises(ValidationError):
			AttendanceService.pause(self.employee_user)

	@patch("apps.attendance.services.timezone.now")
	def test_pause_timestamp_is_backend_generated_and_duplicate_is_rejected(
		self,
		mock_now,
	):
		mock_now.return_value = self.check_in_time
		AttendanceService.check_in(self.employee_user)
		mock_now.return_value = self.pause_time

		pause = AttendanceService.pause(self.employee_user)

		self.assertEqual(pause.started_at, self.pause_time)
		self.assertIsNone(pause.ended_at)
		self.assertIsNone(pause.duration)
		with self.assertRaises(ValidationError):
			AttendanceService.pause(self.employee_user)

	@patch("apps.attendance.services.timezone.now")
	def test_resume_closes_pause_and_calculates_duration(self, mock_now):
		resumed_at = self.pause_time + timedelta(minutes=30)
		mock_now.return_value = self.check_in_time
		AttendanceService.check_in(self.employee_user)
		mock_now.return_value = self.pause_time
		pause = AttendanceService.pause(self.employee_user)
		mock_now.return_value = resumed_at

		attendance = AttendanceService.resume(self.employee_user)

		pause.refresh_from_db()
		self.assertEqual(attendance.id, pause.attendance_id)
		self.assertEqual(pause.ended_at, resumed_at)
		self.assertEqual(pause.duration, timedelta(minutes=30))
		with self.assertRaises(ValidationError):
			AttendanceService.resume(self.employee_user)

	@patch("apps.attendance.services.timezone.now")
	def test_multiple_pause_intervals_are_preserved_and_subtracted(self, mock_now):
		mock_now.return_value = self.check_in_time
		AttendanceService.check_in(self.employee_user)
		first_pause_end = self.pause_time + timedelta(minutes=30)
		second_pause_start = first_pause_end + timedelta(hours=1)
		second_pause_end = second_pause_start + timedelta(minutes=15)
		check_out_time = self.check_in_time + timedelta(hours=8)

		mock_now.return_value = self.pause_time
		first_pause = AttendanceService.pause(self.employee_user)
		mock_now.return_value = first_pause_end
		AttendanceService.resume(self.employee_user)
		mock_now.return_value = second_pause_start
		second_pause = AttendanceService.pause(self.employee_user)
		mock_now.return_value = second_pause_end
		AttendanceService.resume(self.employee_user)
		mock_now.return_value = check_out_time
		attendance = AttendanceService.check_out(self.employee_user)

		first_pause.refresh_from_db()
		second_pause.refresh_from_db()
		self.assertEqual(AttendancePause.objects.filter(attendance=attendance).count(), 2)
		self.assertEqual(first_pause.duration, timedelta(minutes=30))
		self.assertEqual(second_pause.duration, timedelta(minutes=15))
		self.assertEqual(attendance.work_duration, timedelta(hours=7, minutes=15))

	@patch("apps.attendance.services.timezone.now")
	def test_checkout_closes_active_pause_and_excludes_its_duration(self, mock_now):
		pause_checkout_time = self.pause_time + timedelta(hours=2)
		mock_now.return_value = self.check_in_time
		AttendanceService.check_in(self.employee_user)
		mock_now.return_value = self.pause_time
		pause = AttendanceService.pause(self.employee_user)
		mock_now.return_value = pause_checkout_time

		attendance = AttendanceService.check_out(self.employee_user)

		pause.refresh_from_db()
		self.assertEqual(pause.ended_at, pause_checkout_time)
		self.assertEqual(pause.duration, timedelta(hours=2))
		self.assertEqual(attendance.check_out, pause_checkout_time)
		self.assertEqual(attendance.work_duration, timedelta(hours=3))
		self.assertEqual(attendance.id, pause.attendance_id)
