from django.db import models
from apps.employees.models import Employee


class Attendance(models.Model):
	employee = models.ForeignKey(
		Employee,
		on_delete=models.CASCADE,
		related_name="attendance_records",
	)
	date = models.DateField()
	check_in = models.DateTimeField()
	check_out = models.DateTimeField(
		null=True,
		blank=True,
	)
	work_duration = models.DurationField(
		null=True,
		blank=True,
	)

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=("employee", "date"),
				name="attendance_employee_date_unique",
			),
		]

	def __str__(self):
		return f"{self.employee} - {self.date}"


class AttendancePause(models.Model):
	attendance = models.ForeignKey(
		Attendance,
		on_delete=models.CASCADE,
		related_name="pauses",
	)
	started_at = models.DateTimeField()
	ended_at = models.DateTimeField(
		null=True,
		blank=True,
	)
	duration = models.DurationField(
		null=True,
		blank=True,
	)

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=("attendance",),
				condition=models.Q(ended_at__isnull=True),
				name="attendance_one_active_pause",
			),
		]
