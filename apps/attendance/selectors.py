from django.utils import timezone

from apps.attendance.models import Attendance
from apps.employees.models import Employee


def get_employee_for_user(user):
	return Employee.objects.filter(user=user).first()


def get_attendance_for_employee_and_date(
	employee,
	attendance_date,
	lock=False,
):
	attendance = Attendance.objects.filter(
		employee=employee,
		date=attendance_date,
	)

	if lock:
		attendance = attendance.select_for_update()

	attendance = attendance.prefetch_related("pauses")
	return attendance.first()


def get_today_attendance(employee, at=None, lock=False):
	current_time = at or timezone.now()
	return get_attendance_for_employee_and_date(
		employee=employee,
		attendance_date=timezone.localdate(current_time),
		lock=lock,
	)


def get_active_pause(attendance, lock=False):
	pauses = attendance.pauses.filter(ended_at__isnull=True)
	if lock:
		pauses = pauses.select_for_update()
	return pauses.first()
