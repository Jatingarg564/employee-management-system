from rest_framework.exceptions import ValidationError


def validate_check_in_allowed(attendance):
	if attendance is not None:
		raise ValidationError(
			{"detail": "You have already checked in today."},
		)


def validate_check_out_allowed(attendance, check_out):
	if attendance.check_in is None:
		raise ValidationError(
			{"detail": "Attendance has no check-in timestamp."},
		)

	if attendance.check_out is not None:
		raise ValidationError(
			{"detail": "You have already checked out today."},
		)

	if check_out < attendance.check_in:
		raise ValidationError(
			{"detail": "Check-out cannot be earlier than check-in."},
		)


def validate_pause_allowed(attendance, active_pause, paused_at):
	if attendance.check_in is None:
		raise ValidationError(
			{"detail": "Attendance has no check-in timestamp."},
		)

	if attendance.check_out is not None:
		raise ValidationError(
			{"detail": "Cannot pause after checkout."},
		)

	if paused_at < attendance.check_in:
		raise ValidationError(
			{"detail": "Pause cannot start before check-in."},
		)

	if active_pause is not None:
		raise ValidationError(
			{"detail": "Attendance is already paused."},
		)


def validate_resume_allowed(active_pause, resumed_at):
	if active_pause is None:
		raise ValidationError(
			{"detail": "No active pause exists for today."},
		)

	if resumed_at < active_pause.started_at:
		raise ValidationError(
			{"detail": "Resume cannot occur before the pause starts."},
		)
