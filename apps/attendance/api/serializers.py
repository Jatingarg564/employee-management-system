from datetime import timedelta

from rest_framework import serializers
from django.utils import timezone

from apps.attendance.models import Attendance, AttendancePause


class AttendancePauseSerializer(serializers.ModelSerializer):
	class Meta:
		model = AttendancePause
		fields = ("id", "started_at", "ended_at", "duration")
		read_only_fields = fields


class AttendanceSerializer(serializers.ModelSerializer):
	employee_id = serializers.IntegerField(read_only=True)
	status = serializers.SerializerMethodField()
	current_work_duration = serializers.SerializerMethodField()
	current_pause_started_at = serializers.SerializerMethodField()
	pauses = AttendancePauseSerializer(many=True, read_only=True)

	class Meta:
		model = Attendance
		fields = (
			"id",
			"employee_id",
			"date",
			"check_in",
			"check_out",
			"work_duration",
			"status",
			"current_work_duration",
			"current_pause_started_at",
			"pauses",
		)
		read_only_fields = fields

	def _pause_records(self, attendance):
		if not hasattr(attendance, "_attendance_pause_records"):
			attendance._attendance_pause_records = list(attendance.pauses.all())
		return attendance._attendance_pause_records

	def _active_pause(self, attendance):
		return next(
			(
				pause
				for pause in self._pause_records(attendance)
				if pause.ended_at is None
			),
			None,
		)

	def get_status(self, attendance):
		if attendance.check_out is not None:
			return "COMPLETED"
		if self._active_pause(attendance) is not None:
			return "PAUSED"
		return "WORKING"

	def get_current_pause_started_at(self, attendance):
		active_pause = self._active_pause(attendance)
		if active_pause is None:
			return None
		return serializers.DateTimeField().to_representation(
			active_pause.started_at,
		)

	def get_current_work_duration(self, attendance):
		if attendance.check_out is not None:
			current_duration = attendance.work_duration
		else:
			active_pause = self._active_pause(attendance)
			elapsed_until = (
				active_pause.started_at
				if active_pause is not None
				else self.context.get("now", timezone.now())
			)
			completed_pause_duration = sum(
				(
					pause.duration
					for pause in self._pause_records(attendance)
					if pause.duration is not None
				),
				timedelta(),
			)
			current_duration = (
				elapsed_until
				- attendance.check_in
				- completed_pause_duration
			)

		if current_duration is None:
			return None
		return serializers.DurationField().to_representation(current_duration)
