from datetime import datetime, timedelta
from unittest.mock import patch

from django.utils import timezone
from rest_framework import status

from apps.attendance.models import Attendance
from apps.employees.tests.base import EmployeeBaseAPITestCase


class AttendanceAPITest(EmployeeBaseAPITestCase):
	check_in_url = "/api/attendance/check-in/"
	pause_url = "/api/attendance/pause/"
	resume_url = "/api/attendance/resume/"
	check_out_url = "/api/attendance/check-out/"
	today_url = "/api/attendance/today/"

	def setUp(self):
		self.client.force_authenticate(user=self.employee_user)
		self.check_in_time = timezone.make_aware(
			datetime(2026, 10, 1, 9, 0),
		)

	def test_check_in_ignores_client_authoritative_values(self):
		with patch("apps.attendance.services.timezone.now", return_value=self.check_in_time):
			response = self.client.post(
				self.check_in_url,
				{
					"employee_id": self.manager.id,
					"date": "2000-01-01",
					"check_in": "2000-01-01T00:00:00Z",
				},
				format="json",
			)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(response.data["employee_id"], self.employee.id)
		self.assertEqual(response.data["date"], "2026-10-01")
		self.assertEqual(response.data["check_in"], "2026-10-01T09:00:00+05:30")
		self.assertIsNone(response.data["check_out"])
		self.assertIsNone(response.data["work_duration"])

	def test_check_out_response_contains_same_record_and_duration(self):
		attendance = Attendance.objects.create(
			employee=self.employee,
			date=timezone.localdate(self.check_in_time),
			check_in=self.check_in_time,
		)
		check_out_time = self.check_in_time + timedelta(hours=8)

		with patch("apps.attendance.services.timezone.now", return_value=check_out_time):
			response = self.client.post(
				self.check_out_url,
				{
					"employee_id": self.manager.id,
					"date": "2000-01-01",
					"check_out": "2000-01-01T00:00:00Z",
					"work_duration": "99:00:00",
				},
				format="json",
			)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data["id"], attendance.id)
		self.assertEqual(response.data["employee_id"], self.employee.id)
		self.assertEqual(response.data["check_out"], "2026-10-01T17:00:00+05:30")
		self.assertEqual(response.data["work_duration"], "08:00:00")
		self.assertEqual(Attendance.objects.count(), 1)

	def test_today_returns_record_or_standard_not_found_error(self):
		response = self.client.get(self.today_url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data["status"], "NOT_STARTED")
		self.assertIsNone(response.data["id"])

		with patch("apps.attendance.services.timezone.now", return_value=self.check_in_time):
			created = self.client.post(self.check_in_url, {}, format="json")

		with patch(
			"apps.attendance.api.views.timezone.now",
			return_value=self.check_in_time + timedelta(minutes=10),
		):
			response = self.client.get(self.today_url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data["id"], created.data["id"])
		self.assertEqual(response.data["status"], "WORKING")
		self.assertEqual(response.data["current_work_duration"], "00:10:00")

	def test_pause_and_resume_return_current_state(self):
		with patch("apps.attendance.services.timezone.now", return_value=self.check_in_time):
			self.client.post(self.check_in_url, {}, format="json")

		pause_time = self.check_in_time + timedelta(hours=2)
		resume_time = pause_time + timedelta(minutes=30)
		with patch("apps.attendance.services.timezone.now", return_value=pause_time):
			paused = self.client.post(self.pause_url, {}, format="json")
		self.assertEqual(paused.status_code, status.HTTP_201_CREATED)
		self.assertEqual(paused.data["status"], "PAUSED")
		self.assertEqual(paused.data["current_pause_started_at"], "2026-10-01T11:00:00+05:30")
		self.assertEqual(paused.data["current_work_duration"], "02:00:00")

		with patch("apps.attendance.services.timezone.now", return_value=resume_time):
			resumed = self.client.post(self.resume_url, {}, format="json")
		self.assertEqual(resumed.status_code, status.HTTP_200_OK)
		self.assertEqual(resumed.data["status"], "WORKING")
		self.assertIsNone(resumed.data["current_pause_started_at"])
		self.assertEqual(resumed.data["current_work_duration"], "02:00:00")
		self.assertEqual(resumed.data["pauses"][0]["duration"], "00:30:00")

	def test_duplicate_check_in_uses_standard_error_shape(self):
		with patch("apps.attendance.services.timezone.now", return_value=self.check_in_time):
			self.client.post(self.check_in_url, {}, format="json")
			response = self.client.post(self.check_in_url, {}, format="json")

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(
			response.data["detail"],
			"You have already checked in today.",
		)

	def test_checkout_without_attendance_uses_standard_error_shape(self):
		with patch("apps.attendance.services.timezone.now", return_value=self.check_in_time):
			response = self.client.post(self.check_out_url, {}, format="json")

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
		self.assertEqual(
			response.data["detail"],
			"No attendance record exists for today.",
		)

	def test_duplicate_check_out_uses_standard_error_shape(self):
		Attendance.objects.create(
			employee=self.employee,
			date=timezone.localdate(self.check_in_time),
			check_in=self.check_in_time,
			check_out=self.check_in_time + timedelta(hours=8),
			work_duration=timedelta(hours=8),
		)

		with patch(
			"apps.attendance.services.timezone.now",
			return_value=self.check_in_time + timedelta(hours=9),
		):
			response = self.client.post(self.check_out_url, {}, format="json")

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(
			response.data["detail"],
			"You have already checked out today.",
		)

	def test_checkin_and_checkout_require_authentication(self):
		self.client.force_authenticate(user=None)

		check_in_response = self.client.post(self.check_in_url, {}, format="json")
		pause_response = self.client.post(self.pause_url, {}, format="json")
		resume_response = self.client.post(self.resume_url, {}, format="json")
		check_out_response = self.client.post(self.check_out_url, {}, format="json")
		today_response = self.client.get(self.today_url)

		self.assertEqual(check_in_response.status_code, status.HTTP_401_UNAUTHORIZED)
		self.assertEqual(pause_response.status_code, status.HTTP_401_UNAUTHORIZED)
		self.assertEqual(resume_response.status_code, status.HTTP_401_UNAUTHORIZED)
		self.assertEqual(check_out_response.status_code, status.HTTP_401_UNAUTHORIZED)
		self.assertEqual(today_response.status_code, status.HTTP_401_UNAUTHORIZED)
