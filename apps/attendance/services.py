from datetime import timedelta

from django.db import IntegrityError, transaction
from django.db.models import Sum
from django.utils import timezone
from rest_framework.exceptions import NotFound

from apps.attendance.models import Attendance, AttendancePause
from apps.attendance.selectors import (
	get_attendance_for_employee_and_date,
	get_active_pause,
	get_employee_for_user,
)
from apps.attendance.validators import (
	validate_check_in_allowed,
	validate_check_out_allowed,
	validate_pause_allowed,
	validate_resume_allowed,
)


class AttendanceService:
	@staticmethod
	@transaction.atomic
	def check_in(user):
		employee = get_employee_for_user(user)
		if employee is None:
			raise NotFound("No employee profile is associated with this user.")

		check_in_time = timezone.now()
		attendance_date = timezone.localdate(check_in_time)
		existing_attendance = get_attendance_for_employee_and_date(
			employee,
			attendance_date,
		)
		validate_check_in_allowed(existing_attendance)

		try:
			with transaction.atomic():
				return Attendance.objects.create(
					employee=employee,
					date=attendance_date,
					check_in=check_in_time,
				)
		except IntegrityError:
			conflicting_attendance = get_attendance_for_employee_and_date(
				employee,
				attendance_date,
			)
			if conflicting_attendance is not None:
				validate_check_in_allowed(conflicting_attendance)
			raise

	@staticmethod
	@transaction.atomic
	def check_out(user):
		employee = get_employee_for_user(user)
		if employee is None:
			raise NotFound("No employee profile is associated with this user.")

		check_out_time = timezone.now()
		attendance_date = timezone.localdate(check_out_time)
		attendance = get_attendance_for_employee_and_date(
			employee,
			attendance_date,
			lock=True,
		)

		if attendance is None:
			raise NotFound("No attendance record exists for today.")

		validate_check_out_allowed(attendance, check_out_time)
		active_pause = get_active_pause(attendance, lock=True)
		if active_pause is not None:
			validate_resume_allowed(active_pause, check_out_time)
			active_pause.ended_at = check_out_time
			active_pause.duration = check_out_time - active_pause.started_at
			active_pause.save(update_fields=("ended_at", "duration"))
			attendance._prefetched_objects_cache.pop("pauses", None)

		attendance.check_out = check_out_time
		attendance.work_duration = calculate_work_duration(
			attendance,
			check_out_time,
		)
		attendance.save(
			update_fields=("check_out", "work_duration"),
		)
		return attendance

	@staticmethod
	@transaction.atomic
	def pause(user):
		paused_at = timezone.now()
		attendance = _get_today_attendance(user, paused_at, lock=True)
		active_pause = get_active_pause(attendance, lock=True)
		validate_pause_allowed(attendance, active_pause, paused_at)

		try:
			with transaction.atomic():
				pause = AttendancePause.objects.create(
					attendance=attendance,
					started_at=paused_at,
				)
				attendance._prefetched_objects_cache.pop("pauses", None)
				return pause
		except IntegrityError:
			conflicting_pause = get_active_pause(attendance)
			if conflicting_pause is not None:
				validate_pause_allowed(
					attendance,
					conflicting_pause,
					paused_at,
				)
			raise

	@staticmethod
	@transaction.atomic
	def resume(user):
		resumed_at = timezone.now()
		attendance = _get_today_attendance(user, resumed_at, lock=True)
		active_pause = get_active_pause(attendance, lock=True)
		validate_resume_allowed(active_pause, resumed_at)

		active_pause.ended_at = resumed_at
		active_pause.duration = resumed_at - active_pause.started_at
		active_pause.save(update_fields=("ended_at", "duration"))
		attendance._prefetched_objects_cache.pop("pauses", None)
		return attendance


def _get_today_attendance(user, at, lock=False):
	employee = get_employee_for_user(user)
	if employee is None:
		raise NotFound("No employee profile is associated with this user.")

	attendance = get_attendance_for_employee_and_date(
		employee,
		timezone.localdate(at),
		lock=lock,
	)
	if attendance is None:
		raise NotFound("No attendance record exists for today.")
	return attendance


def calculate_work_duration(attendance, ended_at):
	paused_duration = (
		AttendancePause.objects.filter(
			attendance=attendance,
		).aggregate(total=Sum("duration"))["total"]
		or timedelta()
	)
	return ended_at - attendance.check_in - paused_duration
