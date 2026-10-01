from drf_spectacular.utils import extend_schema
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.attendance.api.serializers import AttendanceSerializer
from apps.attendance.selectors import (
	get_employee_for_user,
	get_today_attendance,
)
from apps.attendance.services import AttendanceService


class CheckInAPIView(APIView):
	permission_classes = [IsAuthenticated]

	@extend_schema(
		tags=["Attendance"],
		summary="Check in",
		request=None,
		responses={201: AttendanceSerializer},
	)
	def post(self, request, *args, **kwargs):
		attendance = AttendanceService.check_in(request.user)
		return Response(
			AttendanceSerializer(
				attendance,
				context={"now": timezone.now()},
			).data,
			status=status.HTTP_201_CREATED,
		)


class PauseAPIView(APIView):
	permission_classes = [IsAuthenticated]

	@extend_schema(
		tags=["Attendance"],
		summary="Pause attendance timer",
		request=None,
		responses={201: AttendanceSerializer},
	)
	def post(self, request, *args, **kwargs):
		pause = AttendanceService.pause(request.user)
		return Response(
			AttendanceSerializer(
				pause.attendance,
				context={"now": timezone.now()},
			).data,
			status=status.HTTP_201_CREATED,
		)


class ResumeAPIView(APIView):
	permission_classes = [IsAuthenticated]

	@extend_schema(
		tags=["Attendance"],
		summary="Resume attendance timer",
		request=None,
		responses={200: AttendanceSerializer},
	)
	def post(self, request, *args, **kwargs):
		attendance = AttendanceService.resume(request.user)
		return Response(
			AttendanceSerializer(
				attendance,
				context={"now": timezone.now()},
			).data,
			status=status.HTTP_200_OK,
		)


class CheckOutAPIView(APIView):
	permission_classes = [IsAuthenticated]

	@extend_schema(
		tags=["Attendance"],
		summary="Check out",
		request=None,
		responses={200: AttendanceSerializer},
	)
	def post(self, request, *args, **kwargs):
		attendance = AttendanceService.check_out(request.user)
		return Response(
			AttendanceSerializer(
				attendance,
				context={"now": timezone.now()},
			).data,
			status=status.HTTP_200_OK,
		)


class TodayAttendanceAPIView(APIView):
	permission_classes = [IsAuthenticated]

	@extend_schema(
		tags=["Attendance"],
		summary="Get current-day attendance",
		responses={200: AttendanceSerializer},
	)
	def get(self, request, *args, **kwargs):
		employee = get_employee_for_user(request.user)
		current_time = timezone.now()
		if employee is None:
			return Response(
				{"detail": "No employee profile is associated with this user."},
				status=status.HTTP_404_NOT_FOUND,
			)

		attendance = get_today_attendance(employee, at=current_time)
		if attendance is None:
			return Response(
				{
					"id": None,
					"employee_id": employee.id,
					"date": timezone.localdate(current_time),
					"check_in": None,
					"check_out": None,
					"work_duration": None,
					"status": "NOT_STARTED",
					"current_work_duration": None,
					"current_pause_started_at": None,
					"pauses": [],
				},
				status=status.HTTP_200_OK,
			)

		return Response(
			AttendanceSerializer(
				attendance,
				context={"now": current_time},
			).data,
			status=status.HTTP_200_OK,
		)
